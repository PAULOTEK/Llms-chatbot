import time
from collections.abc import Callable
from typing import Any

import requests
from pyspark.sql import DataFrame, SparkSession

from conversas_ia.comum.linhagem import adicionar_metadados_ingestao


def buscar_paginas(
    url: str,
    headers: dict[str, str] | None = None,
    limite: int = 100,
    tentativas: int = 3,
    requisitor: Callable[..., Any] = requests.get,
) -> list[dict]:
    pagina, resultados = 1, []
    while True:
        for tentativa in range(tentativas):
            try:
                resposta = requisitor(
                    url, params={"page": pagina, "limit": limite}, headers=headers, timeout=30
                )
                resposta.raise_for_status()
                payload = resposta.json()
                break
            except requests.RequestException:
                if tentativa == tentativas - 1:
                    raise
                time.sleep(2**tentativa)
        itens = payload.get("data", payload if isinstance(payload, list) else [])
        resultados.extend(itens)
        if not payload.get("next") and len(itens) < limite:
            return resultados
        pagina += 1


def para_bronze(spark: SparkSession, registros: list[dict], endpoint: str) -> DataFrame:
    return adicionar_metadados_ingestao(spark.createDataFrame(registros), endpoint, "api_rest")
