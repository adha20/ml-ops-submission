FROM tensorflow/serving:latest

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model
ENV MONITORING_CONFIG="/model_config/prometheus.config"

EXPOSE 8080

RUN echo '#!/bin/bash' > /usr/bin/tf_serving_entrypoint.sh && \
    echo 'export PORT="${PORT:-8080}"' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting TF Serving on port $PORT..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'exec tensorflow_model_server --port=8500 --rest_api_port=$PORT --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} --monitoring_config_file=${MONITORING_CONFIG} "$@"' >> /usr/bin/tf_serving_entrypoint.sh && \
    chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
