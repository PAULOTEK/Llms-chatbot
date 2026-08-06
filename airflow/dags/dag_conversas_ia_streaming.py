"""Dispara o job availableNow a cada 15 minutos para consumir o Kafka."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

try:
    from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
except ImportError:
    DatabricksRunNowOperator = None


with DAG(
    dag_id="conversas_ia_streaming",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["kafka", "streaming", "near-real-time"],
    doc_md=__doc__,
) as dag:
    if DatabricksRunNowOperator:
        consumir = DatabricksRunNowOperator(
            task_id="consumir_kafka_available_now",
            databricks_conn_id="databricks_default",
            job_name="conversas-ia-streaming-available-now",
            notebook_params={"ambiente": "prd", "data_execucao": "{{ ds }}"},
        )
    else:
        consumir = PythonOperator(
            task_id="consumir_kafka_available_now",
            python_callable=lambda: print("Fallback: disparar job streaming via API Databricks"),
        )
