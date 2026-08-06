from pyspark.sql import DataFrame, SparkSession


def ler_jdbc(spark: SparkSession, url: str, tabela: str, propriedades: dict) -> DataFrame:
    return spark.read.jdbc(url=url, table=tabela, properties=propriedades)
