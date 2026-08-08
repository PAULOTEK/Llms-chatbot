import re
from pathlib import Path

from pyspark.sql import SparkSession


def preparar_catalogo(spark: SparkSession, raiz_projeto: str, catalogo: str) -> None:
    """Cria os objetos básicos reutilizando o DDL versionado do projeto."""
    caminho = Path(raiz_projeto) / "sql" / "01_catalogo_schemas.sql"
    conteudo = caminho.read_text(encoding="utf-8")
    for trecho in conteudo.split(";"):
        comando = trecho.strip()
        if re.match(r"^CREATE\s+(CATALOG|SCHEMA|VOLUME)\b", comando, re.IGNORECASE):
            spark.sql(re.sub(r"\bconversas_dev\b", catalogo, comando))
