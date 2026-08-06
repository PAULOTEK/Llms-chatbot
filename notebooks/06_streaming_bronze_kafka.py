# Databricks notebook source
dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")

# COMMAND ----------

from conversas_ia.comum.config import carregar_ambiente, carregar_yaml
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.streaming.kafka_bronze import escrever_stream_bronze, ler_stream_kafka

ambiente = dbutils.widgets.get("ambiente")
data_execucao = dbutils.widgets.get("data_execucao")
registrar_inicio("06_streaming_bronze_kafka")
config = carregar_ambiente("/Workspace/Repos/conversas-ia/config/ambientes.yml", ambiente)
pipeline = carregar_yaml("/Workspace/Repos/conversas-ia/config/pipeline.yml")

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
