FROM tensorflow/serving:latest

# Install Nginx to proxy Railway traffic to TF Serving
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model
ENV MONITORING_CONFIG="/model_config/prometheus.config"

# Create a simple Nginx config that listens on 8501 and proxies to TF Serving on 8502
RUN echo "events {} \
http { \
    server { \
        listen 8501; \
        listen [::]:8501; \
        location / { \
            proxy_pass http://127.0.0.1:8502; \
        } \
    } \
}" > /etc/nginx/nginx.conf

RUN echo '#!/bin/bash' > /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting Nginx Proxy on port 8501..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'nginx' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting TF Serving internally on 127.0.0.1:8502..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'exec tensorflow_model_server --port=8500 --rest_api_port=8502 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} --monitoring_config_file=${MONITORING_CONFIG} "$@"' >> /usr/bin/tf_serving_entrypoint.sh && \
    chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
