# Decisões técnicas (ADRs)

## ADR-001 — Delta/Unity Catalog

**Decisão:** usar Delta e Unity Catalog como persistência de produção.
**Motivo:** transações, esquema, governança, tags e linhagem nativas. Testes
locais isolam a escrita Delta para manter baixo custo de execução.

## ADR-002 — Qualidade própria

**Decisão:** implementar expectativas PySpark leves e declarativas em YAML.
**Motivo:** reduzir peso de dependências e manter as regras versionadas junto
ao domínio.

## ADR-003 — Funções puras

**Decisão:** notebooks apenas orquestram; transformações recebem e retornam
DataFrames. **Motivo:** compatibilidade com Serverless/Spark Connect e testes
unitários rápidos.

## ADR-004 — Pseudonimização determinística

**Decisão:** hash com salt secreto por tipo de PII. **Motivo:** preservar a
capacidade de deduplicar sem expor o identificador original; o resultado ainda
é dado pessoal e permanece sob controles LGPD.

## ADR-005 — Normalização Unicode

**Decisão:** aplicar NFKC em um UDF Python isolado e usar expressões Spark para
markup, espaços e lowercase. **Motivo:** Spark não oferece uma expressão
nativa equivalente à normalização Unicode NFKC completa; limitar o UDF à
operação não disponível nativamente reduz o custo de serialização.

## ADR-006 — Kafka com `availableNow`

**Decisão:** consumir Kafka em Structured Streaming com `availableNow` agendado
a cada 15 minutos. **Motivo:** o Serverless processa backlog sem manter compute
contínuo e checkpoints persistentes preservam offsets. A Silver usa `MERGE`
idempotente para tolerar reprocessamento de micro-batches.
