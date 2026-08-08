WITH normalizado AS (
  SELECT conversa_id, turno_id, texto,
         LAG(texto) OVER (PARTITION BY idioma ORDER BY _conteudo_hash) AS texto_anterior,
         LAG(_conteudo_hash) OVER (PARTITION BY idioma ORDER BY _conteudo_hash) AS hash_anterior
  FROM workspace.silver.turnos
  WHERE texto IS NOT NULL
),
marcados AS (
  SELECT *, CASE WHEN levenshtein(texto, texto_anterior) <= 5 THEN 1 ELSE 0 END AS near_duplicate
  FROM normalizado WHERE hash_anterior IS NOT NULL
)
SELECT idioma, COUNT(*) AS comparacoes, SUM(near_duplicate) AS pares_proximos,
       ROUND(SUM(near_duplicate) / NULLIF(COUNT(*), 0), 4) AS taxa_near_duplicate
FROM marcados GROUP BY idioma ORDER BY taxa_near_duplicate DESC;
