# Databricks notebook source
from pyspark.sql import SparkSession

dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")
dbutils.widgets.text("raiz_projeto", "")

# COMMAND ----------

from pathlib import Path

spark = SparkSession.active()

from conversas_ia.comum.config import carregar_ambiente, carregar_yaml
from conversas_ia.comum.catalogo import preparar_catalogo
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.ingestao.arquivos_jsonl import ler_jsonl, escrever_bronze
from conversas_ia.ingestao.gerador_sintetico import gerar_conversas

ambiente = dbutils.widgets.get("ambiente")
data_execucao = dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("01_ingestao_bronze")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
pipeline = carregar_yaml(f"{raiz_projeto}/config/pipeline.yml")
preparar_catalogo(spark, raiz_projeto, config["catalogo"])

# COMMAND ----------

landing = config["paths"]["landing"]
bronze = f'{config["catalogo"]}.{config["schemas"]["bronze"]}.conversas_raw'
fonte = config.get("ingestao", {}).get("fonte", "sintetica")
if fonte == "jsonl":
    df = ler_jsonl(spark, landing)
else:
    quantidade = config.get("ingestao", {}).get("quantidade_sintetica", 10)
    print("Fonte externa não configurada; usando conversas sintéticas.")
    df = gerar_conversas(spark, quantidade)
escrever_bronze(df, bronze)
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao, "01_ingestao_bronze", "bronze", bronze, df.count(), df.count()
    ),
    f'{config["catalogo"]}.{config["schemas"]["governanca"]}.linhagem',
)
