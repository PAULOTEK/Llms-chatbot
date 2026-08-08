# Governança e LGPD

## Base legal e finalidade

O tratamento deve ser vinculado à finalidade de atendimento, melhoria de
serviço ou execução contratual definida pelo controlador. A base legal deve
ser confirmada pelo jurídico e registrada no catálogo antes de promover dados
para Silver/Gold. Dados não necessários à finalidade são descartados.

## Dados sensíveis e anonimização

CPF, CNPJ, e-mail, telefone, cartão e nomes identificáveis são detectados na
camada Silver. A anonimização substitui o valor por placeholder derivado de
hash com salt secreto. A pseudonimização determinística permite deduplicação,
mas não elimina o caráter pessoal: salt, acesso e reversibilidade operacional
devem ser protegidos. Datasets IA exigem ausência de PII residual.

Em Unity Catalog Serverless, o pipeline usa `lgpd.anonimizacao_modo: nativo`
para evitar Python UDFs não suportadas. O modo nativo extrai cada ocorrência,
calcula `sha2(salt || valor)` e substitui todas as ocorrências pelo token
`[TIPO_<hash>]`. O modo `python` permanece disponível para testes locais e
mantém a mesma regra determinística; não há seleção implícita por variável de
ambiente.

## Retenção e direitos

Defina retenção por finalidade, com expurgo periódico de Bronze e quarentena.
Atenda solicitações de acesso, correção, eliminação, oposição e portabilidade
por processo controlado, propagando a exclusão a todas as camadas e backups.

## Controles

Unity Catalog aplica permissões por grupo, tags de classificação, auditoria e
linhagem. Segredos ficam em secret scopes/variáveis protegidas; nunca em YAML,
logs ou notebooks. Qualidade crítica interrompe a publicação Gold.
