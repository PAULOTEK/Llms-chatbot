# Databricks notebook source
dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")

# COMMAND ----------

from conversas_ia.comum.config import carregar_ambiente
from conversas_ia.comum.linhagem import gravar_linhagem, registrar_inicio, registro_execucao
from conversas_ia.transformacao.gold_analitico import dimensao_canal, fato_conversa

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
registrar_inicio("04_gold_analitico")
config = carregar_ambiente("/Workspace/Repos/conversas-ia/config/ambientes.yml", ambiente)
base = f'{config["catalogo"]}.{config["schemas"]}'

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
