from pyspark.sql.types import StringType, StructField, StructType

from conversas_ia.qualidade.executor import executar
from conversas_ia.qualidade.regras import Regra


def test_qualidade_passa(spark):
    df = spark.createDataFrame([("c1", "user")], ["conversa_id", "papel"])
    relatorio, quarentena = executar(
        df,
        [
            Regra("id", "not_null", "conversa_id"),
            Regra("papel", "dominio", "papel", valores=["user"]),
        ],
    )
    assert relatorio.filter("status = 'falha'").count() == 0
    assert quarentena.count() == 0


def test_qualidade_falha_e_quarentena(spark):
    schema = StructType(
        [StructField("conversa_id", StringType()), StructField("papel", StringType())]
    )
    df = spark.createDataFrame([(None, "bot")], schema)
    relatorio, _ = executar(
        df,
        [
            Regra("id", "not_null", "conversa_id"),
            Regra("papel", "dominio", "papel", valores=["user"]),
        ],
    )
    assert relatorio.filter("status = 'falha'").count() == 2
