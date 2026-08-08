from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType, StructField, StructType

from conversas_ia.privacidade.anonimizacao import anonimizar_texto
from conversas_ia.transformacao.gold_analitico import fato_conversa
from conversas_ia.transformacao.gold_datasets_ia import dataset_avaliacao, dataset_sft
from conversas_ia.transformacao.silver import deduplicar_turnos, explodir_turnos, normalizar_texto


def test_normalizacao():
    assert normalizar_texto("  Ｈello <b>mundo</b>  ", True) == "hello mundo"


def test_explode_e_deduplicacao(spark):
    mensagem = StructType(
        [
            StructField("papel", StringType()),
            StructField("texto", StringType()),
            StructField("timestamp", StringType()),
        ]
    )
    schema = StructType(
        [
            StructField("conversa_id", StringType()),
            StructField("canal", StringType()),
            StructField("idioma", StringType()),
            StructField("mensagens", ArrayType(mensagem)),
        ]
    )
    df = spark.createDataFrame(
        [
            (
                "c1",
                "chat",
                "pt",
                [
                    {"papel": "user", "texto": "oi", "timestamp": "2024-01-01T00:00:00"},
                    {"papel": "assistant", "texto": "Olá", "timestamp": "2024-01-01T00:00:01"},
                    {"papel": "assistant", "texto": "Olá", "timestamp": "2024-01-01T00:00:02"},
                ],
            )
        ],
        schema,
    )
    turnos = explodir_turnos(df)
    assert turnos.count() == 3
    assert deduplicar_turnos(turnos).count() == 2


def test_pii_deterministico(spark):
    df = spark.createDataFrame(
        [("c1", "CPF 123.456.789-00 e x@y.com telefone 11999998888")], ["conversa_id", "texto"]
    )
    primeiro = anonimizar_texto(df, salt="segredo").collect()[0]
    segundo = anonimizar_texto(df, salt="segredo").collect()[0]
    assert primeiro.texto == segundo.texto
    assert "123.456.789-00" not in primeiro.texto and "EMAIL" in primeiro.texto
    assert set(primeiro.pii_detectada) >= {"cpf", "email", "telefone"}


def test_pii_multiplos_valores_e_telefone_nao_engole_cpf(spark):
    linhas = [
        ("a", "CPFs 123.456.789-00 e 987.654.321-00 telefone 11999998888"),
        ("b", "Repito o CPF 123.456.789-00"),
    ]
    df = spark.createDataFrame(linhas, ["conversa_id", "texto"])
    anonimizado = anonimizar_texto(df, salt="segredo").orderBy("conversa_id").collect()
    assert anonimizado[0].texto.count("[CPF_") == 2
    tokens = [
        parte.split("]")[0] for parte in anonimizado[0].texto.split("[") if parte.startswith("CPF_")
    ]
    assert tokens[0] != tokens[1]
    token_repetido = [
        parte.split("]")[0] for parte in anonimizado[1].texto.split("[") if parte.startswith("CPF_")
    ][0]
    assert token_repetido == tokens[0]
    assert "[TELEFONE_" in anonimizado[0].texto


def test_pii_nativo_deterministico(spark):
    df = spark.createDataFrame(
        [("c1", "CPF 123.456.789-00 e 987.654.321-00")], ["conversa_id", "texto"]
    )
    anonimizado = anonimizar_texto(df, salt="segredo", modo="nativo").collect()[0].texto

    assert "123.456.789-00" not in anonimizado
    assert anonimizado.count("[CPF_") == 2
    assert anonimizado.split("[CPF_")[1][:10] != anonimizado.split("[CPF_")[2][:10]


def test_dataset_avaliacao_filtra_teste_e_cria_referencia(spark):
    linhas = [
        ("c1", 0, "user", "pergunta", "pt", "chat"),
        ("c1", 1, "assistant", "resposta", "pt", "chat"),
    ]
    df = spark.createDataFrame(
        linhas, ["conversa_id", "turno_id", "papel", "texto", "idioma", "canal"]
    )
    sft = dataset_sft(df).withColumn("split", F.lit("teste"))
    avaliacao = dataset_avaliacao(sft, idiomas=["pt"])
    linha = avaliacao.collect()[0]
    assert linha.referencia == "resposta"
    assert linha.contexto == "pergunta"
    assert linha.categoria == "geral"


def test_gold_datasets_e_agregacao(spark):
    linhas = [
        ("c1", 0, "user", "pergunta", "pt", "chat"),
        ("c1", 1, "assistant", "resposta", "pt", "chat"),
    ]
    df = spark.createDataFrame(
        linhas, ["conversa_id", "turno_id", "papel", "texto", "idioma", "canal"]
    )
    sft = dataset_sft(df)
    assert sft.count() == 1
    assert sft.collect()[0].split in {"treino", "validacao", "teste"}
    fato = fato_conversa(
        df.withColumn("timestamp", F.current_timestamp()).withColumn(
            "tamanho_texto", F.length("texto")
        )
    )
    assert fato.collect()[0].turnos == 2
