FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create model_store directory and copy app
COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_STORE_DIR=/app/app/model_store

CMD ["python", "app/main.py"]
