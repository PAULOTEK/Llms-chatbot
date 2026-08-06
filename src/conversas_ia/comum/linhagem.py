from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def registro_execucao(
    run_id: str,
    job: str,
    camada: str,
    tabela: str,
    linhas_lidas: int,
    linhas_escritas: int,
    git_sha: str = "desconhecido",
) -> dict:
    agora = datetime.now(timezone.utc).isoformat()
    return {
        "run_id": run_id,
        "job": job,
        "camada": camada,
        "tabela": tabela,
        "linhas_lidas": linhas_lidas,
        "linhas_escritas": linhas_escritas,
        "iniciado_em": agora,
        "finalizado_em": agora,
        "git_sha": git_sha,
    }


def gravar_linhagem(spark: SparkSession, registro: dict, tabela: str) -> None:
    spark.createDataFrame([registro]).write.mode("append").format("delta").saveAsTable(tabela)


def adicionar_metadados_ingestao(df: DataFrame, arquivo: str, fonte: str) -> DataFrame:
    return (
        df.withColumn("_arquivo_origem", F.lit(arquivo))
        .withColumn("_ingerido_em", F.current_timestamp())
        .withColumn("_fonte", F.lit(fonte))
    )
