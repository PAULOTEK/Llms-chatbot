# Changelog

Todas as alterações relevantes deste projeto são documentadas neste arquivo.
O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e
o projeto segue [SemVer](https://semver.org/lang/pt-BR/).

## [Unreleased]

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
