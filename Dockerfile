FROM tensorflow/serving:latest

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model
ENV MONITORING_CONFIG="/model_config/prometheus.config"

ENV PORT=8501
EXPOSE 8501

CMD ["--monitoring_config_file=/model_config/prometheus.config"]
