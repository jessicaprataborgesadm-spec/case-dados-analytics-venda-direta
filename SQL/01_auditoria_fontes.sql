-- 01_auditoria_fontes.sql | BigQuery Standard SQL
-- Substitua `SEU_PROJETO.SEUDATASET` pelo projeto.dataset do seu ambiente.
-- Consultas para auditar CSVs SINTÉTICOS já carregados como tabelas RAW.

-- 1. Contagem de linhas por fonte
SELECT 'raw_pedidos' AS tabela, COUNT(*) AS linhas FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`
UNION ALL SELECT 'raw_base', COUNT(*) FROM `SEU_PROJETO.SEUDATASET.raw_base`
UNION ALL SELECT 'raw_materiais', COUNT(*) FROM `SEU_PROJETO.SEUDATASET.raw_materiais`
UNION ALL SELECT 'raw_cadastro', COUNT(*) FROM `SEU_PROJETO.SEUDATASET.raw_cadastro`
UNION ALL SELECT 'raw_orcamento', COUNT(*) FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`
ORDER BY tabela;

-- 2. Completude de campos-chave
SELECT 'raw_pedidos' AS tabela,
  COUNTIF(nr_ciclo IS NULL) AS nr_ciclo_nulo,
  COUNTIF(cod_pedido IS NULL OR TRIM(cod_pedido) = '') AS pedido_vazio,
  COUNTIF(cod_rev IS NULL OR TRIM(cod_rev) = '') AS revendedora_vazia,
  COUNTIF(cod_sku IS NULL OR TRIM(cod_sku) = '') AS sku_vazio,
  COUNTIF(dt_pedido IS NULL) AS data_nula
FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`
UNION ALL
SELECT 'raw_base', COUNTIF(nr_ciclo IS NULL), 0,
  COUNTIF(cod_rev IS NULL OR TRIM(cod_rev) = ''), 0, 0
FROM `SEU_PROJETO.SEUDATASET.raw_base`
UNION ALL
SELECT 'raw_materiais', 0, 0, 0,
  COUNTIF(cod_sku IS NULL OR TRIM(cod_sku) = ''), 0
FROM `SEU_PROJETO.SEUDATASET.raw_materiais`
UNION ALL
SELECT 'raw_cadastro', 0, 0,
  COUNTIF(cod_pessoa IS NULL OR TRIM(cod_pessoa) = ''), 0, 0
FROM `SEU_PROJETO.SEUDATASET.raw_cadastro`
UNION ALL
SELECT 'raw_orcamento', COUNTIF(nr_ciclo IS NULL), 0, 0, 0, 0
FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`;

-- 3. Duplicidades no grain esperado
SELECT 'raw_pedidos' AS tabela,
  COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(nr_ciclo, cod_pedido, cod_rev, cod_sku))) AS duplicatas_grain
FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`
UNION ALL
SELECT 'raw_base', COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(nr_ciclo, cod_rev)))
FROM `SEU_PROJETO.SEUDATASET.raw_base`
UNION ALL
SELECT 'raw_materiais', COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(cod_sku)))
FROM `SEU_PROJETO.SEUDATASET.raw_materiais`
UNION ALL
SELECT 'raw_cadastro', COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(cod_pessoa)))
FROM `SEU_PROJETO.SEUDATASET.raw_cadastro`
UNION ALL
SELECT 'raw_orcamento', COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(nr_ciclo, des_kpi, des_marca)))
FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`;

-- 4. Integridade referencial
SELECT 'pedidos_sem_cadastro' AS verificacao, COUNT(*) AS registros
FROM `SEU_PROJETO.SEUDATASET.raw_pedidos` p
LEFT JOIN `SEU_PROJETO.SEUDATASET.raw_cadastro` c ON p.cod_rev = c.cod_pessoa
WHERE c.cod_pessoa IS NULL
UNION ALL
SELECT 'pedidos_sem_material', COUNT(*)
FROM `SEU_PROJETO.SEUDATASET.raw_pedidos` p
LEFT JOIN `SEU_PROJETO.SEUDATASET.raw_materiais` m ON p.cod_sku = m.cod_sku
WHERE m.cod_sku IS NULL
UNION ALL
SELECT 'base_sem_cadastro', COUNT(*)
FROM `SEU_PROJETO.SEUDATASET.raw_base` b
LEFT JOIN `SEU_PROJETO.SEUDATASET.raw_cadastro` c ON b.cod_rev = c.cod_pessoa
WHERE c.cod_pessoa IS NULL;

-- 5. Flags fora do domínio esperado {0,1}
SELECT
  COUNTIF(flg_base NOT IN (0,1) OR flg_base IS NULL) AS flag_base_fora_dominio,
  COUNTIF(flg_base_ativa NOT IN (0,1) OR flg_base_ativa IS NULL) AS flag_base_ativa_fora_dominio,
  COUNTIF(flg_inicio NOT IN (0,1) OR flg_inicio IS NULL) AS flag_inicio_fora_dominio,
  COUNTIF(flg_reinicio NOT IN (0,1) OR flg_reinicio IS NULL) AS flag_reinicio_fora_dominio,
  COUNTIF(flg_perda NOT IN (0,1) OR flg_perda IS NULL) AS flag_perda_fora_dominio
FROM `SEU_PROJETO.SEUDATASET.raw_base`;

-- 6. Valores não numéricos/negativos e descontos acima do GMV
SELECT
  COUNTIF(SAFE_CAST(vlr_gmv AS NUMERIC) IS NULL) AS gmv_nao_numerico,
  COUNTIF(SAFE_CAST(vlr_volume AS NUMERIC) IS NULL) AS volume_nao_numerico,
  COUNTIF(SAFE_CAST(vlr_desconto AS NUMERIC) IS NULL) AS desconto_nao_numerico,
  COUNTIF(SAFE_CAST(vlr_gmv AS NUMERIC) < 0) AS gmv_negativo,
  COUNTIF(SAFE_CAST(vlr_volume AS NUMERIC) < 0) AS volume_negativo,
  COUNTIF(SAFE_CAST(vlr_desconto AS NUMERIC) > SAFE_CAST(vlr_gmv AS NUMERIC)) AS desconto_maior_que_gmv
FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`;

-- Desconto maior que GMV é um alerta de investigação, não uma regra automática de exclusão.

-- 7. Conferência do domínio de marcas por fonte.
-- Materiais: LUMI, VEL, LUO, NUV e PAM. Orçamento: LUMI, VEL, LUO e NUV,
-- além do rótulo 'total' para KPIs de canal. PAM deve permanecer sem orçamento.
SELECT 'materiais' AS fonte, UPPER(TRIM(des_marca)) AS marca, COUNT(*) AS registros
FROM `SEU_PROJETO.SEUDATASET.raw_materiais`
GROUP BY 1, 2
UNION ALL
SELECT 'orcamento' AS fonte, UPPER(TRIM(des_marca)) AS marca, COUNT(*) AS registros
FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`
GROUP BY 1, 2
ORDER BY fonte, marca;

-- 8. Checagem específica de rótulos inesperados no orçamento.
-- Resultado esperado: linhas_orcamento_pam = 0 e linhas_marca_fora_padrao = 0.
SELECT
  COUNTIF(UPPER(TRIM(des_marca)) = 'PAM') AS linhas_orcamento_pam,
  COUNTIF(des_marca IS NULL OR UPPER(TRIM(des_marca)) NOT IN ('LUMI', 'VEL', 'LUO', 'NUV', 'TOTAL')) AS linhas_marca_fora_padrao
FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`;
