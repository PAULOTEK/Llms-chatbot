from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from conversas_ia.transformacao.silver import (
    deduplicar_turnos,
    enriquecer_turnos,
    explodir_turnos,
    normalizar_mensagens,
)


def preparar_silver_stream(df: DataFrame, watermark: str = "10 minutes") -> DataFrame:
    """Deduplica eventos tardios; dados além do watermark são descartados pelo Spark."""
    turnos = explodir_turnos(df)
    turnos = turnos.withWatermark("timestamp", watermark).dropDuplicates(
        ["conversa_id", "turno_id", "timestamp"]
    )
    return turnos


def _merge_delta(batch: DataFrame, tabela: str) -> None:
    from delta.tables import DeltaTable

    destino = DeltaTable.forName(batch.sparkSession, tabela)
    (
        destino.alias("destino")
        .merge(
            batch.alias("origem"),
            "destino.conversa_id = origem.conversa_id " "AND destino.turno_id = origem.turno_id",
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )


def processar_microbatch_silver(
    batch: DataFrame, batch_id: int, tabela: str, salt: str = "salt"
) -> None:
    if batch.isEmpty():
        return
    tratado = normalizar_mensagens(batch)
    tratado = deduplicar_turnos(tratado)
    tratado = enriquecer_turnos(tratado, salt)
    _merge_delta(tratado, tabela)


def iniciar_silver_stream(
    bronze: DataFrame,
    tabela: str,
    checkpoint: str,
    watermark: str = "10 minutes",
    trigger: str = "availableNow",
    salt: str = "salt",
) -> StreamingQuery:
    fluxo = preparar_silver_stream(bronze, watermark)
    escritor = fluxo.writeStream.foreachBatch(
        lambda batch, batch_id: processar_microbatch_silver(batch, batch_id, tabela, salt)
    ).option("checkpointLocation", checkpoint)
    if trigger == "availableNow":
        escritor = escritor.trigger(availableNow=True)
    else:
        escritor = escritor.trigger(processingTime=trigger.split("=", 1)[-1])
    return escritor.start()
