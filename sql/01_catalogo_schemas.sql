CREATE CATALOG IF NOT EXISTS __CATALOG__ COMMENT 'Lakehouse conversacional para dados de IA';
CREATE SCHEMA IF NOT EXISTS __CATALOG__.bronze COMMENT 'Dados brutos append-only';
CREATE SCHEMA IF NOT EXISTS __CATALOG__.silver COMMENT 'Dados normalizados e anonimizados';
CREATE SCHEMA IF NOT EXISTS __CATALOG__.gold COMMENT 'Produtos analíticos e datasets de IA';
CREATE SCHEMA IF NOT EXISTS __CATALOG__.governanca COMMENT 'Qualidade, linhagem e auditoria';
CREATE VOLUME IF NOT EXISTS __CATALOG__.bronze.landing;
CREATE VOLUME IF NOT EXISTS __CATALOG__.bronze.checkpoints;

COMMENT ON TABLE __CATALOG__.gold.fato_conversa IS 'Métricas agregadas por conversa';
COMMENT ON COLUMN __CATALOG__.gold.fato_conversa.conversa_id IS 'Identificador técnico sem PII';
COMMENT ON TABLE __CATALOG__.gold.dataset_sft IS 'Pares instruction-tuning filtrados e anonimizados';
ALTER TABLE __CATALOG__.silver.turnos SET TAGS ('classificacao' = 'conversacional');
ALTER TABLE __CATALOG__.silver.turnos ALTER COLUMN texto SET TAGS ('pii' = 'anonimizado');
GRANT USE CATALOG ON CATALOG __CATALOG__ TO `grupo-engenharia-dados`;
GRANT USE SCHEMA ON SCHEMA __CATALOG__.gold TO `grupo-engenharia-dados`;
GRANT SELECT ON SCHEMA __CATALOG__.gold TO `grupo-analytics`;
