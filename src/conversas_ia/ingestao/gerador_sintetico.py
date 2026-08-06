from datetime import datetime, timedelta, timezone

from pyspark.sql import DataFrame, SparkSession


def gerar_conversas(spark: SparkSession, quantidade: int = 10) -> DataFrame:
    base = []
    for i in range(quantidade):
        inicio = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=i)
        base.append(
            {
                "conversa_id": f"conv-{i:04d}",
                "canal": "chat",
                "idioma": "pt",
                "mensagens": [
                    {
                        "papel": "user",
                        "texto": f"Olá, preciso de ajuda {i}",
                        "timestamp": inicio.isoformat(),
                    },
                    {
                        "papel": "assistant",
                        "texto": "Claro, como posso ajudar?",
                        "timestamp": (inicio + timedelta(seconds=4)).isoformat(),
                    },
                ],
            }
        )
    return spark.createDataFrame(base)
