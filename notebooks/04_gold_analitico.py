# Databricks notebook source
from pyspark.sql import SparkSession

dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")
dbutils.widgets.text("raiz_projeto", "")

# COMMAND ----------

from pathlib import Path

spark = SparkSession.active()

from conversas_ia.comum.config import carregar_ambiente
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.transformacao.gold_analitico import dimensao_canal, fato_conversa

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("04_gold_analitico")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
base = {camada: f'{config["catalogo"]}.{schema}' for camada, schema in config["schemas"].items()}

# COMMAND ----------

turnos = spark.table(f"{base['silver']}.turnos")
fato = fato_conversa(turnos)
dimensao = dimensao_canal(turnos)
fato.write.mode("overwrite").format("delta").saveAsTable(f"{base['gold']}.fato_conversa")
dimensao.write.mode("overwrite").format("delta").saveAsTable(f"{base['gold']}.dim_canal")
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao,
        "04_gold_analitico",
        "gold",
        f"{base['gold']}.fato_conversa",
        turnos.count(),
        fato.count(),
    ),
    f"{base['governanca']}.linhagem",
)
