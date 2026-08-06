CREATE CATALOG IF NOT EXISTS conversas_dev COMMENT 'Lakehouse conversacional para dados de IA';
CREATE SCHEMA IF NOT EXISTS conversas_dev.bronze COMMENT 'Dados brutos append-only';
CREATE SCHEMA IF NOT EXISTS conversas_dev.silver COMMENT 'Dados normalizados e anonimizados';
CREATE SCHEMA IF NOT EXISTS conversas_dev.gold COMMENT 'Produtos analíticos e datasets de IA';
CREATE SCHEMA IF NOT EXISTS conversas_dev.governanca COMMENT 'Qualidade, linhagem e auditoria';
CREATE VOLUME IF NOT EXISTS conversas_dev.bronze.landing;
CREATE VOLUME IF NOT EXISTS conversas_dev.bronze.checkpoints;

COMMENT ON TABLE conversas_dev.gold.fato_conversa IS 'Métricas agregadas por conversa';
COMMENT ON COLUMN conversas_dev.gold.fato_conversa.conversa_id IS 'Identificador técnico sem PII';
COMMENT ON TABLE conversas_dev.gold.dataset_sft IS 'Pares instruction-tuning filtrados e anonimizados';
ALTER TABLE conversas_dev.silver.turnos SET TAGS ('classificacao' = 'conversacional');
ALTER TABLE conversas_dev.silver.turnos ALTER COLUMN texto SET TAGS ('pii' = 'anonimizado');
GRANT USE CATALOG ON CATALOG conversas_dev TO `grupo-engenharia-dados`;
GRANT USE SCHEMA ON SCHEMA conversas_dev.gold TO `grupo-engenharia-dados`;
GRANT SELECT ON SCHEMA conversas_dev.gold TO `grupo-analytics`;
