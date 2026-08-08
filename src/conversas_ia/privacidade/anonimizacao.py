import hashlib
import re

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

from conversas_ia.privacidade.deteccao_pii import PADROES, detectar_tipos

_ORDEM_PADROES = ("email", "cartao", "cnpj", "cpf", "telefone")
_PADRAO_COMBINADO = "|".join(f"(?P<{tipo}>{PADROES[tipo]})" for tipo in _ORDEM_PADROES)


def _substituidor_nativo(tipo: str, salt: str):
    def substituir(acumulado, valor):
        padrao_literal = F.regexp_replace(
            valor,
            r"([\\.\[\]{}()*+?^$|])",
            r"\\$1",
        )
        return F.regexp_replace(
            acumulado,
            padrao_literal,
            F.concat(
                F.lit(f"[{tipo.upper()}_"),
                F.substring(F.sha2(F.concat(F.lit(salt), valor), 256), 1, 10),
                F.lit("]"),
            ),
        )

    return substituir


def substituir_pii(texto: str | None, salt: str) -> str | None:
    """Pseudonimiza cada ocorrência de PII por `[TIPO_<hash>]` de forma determinística."""
    if texto is None:
        return None

    def substituir(match: re.Match) -> str:
        tipo = next(nome for nome in _ORDEM_PADROES if match.group(nome) is not None)
        token = hashlib.sha256(f"{salt}{match.group(0)}".encode()).hexdigest()[:10]
        return f"[{tipo.upper()}_{token}]"

    return re.sub(_PADRAO_COMBINADO, substituir, texto)


def _anonimizar_nativo(original, salt: str):
    anonimizado = original
    for tipo in _ORDEM_PADROES:
        ocorrencias = F.array_distinct(F.regexp_extract_all(original, F.lit(PADROES[tipo]), 0))
        anonimizado = F.aggregate(
            ocorrencias,
            anonimizado,
            _substituidor_nativo(tipo, salt),
        )
    return anonimizado


def anonimizar_texto(
    df: DataFrame,
    coluna: str = "texto",
    salt: str = "salt",
    modo: str = "python",
) -> DataFrame:
    """Anonimiza PII com UDF local ou expressões nativas determinísticas.

    O modo ``nativo`` é necessário para Unity Catalog Serverless, onde Python
    UDFs são rejeitadas. Ambos os modos derivam o token do salt e do valor.
    """
    original = F.col(coluna)
    if modo == "python":
        anonimizar = F.udf(lambda texto: substituir_pii(texto, salt), StringType())
        anonimizado = anonimizar(original)
    elif modo == "nativo":
        anonimizado = _anonimizar_nativo(original, salt)
    else:
        raise ValueError(f"Modo de anonimização desconhecido: {modo}")
    return df.withColumn("pii_detectada", detectar_tipos(original)).withColumn(coluna, anonimizado)
