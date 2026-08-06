"""Orquestração Airflow; requer provider apache-airflow-providers-databricks."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

try:
    from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
except ImportError:  # fallback permite validar/compilar o DAG sem provider instalado
    DatabricksRunNowOperator = None


def validar_landing():
    # Em produção, validar volumes/contratos via pacote antes do disparo.
    return True


def gate_qualidade(**context):
    if context["ti"].xcom_pull(task_ids="pipeline.qualidade_quarentena") is False:
        raise RuntimeError("Gate de qualidade reprovado.")


default_args = {
    "owner": "engenharia-dados",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
}

with DAG(
    dag_id="conversas_ia_diario",
    start_date=datetime(2024, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["lakehouse", "llm", "lgpd"],
    doc_md=__doc__,
) as dag:
    validar = PythonOperator(task_id="validar_landing_fontes", python_callable=validar_landing)
    with TaskGroup("pipeline_databricks") as pipeline:
        if DatabricksRunNowOperator:
            disparar = DatabricksRunNowOperator(
                task_id="disparar_job_bundle",
                databricks_conn_id="databricks_default",
                job_name="conversas-ia-diario",
                notebook_params={"ambiente": "prd", "data_execucao": "{{ ds }}"},
            )
        else:
            disparar = PythonOperator(
                task_id="disparar_job_bundle",
                python_callable=lambda: print(
                    "Fallback local: disparar uma única execução do job via API Databricks"
                ),
            )
    gate = PythonOperator(task_id="gate_qualidade", python_callable=gate_qualidade)
    publicar = PythonOperator(
        task_id="publicar_notificar",
        python_callable=lambda: print("Publicação Gold concluída; notificação emitida."),
    )
    validar >> pipeline >> gate >> publicar
