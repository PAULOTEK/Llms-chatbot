from conversas_ia.ingestao.gerador_sintetico import gerar_conversas


def test_gerar_conversas_usa_schema_de_conversa(spark):
    conversas = gerar_conversas(spark, 2).collect()

    assert len(conversas) == 2
    assert conversas[0].conversa_id == "conv-0000"
    assert conversas[0].canal == "chat"
    assert len(conversas[0].mensagens) == 2
    assert conversas[0].mensagens[0].papel == "user"
