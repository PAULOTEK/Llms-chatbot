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
from conversas_ia.privacidade.anonimizacao import anonimizar_texto
from conversas_ia.transformacao.silver import (
    deduplicar_turnos,
    enriquecer_turnos,
    explodir_turnos,
    normalizar_mensagens,
)

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("02_silver_normalizacao_lgpd")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
pipeline = carregar_yaml("/Workspace/Repos/conversas-ia/config/pipeline.yml")
base = f'{config["catalogo"]}.{config["schemas"]}'

# COMMAND ----------

raw = spark.table(f"{base['bronze']}.conversas_raw")
turnos = explodir_turnos(raw)
turnos = normalizar_mensagens(turnos)
turnos = deduplicar_turnos(turnos)
turnos = enriquecer_turnos(turnos, pipeline.get("lgpd", {}).get("salt_env", "salt"))
destino = f"{base['silver']}.turnos"
turnos.write.mode("append").format("delta").saveAsTable(destino)
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao, "02_silver_normalizacao_lgpd", "silver", destino, raw.count(), turnos.count()
    ),
    f"{base['governanca']}.linhagem",
)
