from pyspark.sql import SparkSession


def criar_sessao(
    app_name: str = "conversas-ia",
    configuracoes_locais: dict[str, str] | None = None,
    local: bool = False,
) -> SparkSession:
    """Cria sessão sem impor configurações incompatíveis com Serverless/Connect.

    Configurações como shuffle devem ser aplicadas apenas por chamadas locais,
    normalmente pela fixture de testes, e nunca como padrão de produção.
    """
    sessao_ativa = SparkSession.getActiveSession()
    if sessao_ativa is not None:
        return sessao_ativa

    builder = SparkSession.builder.appName(app_name)
    if local:
        for chave, valor in (configuracoes_locais or {}).items():
            builder = builder.config(chave, valor)
    return builder.getOrCreate()
