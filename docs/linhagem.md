# Linhagem e governança

O domínio `conversas` usa arquitetura medalhão em Delta Lake, com tabelas
registradas no Unity Catalog:

```text
API REST ─┐
JDBC ─────┼─> Bronze (raw + metadados) -> Silver (turnos tratados) -> Gold
JSONL ────┘                                      ├─ fato_conversa / dimensões BI
                                                 └─ dataset_sft / dataset_avaliacao
```

Cada etapa recebe `run_id` e registra em `qualidade_execucoes` e na estrutura
de linhagem o job, camada, tabela, volume processado, timestamps e `git_sha`.
O campo `_hash_linha` permite idempotência e auditoria do registro original.

O DAG Airflow valida as fontes antes do job Databricks e o Asset Bundle encadeia
as cinco tarefas. Assim, a linhagem operacional é: landing/API/JDBC → Bronze →
Silver → qualidade/quarentena → Gold BI/IA.

## Classificação LGPD

As colunas de texto são classificadas com tag `pii_detectada` na camada Silver.
CPF, CNPJ, e-mail, telefone e cartão são substituídos por pseudônimos
determinísticos derivados de salt configurável. O salt deve ser fornecido pelo
segredo `CONVERSAS_PII_SALT`, nunca versionado no repositório.

Em Databricks, a publicação aplica comentários e tags de Unity Catalog:

```sql
COMMENT ON TABLE gold.dataset_sft IS 'Pares instruction-tuning sem PII residual';
ALTER TABLE silver.turnos SET TAGS ('classificacao' = 'dados_conversacionais');
ALTER TABLE silver.turnos ALTER COLUMN texto SET TAGS ('contém_pii' = 'anonimizado');
```
