FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir tensorflow fastapi uvicorn prometheus-client numpy pydantic

# Create model_store directory and copy app
COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_STORE_DIR=/app/app/model_store

CMD ["python", "app/main.py"]
