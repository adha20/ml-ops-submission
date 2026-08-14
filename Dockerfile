FROM tensorflow/serving:latest

COPY ./app/model_store /models/customer-churn-model
COPY ./monitoring /model_config
ENV MODEL_NAME=customer-churn-model

ENV MONITORING_CONFIG="/model_config/prometheus.config"
ENV PORT=8501
EXPOSE 8501
RUN printf '#!/bin/bash\n\n\
env\n\
tensorflow_model_server --port=8500 --rest_api_port=${PORT} \\\n\
--model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} \\\n\
--monitoring_config_file=${MONITORING_CONFIG} \\\n\
"$@"' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8501/v1/models/customer-churn-model || exit 1

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
