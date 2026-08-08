# Changelog

Todas as alterações relevantes deste projeto são documentadas neste arquivo.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e
o projeto segue [SemVer](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [0.2.3] - 2026-08-08

### Fixed

- Corrige a passagem da versão ao Databricks Bundle usando a opção `--var`.

## [0.2.2] - 2026-08-08

### Fixed

- Aceita `DATABRICKS_HOST` como Variable ou Secret, com diagnóstico seguro de
  credenciais ausentes.
- Adiciona execução manual do job Databricks após o deploy.
- Torna as notas de release resilientes quando uma seção do changelog estiver
  ausente.

## [0.2.1] - 2026-08-06

### Fixed

- Gates de credenciais Databricks nos workflows: o contexto `secrets` não é
  avaliável em `if:` de job, o que invalidava `ci.yml` e `cd.yml`.

## [0.2.0] - 2026-08-06

### Added

- Streaming near real-time com Kafka KRaft e Spark Structured Streaming.
- Bronze Kafka com checkpoints, watermark e metadados de offsets.
- Silver `foreachBatch` com MERGE Delta idempotente.
- Produtor sintético local e DAG de consumo `availableNow`.
- Versionamento SemVer, changelog, rastreabilidade de runtime e release
  automático com wheel.

## [0.1.0] - 2026-08-06

### Added

- Lakehouse conversacional batch em arquitetura Bronze/Silver/Gold.
- Ingestão via API REST, JDBC e JSONL.
- Normalização de texto, deduplicação, anonimização LGPD e qualidade declarativa.
- Datasets Gold para BI, SFT e avaliação de LLM.
- Notebooks Databricks, Asset Bundle, Airflow, SQL analítico e CI/CD.
