FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

ENV PORT=8080
ENV MODEL_PATH=/app/model_store/churn_model.joblib

CMD ["python", "app/main.py"]
