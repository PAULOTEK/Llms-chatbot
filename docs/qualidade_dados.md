# Qualidade de dados

As regras são declarativas em `config/qualidade/regras_*.yml` e executadas por
`conversas_ia.qualidade.executor`, sem dependência de Great Expectations.
Há expectativas de nulos, domínio, regex, ranges e unicidade. Cada execução
gera contagens por regra, severidade e status na tabela
`governanca.qualidade_execucoes`.

Falhas críticas são encaminhadas à Silver quarantine e bloqueiam a sequência
Gold. Falhas não críticas são reportadas para acompanhamento. O `run_id`,
volume de entrada/saída e `git_sha` permitem reproduzir e auditar cada lote.
