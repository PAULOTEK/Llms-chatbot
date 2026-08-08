import hashlib
import os
import re

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType

from conversas_ia.privacidade.deteccao_pii import PADROES, detectar_tipos

_ORDEM_PADROES = ("email", "cartao", "cnpj", "cpf", "telefone")
_PADRAO_COMBINADO = "|".join(f"(?P<{tipo}>{PADROES[tipo]})" for tipo in _ORDEM_PADROES)


def substituir_pii(texto: str | None, salt: str) -> str | None:
    """Pseudonimiza cada ocorrência de PII por `[TIPO_<hash>]` de forma determinística."""
    if texto is None:
        return None

    def substituir(match: re.Match) -> str:
        tipo = next(nome for nome in _ORDEM_PADROES if match.group(nome) is not None)
        token = hashlib.sha256(f"{salt}{match.group(0)}".encode()).hexdigest()[:10]
        return f"[{tipo.upper()}_{token}]"

    return re.sub(_PADRAO_COMBINADO, substituir, texto)


def anonimizar_texto(df: DataFrame, coluna: str = "texto", salt: str = "salt") -> DataFrame:
    original = F.col(coluna)
    if os.getenv("DATABRICKS_RUNTIME_VERSION") or os.getenv("SPARK_CONNECT_MODE_ENABLED"):
        anonimizado = original
        for tipo in _ORDEM_PADROES:
            anonimizado = F.regexp_replace(
                anonimizado,
                PADROES[tipo],
                f"[{tipo.upper()}_REDACTED]",
            )
    else:
        anonimizar = F.udf(lambda texto: substituir_pii(texto, salt), StringType())
        anonimizado = anonimizar(original)
    return df.withColumn("pii_detectada", detectar_tipos(original)).withColumn(coluna, anonimizado)
