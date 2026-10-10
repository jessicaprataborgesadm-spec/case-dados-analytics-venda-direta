-- 03_realizado_x_orcado.sql | BigQuery Standard SQL
-- Substitua `SEU_PROJETO.SEUDATASET` pelo projeto.dataset do seu ambiente.
-- Requer analitico_canal_ciclo, analitico_marca_ciclo e raw_orcamento.

CREATE OR REPLACE TABLE `SEU_PROJETO.SEUDATASET.realizado_x_orcado_ciclo` AS
WITH realizado_canal AS (
  SELECT nr_ciclo, kpi.des_kpi, kpi.des_marca, kpi.realizado
  FROM `SEU_PROJETO.SEUDATASET.analitico_canal_ciclo`
  CROSS JOIN UNNEST([
    STRUCT('base' AS des_kpi, 'total' AS des_marca, CAST(base AS NUMERIC) AS realizado),
    STRUCT('base_ativa' AS des_kpi, 'total' AS des_marca, CAST(base_ativa AS NUMERIC) AS realizado),
    STRUCT('ativas' AS des_kpi, 'total' AS des_marca, CAST(ativas AS NUMERIC) AS realizado),
    STRUCT('inicio' AS des_kpi, 'total' AS des_marca, CAST(inicio AS NUMERIC) AS realizado),
    STRUCT('reinicio' AS des_kpi, 'total' AS des_marca, CAST(reinicio AS NUMERIC) AS realizado),
    STRUCT('perda' AS des_kpi, 'total' AS des_marca, CAST(perda AS NUMERIC) AS realizado)
  ]) AS kpi
),
realizado_marca AS (
  SELECT nr_ciclo, kpi.des_kpi, des_marca, kpi.realizado
  FROM `SEU_PROJETO.SEUDATASET.analitico_marca_ciclo`
  CROSS JOIN UNNEST([
    STRUCT('gmv' AS des_kpi, CAST(gmv AS NUMERIC) AS realizado),
    STRUCT('compradores' AS des_kpi, CAST(compradores AS NUMERIC) AS realizado)
  ]) AS kpi
),
realizado AS (
  SELECT * FROM realizado_canal
  UNION ALL
  SELECT * FROM realizado_marca
),
orcado AS (
  SELECT nr_ciclo, LOWER(TRIM(des_kpi)) AS des_kpi,
    LOWER(TRIM(des_marca)) AS des_marca,
    SAFE_CAST(vlr_kpi AS NUMERIC) AS orcado
  FROM `SEU_PROJETO.SEUDATASET.raw_orcamento`
),
comparacao AS (
  SELECT r.nr_ciclo, r.des_kpi, r.des_marca, r.realizado, o.orcado
  FROM realizado r
  INNER JOIN orcado o
    ON r.nr_ciclo = o.nr_ciclo
   AND LOWER(TRIM(r.des_kpi)) = o.des_kpi
   AND LOWER(TRIM(r.des_marca)) = o.des_marca
)
SELECT nr_ciclo, des_kpi, des_marca, realizado, orcado,
  realizado - orcado AS diferenca_absoluta,
  SAFE_DIVIDE(realizado - orcado, orcado) AS diferenca_percentual,
  SAFE_DIVIDE(realizado, orcado) AS atingimento_percentual
FROM comparacao;

-- Inspecione o ciclo sintético 202516
SELECT *
FROM `SEU_PROJETO.SEUDATASET.realizado_x_orcado_ciclo`
WHERE nr_ciclo = 202516
ORDER BY CASE des_marca WHEN 'total' THEN 0 ELSE 1 END, des_kpi, des_marca;

-- Importante: esta simulação não inclui orçamento direto de RPA ou UPA.
-- Não compare GMV total do canal contra orçamento definido apenas por marcas.
-- Só derive RPA orçado se GMV e Ativas estiverem em escopos compatíveis.
