from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def fato_conversa(turnos: DataFrame) -> DataFrame:
    return (
        turnos.groupBy("conversa_id")
        .agg(
            F.count("*").alias("turnos"),
            F.min("timestamp").alias("inicio"),
            F.max("timestamp").alias("fim"),
            F.avg(F.when(F.col("papel") == "assistant", F.col("tamanho_texto"))).alias(
                "tamanho_medio_resposta"
            ),
            (
                F.avg(F.col("latencia_ms")).alias("latencia_media_ms")
                if "latencia_ms" in turnos.columns
                else F.lit(None).cast("double").alias("latencia_media_ms")
            ),
        )
        .withColumn(
            "duracao_segundos",
            F.coalesce(F.col("fim").cast("long") - F.col("inicio").cast("long"), F.lit(0)),
        )
        .withColumn("resolvida", F.lit(None).cast("boolean"))
    )


def dimensao_canal(turnos: DataFrame) -> DataFrame:
    return turnos.select("canal").distinct().withColumn("canal_sk", F.xxhash64("canal"))
