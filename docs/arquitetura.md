# Arquitetura

O pipeline implementa Bronze/Silver/Gold no domínio de conversas. Bronze
preserva payloads e metadados de ingestão; Silver produz uma linha por turno,
normaliza Unicode, deduplica e anonimiza; Gold publica métricas para BI e
datasets para instruction-tuning e avaliação.

O Databricks Asset Bundle executa cinco notebooks Serverless em sequência. O
Airflow é uma camada de orquestração externa, útil para validar fontes,
integrar calendários corporativos e disparar o job Databricks. Toda regra de
transformação reside em funções do pacote para ser testada fora do notebook.

As escritas Delta ficam isoladas nas entradas dos notebooks e nos adaptadores
de ingestão; os testes usam apenas DataFrames Spark.
