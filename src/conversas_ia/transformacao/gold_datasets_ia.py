from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from conversas_ia.privacidade.deteccao_pii import PADROES

_PII_RESIDUAL = "|".join(f"(?:{padrao})" for padrao in PADROES.values())


def _split(conversa_id):
    valor = F.pmod(F.xxhash64(conversa_id), F.lit(100))
    return F.when(valor < 80, "treino").when(valor < 90, "validacao").otherwise("teste")


def dataset_sft(turnos: DataFrame, minimo_turnos: int = 2) -> DataFrame:
    janela = Window.partitionBy("conversa_id").orderBy("turno_id")
    contexto_janela = janela.rowsBetween(Window.unboundedPreceding, -1)
    pares = (
        turnos.withColumn("_texto_anterior", F.lag("texto").over(janela))
        .withColumn("_contexto", F.concat_ws(" ", F.collect_list("texto").over(contexto_janela)))
        .filter(F.col("papel") == "assistant")
        .withColumn("prompt", F.col("_texto_anterior"))
        .withColumn("resposta", F.col("texto"))
        .filter(F.col("prompt").isNotNull())
    )
    pares = (
        pares.withColumn("_pii_anterior", F.lag("pii_detectada").over(janela))
        if "pii_detectada" in turnos.columns
        else pares.withColumn("_pii_anterior", F.lit(None).cast("array<string>"))
    )
    elegiveis = turnos.groupBy("conversa_id").count().filter(F.col("count") >= minimo_turnos)
    colunas = ["conversa_id", "prompt", "resposta", "_contexto", "_pii_anterior"]
    if "idioma" in turnos.columns:
        colunas.append("idioma")
    if "categoria" in turnos.columns:
        colunas.append("categoria")
    return (
        pares.join(elegiveis.select("conversa_id"), "conversa_id")
        .select(*colunas)
        .withColumn("contexto", F.col("_contexto"))
        .drop("_contexto")
        .withColumn("split", _split(F.col("conversa_id")))
    )


def dataset_avaliacao(
    sft: DataFrame,
    idiomas: list[str] | None = None,
    tamanho_minimo: int = 1,
    tamanho_maximo: int = 4000,
) -> DataFrame:
    """Seleciona exemplos de teste e adiciona referência/contexto para avaliação."""
    avaliado = sft.filter(F.col("split") == "teste")
    avaliado = avaliado.filter(
        F.length("prompt").between(tamanho_minimo, tamanho_maximo)
        & F.length("resposta").between(tamanho_minimo, tamanho_maximo)
    )
    avaliado = avaliado.filter(
        ~F.col("prompt").rlike(_PII_RESIDUAL) & ~F.col("resposta").rlike(_PII_RESIDUAL)
    )
    if "idioma" in sft.columns and idiomas:
        avaliado = avaliado.filter(F.col("idioma").isin(idiomas))
    if "_pii_anterior" in sft.columns:
        avaliado = avaliado.filter(
            F.col("_pii_anterior").isNull() | (F.size(F.col("_pii_anterior")) == 0)
        )
    return avaliado.withColumn("referencia", F.col("resposta")).withColumn(
        "categoria",
        (
            F.coalesce(F.col("categoria"), F.lit("geral"))
            if "categoria" in sft.columns
            else F.lit("geral")
        ),
    )
