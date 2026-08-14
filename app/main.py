import os
import base64
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel

MODEL_STORE_DIR = os.environ.get('MODEL_STORE_DIR', os.path.join(os.path.dirname(__file__), 'model_store'))

app = FastAPI(title='Customer Churn Prediction API')
REQUEST_COUNT = Counter('customer_churn_requests_total', 'Total prediction requests')
REQUEST_LATENCY = Histogram('customer_churn_request_latency_seconds', 'Prediction latency seconds')

class CustomerInput(BaseModel):
    customer_age: int
    gender: str
    contract_type: str
    monthly_charges: float
    tenure: int
    support_calls: int
    total_usage: int
    satisfaction_score: int

def get_latest_model_path():
    if not os.path.exists(MODEL_STORE_DIR):
        return None
    versions = [d for d in os.listdir(MODEL_STORE_DIR) if os.path.isdir(os.path.join(MODEL_STORE_DIR, d))]
    if not versions:
        return None
    latest_version = sorted(versions, key=int)[-1]
    return os.path.join(MODEL_STORE_DIR, latest_version)

model = None
predict_fn = None

def _float_feature(value):
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value.encode('utf-8')]))

@app.get('/')
def root():
    return {'message': 'Customer churn prediction service is running.'}

@app.get('/metrics')
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post('/predict')
def predict(item: CustomerInput):
    global model
    global predict_fn
    if not predict_fn:
        try:
            latest_path = get_latest_model_path()
            if not latest_path:
                raise HTTPException(status_code=500, detail="Model not found in model_store.")
            model = tf.saved_model.load(latest_path)
            predict_fn = model.signatures['serving_default']
        except Exception as e:
            return {"error": str(e), "type": str(type(e)), "path": latest_path}
        
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        example = tf.train.Example(features=tf.train.Features(feature={
            'customer_age': _int64_feature(item.customer_age),
            'gender': _bytes_feature(item.gender),
            'contract_type': _bytes_feature(item.contract_type),
            'monthly_charges': _float_feature(item.monthly_charges),
            'tenure': _int64_feature(item.tenure),
            'support_calls': _int64_feature(item.support_calls),
            'total_usage': _int64_feature(item.total_usage),
            'satisfaction_score': _int64_feature(item.satisfaction_score),
        }))
        
        serialized_example = example.SerializeToString()
        tensor = tf.constant([serialized_example])
        
        prediction_result = predict_fn(examples=tensor)
        probability = float(prediction_result['output_0'].numpy()[0][0])
        prediction_class = int(probability >= 0.5)
        
        return {
            'prediction': prediction_class,
            'probability': probability,
            'label': 'churn' if prediction_class == 1 else 'no_churn'
        }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT', '8080')))
