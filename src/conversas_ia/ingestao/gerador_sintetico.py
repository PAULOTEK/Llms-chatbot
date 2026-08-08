from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def gerar_conversas(spark: SparkSession, quantidade: int = 10) -> DataFrame:
    """Gera conversas com operações Spark, sem coletar dados no driver.

    A construção via ``spark.createDataFrame(list[dict])`` usa arquivos
    temporários locais que não são graváveis em alguns ambientes Serverless.
    ``range`` mantém a geração distribuída e compatível com Spark Connect.
    """
    inicio = F.from_unixtime(
        F.lit(1704067200) + F.col("id") * 60,
        "yyyy-MM-dd'T'HH:mm:ss'Z'",
    )
    fim = F.from_unixtime(
        F.lit(1704067200) + F.col("id") * 60 + 4,
        "yyyy-MM-dd'T'HH:mm:ss'Z'",
    )
    mensagem_usuario = F.struct(
        F.lit("user").alias("papel"),
        F.format_string("Olá, preciso de ajuda %d", F.col("id")).alias("texto"),
        inicio.alias("timestamp"),
    )
    mensagem_assistente = F.struct(
        F.lit("assistant").alias("papel"),
        F.lit("Claro, como posso ajudar?").alias("texto"),
        fim.alias("timestamp"),
    )
    return spark.range(quantidade).select(
        F.format_string("conv-%04d", F.col("id")).alias("conversa_id"),
        F.lit("chat").alias("canal"),
        F.lit("pt").alias("idioma"),
        F.array(mensagem_usuario, mensagem_assistente).alias("mensagens"),
    )
