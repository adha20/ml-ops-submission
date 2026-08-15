FROM tensorflow/serving:latest

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model

ENV MONITORING_CONFIG="/model_config/prometheus.config"
ENV PORT=8080
EXPOSE 8080
RUN printf '#!/bin/bash\n\n\
env\n\
tensorflow_model_server --port=8500 --rest_api_port=${PORT} \\
--model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} \\
--monitoring_config_file=${MONITORING_CONFIG} \\
"$@"' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:${PORT}/v1/models/customer-churn-model || exit 1

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
