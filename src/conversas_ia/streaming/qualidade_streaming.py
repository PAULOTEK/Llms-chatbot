from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from conversas_ia.qualidade.executor import executar
from conversas_ia.qualidade.regras import Regra


def processar_qualidade_microbatch(
    batch: DataFrame,
    batch_id: int,
    regras: list[Regra],
    tabela_relatorio: str,
    tabela_quarentena: str,
) -> None:
    relatorio, quarentena = executar(batch, regras)
    relatorio.withColumn("batch_id", F.lit(batch_id)).write.mode("append").format(
        "delta"
    ).saveAsTable(tabela_relatorio)
    quarentena.withColumn("batch_id", F.lit(batch_id)).write.mode("append").format(
        "delta"
    ).saveAsTable(tabela_quarentena)
