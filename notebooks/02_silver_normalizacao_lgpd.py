# Databricks notebook source
dbutils.widgets.text("ambiente", "dev")
dbutils.widgets.text("data_execucao", "")

# COMMAND ----------

from conversas_ia.comum.config import carregar_ambiente, carregar_yaml
from conversas_ia.comum.linhagem import registro_execucao, gravar_linhagem
from conversas_ia.privacidade.anonimizacao import anonimizar_texto
from conversas_ia.transformacao.silver import (
    deduplicar_turnos,
    enriquecer_turnos,
    explodir_turnos,
    normalizar_mensagens,
)

ambiente, data_execucao = dbutils.widgets.get("ambiente"), dbutils.widgets.get("data_execucao")
config = carregar_ambiente("/Workspace/Repos/conversas-ia/config/ambientes.yml", ambiente)
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
