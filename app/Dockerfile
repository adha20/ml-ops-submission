FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir tensorflow fastapi uvicorn prometheus-client numpy pydantic

COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_PATH=/app/model_store/churn_model.joblib

CMD ["python", "app/main.py"]
