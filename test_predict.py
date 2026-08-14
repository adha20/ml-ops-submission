import os
import tensorflow as tf

# Set MODEL_STORE_DIR to local path
os.environ['MODEL_STORE_DIR'] = os.path.abspath('app/model_store')

from app.main import get_latest_model_path, CustomerInput, predict, app
from fastapi.testclient import TestClient

client = TestClient(app)

payload = {
    'customer_age': 35,
    'gender': 'Male',
    'contract_type': 'Month-to-Month',
    'monthly_charges': 72.5,
    'tenure': 12,
    'support_calls': 4,
    'total_usage': 210,
    'satisfaction_score': 2,
}

response = client.post('/predict', json=payload)
print(response.status_code)
print(response.text)
