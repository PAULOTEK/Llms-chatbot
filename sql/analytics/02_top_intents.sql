WITH classificadas AS (
  SELECT conversa_id, canal, DATE(inicio) AS dia,
         CASE
           WHEN LOWER(prompt) RLIKE 'pagamento|boleto|cobrança' THEN 'pagamento'
           WHEN LOWER(prompt) RLIKE 'senha|acesso|login' THEN 'acesso'
           WHEN LOWER(prompt) RLIKE 'entrega|pedido|rastreamento' THEN 'pedido'
           ELSE 'outros'
         END AS intent
  FROM conversas_dev.gold.dataset_sft
  JOIN conversas_dev.gold.fato_conversa USING (conversa_id)
),
ranking AS (
  SELECT dia, intent, COUNT(*) AS volume,
         DENSE_RANK() OVER (PARTITION BY dia ORDER BY COUNT(*) DESC) AS posicao
  FROM classificadas GROUP BY dia, intent
)
SELECT * FROM ranking WHERE posicao <= 10 ORDER BY dia, posicao;
