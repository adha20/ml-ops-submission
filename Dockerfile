FROM tensorflow/serving:latest

# Install HAProxy
RUN apt-get update && apt-get install -y haproxy && rm -rf /var/lib/apt/lists/*

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model
ENV MONITORING_CONFIG="/model_config/prometheus.config"

EXPOSE 8080

RUN cat << 'EOF' > /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 256
defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
frontend http_in
    bind *:8080
    default_backend tf_serving
backend tf_serving
    server tf_server 127.0.0.1:8502
EOF

RUN echo '#!/bin/bash' > /usr/bin/tf_serving_entrypoint.sh && \
    echo 'export PORT="${PORT:-8080}"' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'sed -i "s/bind \*:8080/bind \*:$PORT/g" /etc/haproxy/haproxy.cfg' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'haproxy -f /etc/haproxy/haproxy.cfg' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'echo "Starting TF Serving internally on 127.0.0.1:8502..."' >> /usr/bin/tf_serving_entrypoint.sh && \
    echo 'exec tensorflow_model_server --port=8500 --rest_api_port=8502 --model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} --monitoring_config_file=${MONITORING_CONFIG} "$@"' >> /usr/bin/tf_serving_entrypoint.sh && \
    chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
