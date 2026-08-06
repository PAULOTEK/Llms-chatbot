from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.streaming import StreamingQuery

from conversas_ia.comum.hash import hash_colunas
from conversas_ia.streaming.esquemas import CONVERSA_SCHEMA


def opcoes_kafka(config: dict[str, Any]) -> dict[str, str]:
    kafka = config.get("kafka", config)
    opcoes = {
        "kafka.bootstrap.servers": kafka["bootstrap_servers"],
        "subscribe": kafka["topic"],
        "startingOffsets": kafka.get("starting_offsets", "latest"),
        "failOnDataLoss": str(kafka.get("fail_on_data_loss", True)).lower(),
    }
    if kafka.get("max_offsets_per_trigger") is not None:
        opcoes["maxOffsetsPerTrigger"] = str(kafka["max_offsets_per_trigger"])
    if kafka.get("security_protocol"):
        opcoes["kafka.security.protocol"] = kafka["security_protocol"]
    if kafka.get("sasl_mechanism"):
        opcoes["kafka.sasl.mechanism"] = kafka["sasl_mechanism"]
    if kafka.get("sasl_jaas_config"):
        opcoes["kafka.sasl.jaas.config"] = kafka["sasl_jaas_config"]
    return opcoes


def parsear_payload_kafka(df: DataFrame) -> DataFrame:
    """Converte o payload binário Kafka em conversa e preserva metadados."""
    conversa = F.from_json(F.col("value").cast("string"), CONVERSA_SCHEMA)
    parseado = df.select(
        "topic",
        "partition",
        "offset",
        "timestamp",
        conversa.alias("conversa"),
    ).select("conversa.*", "topic", "partition", "offset", "timestamp")
    colunas_hash = ["conversa_id", "canal", "idioma", "mensagens", "categoria", "offset"]
    return hash_colunas(
        parseado.withColumn("_ingerido_em", F.current_timestamp())
        .withColumn("_fonte", F.lit("kafka"))
        .withColumn("_kafka_topico", F.col("topic"))
        .withColumn("_kafka_particao", F.col("partition"))
        .withColumn("_kafka_offset", F.col("offset"))
        .withColumn("_kafka_timestamp", F.col("timestamp")),
        colunas_hash,
    )


def ler_stream_kafka(spark: SparkSession, config: dict[str, Any]) -> DataFrame:
    return parsear_payload_kafka(
        spark.readStream.format("kafka").options(**opcoes_kafka(config)).load()
    )


def escrever_stream_bronze(
    df: DataFrame,
    caminho_ou_tabela: str,
    checkpoint: str,
    trigger: str = "availableNow",
) -> StreamingQuery:
    escritor = (
        df.writeStream.format("delta").outputMode("append").option("checkpointLocation", checkpoint)
    )
    if trigger == "availableNow":
        escritor = escritor.trigger(availableNow=True)
    elif trigger.startswith("processingTime"):
        intervalo = trigger.split("=", 1)[1] if "=" in trigger else "1 minute"
        escritor = escritor.trigger(processingTime=intervalo)
    else:
        raise ValueError("trigger deve ser availableNow ou processingTime=<intervalo>")
    if caminho_ou_tabela.startswith("/"):
        return escritor.start(caminho_ou_tabela)
    return escritor.toTable(caminho_ou_tabela)
