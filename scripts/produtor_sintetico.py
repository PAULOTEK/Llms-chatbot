"""Publica conversas sintéticas no Kafka local (pip install -e '.[streaming]')."""

import argparse
import json

from kafka import KafkaProducer

from conversas_ia.comum.spark import criar_sessao
from conversas_ia.ingestao.gerador_sintetico import gerar_conversas


def publicar(bootstrap_servers: str, topic: str, quantidade: int) -> None:
    spark = criar_sessao("produtor-sintetico", local=True)
    produtor = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda valor: json.dumps(valor).encode("utf-8"),
    )
    try:
        for registro in gerar_conversas(spark, quantidade).toLocalIterator():
            produtor.send(topic, registro.asDict(recursive=True))
        produtor.flush()
    finally:
        produtor.close()
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="conversas")
    parser.add_argument("--quantidade", type=int, default=10)
    args = parser.parse_args()
    publicar(args.bootstrap_servers, args.topic, args.quantidade)
