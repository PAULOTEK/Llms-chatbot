from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def preparar_bronze(df: DataFrame) -> DataFrame:
    return df.withColumn("_ingerido_em", F.coalesce(F.col("_ingerido_em"), F.current_timestamp()))
