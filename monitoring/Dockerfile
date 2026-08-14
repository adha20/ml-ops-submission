FROM prom/prometheus:v2.54.1

COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY prometheus.config /etc/prometheus/prometheus.config

EXPOSE 9090

CMD ["--config.file=/etc/prometheus/prometheus.yml"]
