# Databricks notebook source
dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")

# COMMAND ----------

from conversas_ia.comum.config import carregar_ambiente, carregar_yaml
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.ingestao.arquivos_jsonl import ler_jsonl, escrever_bronze

ambiente = dbutils.widgets.get("ambiente")
data_execucao = dbutils.widgets.get("data_execucao")
registrar_inicio("01_ingestao_bronze")
config = carregar_ambiente("/Workspace/Repos/conversas-ia/config/ambientes.yml", ambiente)
pipeline = carregar_yaml("/Workspace/Repos/conversas-ia/config/pipeline.yml")

# COMMAND ----------

# Os conectores de API/JDBC são executados pelo pacote; este notebook só orquestra.
landing = config["paths"]["landing"]
bronze = f'{config["catalogo"]}.{config["schemas"]["bronze"]}.conversas_raw'
df = ler_jsonl(spark, landing)
escrever_bronze(df, bronze)
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao, "01_ingestao_bronze", "bronze", bronze, df.count(), df.count()
    ),
    f'{config["catalogo"]}.{config["schemas"]["governanca"]}.linhagem',
)
