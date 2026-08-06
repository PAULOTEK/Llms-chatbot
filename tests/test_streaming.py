import json

from conversas_ia.streaming.kafka_bronze import opcoes_kafka, parsear_payload_kafka


def test_parse_kafka_payload_e_metadados(spark):
    payload = {
        "conversa_id": "c-stream",
        "canal": "chat",
        "idioma": "pt",
        "mensagens": [
            {
                "papel": "user",
                "texto": "Olá",
                "timestamp": "2024-01-01T00:00:00",
            }
        ],
    }
    bruto = spark.createDataFrame(
        [(json.dumps(payload).encode("utf-8"), "conversas", 2, 10, "2024-01-01T00:00:00")],
        ["value", "topic", "partition", "offset", "timestamp"],
    )
    parseado = parsear_payload_kafka(bruto).collect()[0]
    assert parseado.conversa_id == "c-stream"
    assert parseado._kafka_topico == "conversas"
    assert parseado._kafka_particao == 2
    assert parseado._kafka_offset == 10
    assert parseado._hash_linha


def test_opcoes_kafka_parametrizadas():
    opcoes = opcoes_kafka(
        {
            "bootstrap_servers": "localhost:9092",
            "topic": "conversas",
            "starting_offsets": "earliest",
            "max_offsets_per_trigger": 50,
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
        }
    )
    assert opcoes["kafka.bootstrap.servers"] == "localhost:9092"
    assert opcoes["startingOffsets"] == "earliest"
    assert opcoes["maxOffsetsPerTrigger"] == "50"
    assert opcoes["kafka.security.protocol"] == "SASL_SSL"
