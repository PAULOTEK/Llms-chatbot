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
from conversas_ia.transformacao.gold_datasets_ia import dataset_avaliacao, dataset_sft

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("05_gold_datasets_ia")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
pipeline = carregar_yaml("/Workspace/Repos/conversas-ia/config/pipeline.yml")
base = f'{config["catalogo"]}.{config["schemas"]}'

# COMMAND ----------

turnos = spark.table(f"{base['silver']}.turnos").filter("valido AND size(pii_detectada) = 0")
sft = dataset_sft(turnos, pipeline["datasets"]["minimo_turnos"])
avaliacao = dataset_avaliacao(sft, pipeline["datasets"].get("idiomas"))
sft.write.mode("overwrite").format("delta").saveAsTable(f"{base['gold']}.dataset_sft")
avaliacao.write.mode("overwrite").format("delta").saveAsTable(f"{base['gold']}.dataset_avaliacao")
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao,
        "05_gold_datasets_ia",
        "gold",
        f"{base['gold']}.dataset_sft",
        turnos.count(),
        sft.count(),
    ),
    f"{base['governanca']}.linhagem",
)
