import re
import unicodedata

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

from conversas_ia.privacidade.anonimizacao import anonimizar_texto


def normalizar_texto(valor: str | None, lowercase: bool = False) -> str | None:
    if valor is None:
        return None
    texto = unicodedata.normalize("NFKC", valor)
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto.lower() if lowercase else texto


def normalizar_mensagens(
    df: DataFrame, coluna: str = "texto", lowercase: bool = False
) -> DataFrame:
    # NFKC não possui equivalente completo em expressões Spark; isole o UDF
    # Unicode e mantenha markup/espaços/lowercase em funções nativas.
    normalizar_unicode = F.udf(
        lambda valor: unicodedata.normalize("NFKC", valor) if valor is not None else None,
        StringType(),
    )
    texto = normalizar_unicode(F.col(coluna))
    texto = F.regexp_replace(texto, r"<[^>]+>", " ")
    texto = F.trim(F.regexp_replace(texto, r"\s+", " "))
    if lowercase:
        texto = F.lower(texto)
    return df.withColumn(coluna, texto)


def explodir_turnos(df: DataFrame) -> DataFrame:
    mensagens = F.posexplode("mensagens")
    return df.select(
        "conversa_id", "canal", "idioma", mensagens.alias("turno_id", "mensagem")
    ).select(
        "conversa_id",
        "turno_id",
        "canal",
        "idioma",
        F.col("mensagem.papel").alias("papel"),
        F.col("mensagem.texto").alias("texto"),
        F.to_timestamp("mensagem.timestamp").alias("timestamp"),
    )


def deduplicar_turnos(df: DataFrame) -> DataFrame:
    janela = Window.partitionBy("conversa_id", "turno_id").orderBy(
        F.col("timestamp").desc_nulls_last()
    )
    return (
        df.withColumn("_conteudo_hash", F.sha2(F.concat_ws("|", "papel", "texto"), 256))
        .dropDuplicates(["conversa_id", "_conteudo_hash"])
        .withColumn("_ordem", F.row_number().over(janela))
        .filter(F.col("_ordem") == 1)
        .drop("_ordem")
    )


def enriquecer_turnos(df: DataFrame, salt: str = "salt") -> DataFrame:
    df = anonimizar_texto(df, "texto", salt)
    toxicos = ["ódio", "ameaça", "violência"]
    tox = F.lower(F.col("texto"))
    return (
        df.withColumn("contagem_tokens_aprox", F.size(F.split(F.trim("texto"), r"\s+")))
        .withColumn("tamanho_texto", F.length("texto"))
        .withColumn("toxico", F.array_contains(F.array(*[tox.contains(t) for t in toxicos]), True))
        .withColumn("valido", F.col("conversa_id").isNotNull() & F.col("texto").isNotNull())
    )
