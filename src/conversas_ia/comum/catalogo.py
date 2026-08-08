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
            sql = re.sub(r"\b__CATALOG__\b", catalogo, comando)
            try:
                spark.sql(sql)
            except Exception as exc:
                if re.match(r"^CREATE\s+CATALOG\b", comando, re.IGNORECASE):
                    print(
                        "Aviso: CREATE CATALOG não executado; "
                        f"seguindo com o catálogo existente ({exc})."
                    )
                    continue
                raise
