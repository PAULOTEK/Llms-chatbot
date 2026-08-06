from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def separar_quarentena(df: DataFrame, condicao_valida) -> tuple[DataFrame, DataFrame]:
    return df.filter(condicao_valida), df.filter(~condicao_valida).withColumn(
        "_quarentenado_em", F.current_timestamp()
    )
