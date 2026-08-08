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
from conversas_ia.qualidade.executor import executar
from conversas_ia.qualidade.regras import carregar_regras

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
raiz_projeto = dbutils.widgets.get("raiz_projeto").strip()
if not raiz_projeto:
    raiz_projeto = (
        str(Path(__file__).resolve().parents[1]) if "__file__" in globals() else str(Path.cwd())
    )
registrar_inicio("03_qualidade_quarentena")
config = carregar_ambiente(f"{raiz_projeto}/config/ambientes.yml", ambiente)
base = f'{config["catalogo"]}.{config["schemas"]}'

# COMMAND ----------

turnos = spark.table(f"{base['silver']}.turnos")
regras = carregar_regras("/Workspace/Repos/conversas-ia/config/qualidade/regras_silver.yml")
relatorio, quarentena = executar(turnos, regras)
relatorio.write.mode("append").format("delta").saveAsTable(
    f"{base['governanca']}.qualidade_execucoes"
)
quarentena.write.mode("append").format("delta").saveAsTable(f"{base['silver']}.quarentena")
if relatorio.filter("status = 'falha' AND severidade = 'critica'").count():
    raise RuntimeError("Qualidade crítica falhou; registros enviados para quarentena.")
gravar_linhagem(
    spark,
    registro_execucao(
        data_execucao,
        "03_qualidade_quarentena",
        "silver",
        f"{base['silver']}.turnos",
        turnos.count(),
        turnos.count(),
    ),
    f"{base['governanca']}.linhagem",
)
