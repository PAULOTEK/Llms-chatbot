from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def hash_colunas(df: DataFrame, colunas: list[str], alias: str = "_hash_linha") -> DataFrame:
    return df.withColumn(alias, F.sha2(F.to_json(F.struct(*[F.col(c) for c in colunas])), 256))


def hash_texto(texto: str, salt: str = "") -> str:
    import hashlib

    return hashlib.sha256(f"{salt}{texto}".encode()).hexdigest()
