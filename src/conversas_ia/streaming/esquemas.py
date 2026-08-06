from pyspark.sql.types import ArrayType, StringType, StructField, StructType

MENSAGEM_SCHEMA = StructType(
    [
        StructField("papel", StringType(), True),
        StructField("texto", StringType(), True),
        StructField("timestamp", StringType(), True),
    ]
)

CONVERSA_SCHEMA = StructType(
    [
        StructField("conversa_id", StringType(), False),
        StructField("canal", StringType(), True),
        StructField("idioma", StringType(), True),
        StructField("mensagens", ArrayType(MENSAGEM_SCHEMA), True),
        StructField("categoria", StringType(), True),
    ]
)
