WITH interacoes AS (
  SELECT conversa_id,
         SUM(CASE WHEN papel = 'user' THEN 1 ELSE 0 END) AS turnos_usuario,
         SUM(CASE WHEN papel = 'assistant' THEN 1 ELSE 0 END) AS turnos_bot,
         MAX(CASE WHEN texto RLIKE '(?i)atendente|humano|protocolo' THEN 1 ELSE 0 END) AS escalou
  FROM conversas_dev.silver.turnos GROUP BY conversa_id
)
SELECT COUNT(*) AS conversas,
       SUM(CASE WHEN escalou = 0 AND turnos_bot > 0 THEN 1 ELSE 0 END) AS contidas,
       ROUND(SUM(CASE WHEN escalou = 0 AND turnos_bot > 0 THEN 1 ELSE 0 END) /
             NULLIF(COUNT(*), 0), 4) AS taxa_contencao
FROM interacoes;
