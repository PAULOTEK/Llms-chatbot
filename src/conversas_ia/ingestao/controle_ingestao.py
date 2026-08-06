from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def filtrar_nao_processados(
    df: DataFrame, controle: DataFrame, chave: str = "identificador"
) -> DataFrame:
    return df.join(controle.select(chave).distinct(), chave, "left_anti")


def marcar_processados(df: DataFrame, identificador: str, pagina: int | None = None) -> DataFrame:
    return df.select(
        F.lit(identificador).alias("identificador"),
        F.lit(pagina).cast("long").alias("pagina"),
        F.current_timestamp().alias("processado_em"),
    ).distinct()
