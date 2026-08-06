from pyspark.sql import DataFrame, SparkSession

from conversas_ia.comum.hash import hash_colunas
from conversas_ia.comum.linhagem import adicionar_metadados_ingestao


def ler_jsonl(spark: SparkSession, caminho: str) -> DataFrame:
    bruto = spark.read.json(caminho)
    colunas = [c for c in bruto.columns if not c.startswith("_")]
    return hash_colunas(adicionar_metadados_ingestao(bruto, caminho, "jsonl"), colunas)


def escrever_bronze(df: DataFrame, tabela: str) -> None:
    df.write.mode("append").format("delta").saveAsTable(tabela)
