WITH etapas AS (
  SELECT conversa_id,
         MAX(CASE WHEN papel = 'user' THEN 1 ELSE 0 END) AS iniciou,
         MAX(CASE WHEN papel = 'assistant' THEN 1 ELSE 0 END) AS recebeu_resposta,
         MAX(CASE WHEN papel = 'assistant' AND resolvida THEN 1 ELSE 0 END) AS resolveu
  FROM conversas_dev.silver.turnos
  GROUP BY conversa_id
)
SELECT COUNT(*) AS conversas,
       SUM(iniciou) AS iniciadas,
       SUM(recebeu_resposta) AS com_resposta,
       SUM(resolveu) AS resolvidas,
       ROUND(SUM(recebeu_resposta) / NULLIF(SUM(iniciou), 0), 4) AS taxa_resposta,
       ROUND(SUM(resolveu) / NULLIF(SUM(iniciou), 0), 4) AS taxa_resolucao
FROM etapas;
