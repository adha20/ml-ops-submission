FROM python:3.9-slim

WORKDIR /app

RUN pip install "tensorflow==2.10.0" "fastapi" "uvicorn" "pydantic" "prometheus-client" numpy

# Create model_store directory and copy app
COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_STORE_DIR=/app/app/model_store

CMD ["python", "app/main.py"]
