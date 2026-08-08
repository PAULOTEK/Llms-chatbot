# Databricks notebook source
from pyspark.sql import SparkSession

dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")
dbutils.widgets.text("raiz_projeto", "")

# COMMAND ----------

from pathlib import Path

spark = SparkSession.active()

from conversas_ia.comum.config import carregar_ambiente, carregar_yaml
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.streaming.kafka_bronze import escrever_stream_bronze, ler_stream_kafka

ambiente = dbutils.widgets.get("ambiente")
data_execucao = dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("06_streaming_bronze_kafka")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
pipeline = carregar_yaml(f"{raiz_projeto}/config/pipeline.yml")

# COMMAND ----------

bronze = f'{config["catalogo"]}.{config["schemas"]["bronze"]}.conversas_kafka_raw'
stream = ler_stream_kafka(spark, config)
query = escrever_stream_bronze(
    stream,
    bronze,
    pipeline["streaming"]["checkpoints"]["bronze"],
    pipeline["streaming"]["trigger"],
)
query.awaitTermination()
gravar_linhagem(
    spark,
    registro_execucao(data_execucao, "06_streaming_bronze_kafka", "bronze", bronze, 0, 0),
    f'{config["catalogo"]}.{config["schemas"]["governanca"]}.linhagem',
)
