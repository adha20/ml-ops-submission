FROM python:3.9-slim

WORKDIR /app

RUN pip install "tensorflow==2.10.0" "fastapi" "uvicorn" "pydantic" "prometheus-client" "numpy<2.0.0"

COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_PATH=/app/model_store/churn_model.joblib

CMD ["python", "app/main.py"]
