FROM apache/airflow:2.10.2-python3.11

USER airflow
RUN pip install --no-cache-dir "apache-airflow-providers-databricks==7.7.4"
COPY --chown=airflow:root . /opt/conversas-ia
RUN pip install --no-cache-dir /opt/conversas-ia
