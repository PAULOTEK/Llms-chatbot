from functools import reduce

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from conversas_ia.qualidade.regras import Regra


def _falha(df: DataFrame, regra: Regra):
    c = F.col(regra.coluna)
    if regra.tipo == "not_null":
        return c.isNull()
    if regra.tipo == "unicidade":
        return F.count("*").over(Window.partitionBy(regra.coluna)) > F.lit(1)
    if regra.tipo == "dominio":
        return ~c.isin(regra.valores or [])
    if regra.tipo == "range":
        condicao = F.lit(False)
        if regra.minimo is not None:
            condicao = condicao | (c < F.lit(regra.minimo))
        if regra.maximo is not None:
            condicao = condicao | (c > F.lit(regra.maximo))
        return condicao
    if regra.tipo == "regex":
        return ~c.rlike(regra.padrao or "")
    raise ValueError(f"Tipo de regra desconhecido: {regra.tipo}")


def avaliar(df: DataFrame, regras: list[Regra]) -> DataFrame:
    linhas = [
        df.agg(
            F.count(F.lit(1)).alias("linhas"),
            F.coalesce(
                F.sum(F.when(_falha(df, regra), F.lit(1)).otherwise(F.lit(0))),
                F.lit(0),
            ).alias("falhas"),
        ).select(
            F.lit(regra.nome).alias("regra"),
            F.lit(regra.coluna).alias("coluna"),
            F.lit(regra.tipo).alias("tipo"),
            "linhas",
            "falhas",
            F.when(F.col("falhas") > 0, F.lit("falha")).otherwise(F.lit("passa")).alias("status"),
            F.lit(regra.severidade).alias("severidade"),
        )
        for regra in regras
    ]
    return reduce(DataFrame.unionByName, linhas)


def executar(
    df: DataFrame, regras: list[Regra], severidade_critica: str = "critica"
) -> tuple[DataFrame, DataFrame]:
    relatorio = avaliar(df, regras)
    condicao = F.lit(False)
    for regra in regras:
        if regra.severidade == severidade_critica:
            condicao = condicao | _falha(df, regra)
    return relatorio, df.filter(condicao)
