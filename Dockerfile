FROM tensorflow/serving:latest

# Install socat to forward Railway traffic to TF Serving
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model
ENV MONITORING_CONFIG="/model_config/prometheus.config"

RUN echo '#!/bin/bash' > /usr/bin/tf_serving_entrypoint.sh && \
    echo 'export PORT="${PORT:-8080}"' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting TF Serving internally on 8501..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'tensorflow_model_server --port=8500 --rest_api_port=8501 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} --monitoring_config_file=${MONITORING_CONFIG} "$@" &' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Waiting for TF Serving to start..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'sleep 3' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting socat proxy to forward Railway traffic on port $PORT to 8501..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'exec socat TCP-LISTEN:${PORT},fork,reuseaddr TCP4:127.0.0.1:8501' >> /usr/bin/tf_serving_entrypoint.sh && \
    chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
