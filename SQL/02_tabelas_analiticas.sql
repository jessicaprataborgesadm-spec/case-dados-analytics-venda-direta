-- 02_tabelas_analiticas.sql | BigQuery Standard SQL
-- Substitua `SEU_PROJETO.SEUDATASET` pelo projeto.dataset do seu ambiente.
-- As fontes RAW desta versão são sintéticas.
-- des_marca é lida de raw_materiais, sem lista de marcas fixa no SQL.
-- Marcas da simulação: LUMI, VEL, LUO, NUV e PAM.

-- A. ANALITICO_CICLO | grain: 1 linha por nr_ciclo
CREATE OR REPLACE TABLE `SEU_PROJETO.SEUDATASET.analitico_canal_ciclo` AS
WITH ciclos AS (
  SELECT nr_ciclo FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`
  UNION DISTINCT
  SELECT nr_ciclo FROM `SEU_PROJETO.SEUDATASET.raw_base`
),
pedidos_ciclo AS (
  SELECT nr_ciclo,
    SUM(SAFE_CAST(vlr_gmv AS NUMERIC)) AS gmv,
    SUM(SAFE_CAST(vlr_volume AS NUMERIC)) AS volume,
    COUNT(DISTINCT cod_rev) AS ativas
  FROM `SEU_PROJETO.SEUDATASET.raw_pedidos`
  GROUP BY nr_ciclo
),
base_ciclo AS (
  SELECT nr_ciclo,
    SUM(CAST(flg_base AS INT64)) AS base,
    SUM(CAST(flg_base_ativa AS INT64)) AS base_ativa,
    SUM(CAST(flg_inicio AS INT64)) AS inicio,
    SUM(CAST(flg_reinicio AS INT64)) AS reinicio,
    SUM(CAST(flg_perda AS INT64)) AS perda
  FROM `SEU_PROJETO.SEUDATASET.raw_base`
  GROUP BY nr_ciclo
),
metricas AS (
  SELECT c.nr_ciclo,
    COALESCE(p.gmv, CAST(0 AS NUMERIC)) AS gmv,
    COALESCE(p.volume, CAST(0 AS NUMERIC)) AS volume,
    COALESCE(p.ativas, 0) AS ativas,
    COALESCE(b.base, 0) AS base,
    COALESCE(b.base_ativa, 0) AS base_ativa,
    COALESCE(b.inicio, 0) AS inicio,
    COALESCE(b.reinicio, 0) AS reinicio,
    COALESCE(b.perda, 0) AS perda
  FROM ciclos c
  LEFT JOIN pedidos_ciclo p USING (nr_ciclo)
  LEFT JOIN base_ciclo b USING (nr_ciclo)
)
SELECT nr_ciclo, gmv, volume, ativas, base, base_ativa, inicio, reinicio, perda,
  SAFE_DIVIDE(ativas, base) AS atividade,
  SAFE_DIVIDE(ativas - inicio - reinicio, base_ativa) AS atividade_base_ativa,
  SAFE_DIVIDE(gmv, ativas) AS rpa,
  SAFE_DIVIDE(volume, ativas) AS upa
FROM metricas;

-- B. ANALITICO_MARCA_CICLO | grain: ciclo + marca
-- Penetração = compradores distintos da marca / ativas totais do canal.
-- O nome da marca vem de raw_materiais.des_marca e acompanha as marcas fictícias vigentes.
CREATE OR REPLACE TABLE `SEU_PROJETO.SEUDATASET.analitico_marca_ciclo` AS
WITH marca AS (
  SELECT p.nr_ciclo, m.des_marca,
    SUM(SAFE_CAST(p.vlr_gmv AS NUMERIC)) AS gmv,
    SUM(SAFE_CAST(p.vlr_volume AS NUMERIC)) AS volume,
    COUNT(DISTINCT p.cod_pedido) AS pedidos,
    COUNT(DISTINCT p.cod_rev) AS compradores
  FROM `SEU_PROJETO.SEUDATASET.raw_pedidos` p
  INNER JOIN `SEU_PROJETO.SEUDATASET.raw_materiais` m ON p.cod_sku = m.cod_sku
  GROUP BY p.nr_ciclo, m.des_marca
)
SELECT m.nr_ciclo, m.des_marca, m.gmv, m.volume, m.pedidos, m.compradores,
  SAFE_DIVIDE(m.compradores, c.ativas) AS penetracao_marca,
  SAFE_DIVIDE(m.gmv, m.compradores) AS gmv_por_comprador,
  SAFE_DIVIDE(m.gmv, c.gmv) AS participacao_gmv_canal
FROM marca m
LEFT JOIN `SEU_PROJETO.SEUDATASET.analitico_canal_ciclo` c USING (nr_ciclo);

-- C. ANALITICO_MIX_CICLO | grain: ciclo + marca + categoria
CREATE OR REPLACE TABLE `SEU_PROJETO.SEUDATASET.analitico_mix_ciclo` AS
WITH mix AS (
  SELECT p.nr_ciclo, m.des_marca, m.des_categoria,
    SUM(SAFE_CAST(p.vlr_gmv AS NUMERIC)) AS gmv,
    SUM(SAFE_CAST(p.vlr_volume AS NUMERIC)) AS volume,
    COUNT(DISTINCT p.cod_pedido) AS pedidos,
    COUNT(DISTINCT p.cod_rev) AS compradores
  FROM `SEU_PROJETO.SEUDATASET.raw_pedidos` p
  INNER JOIN `SEU_PROJETO.SEUDATASET.raw_materiais` m ON p.cod_sku = m.cod_sku
  GROUP BY p.nr_ciclo, m.des_marca, m.des_categoria
)
SELECT nr_ciclo, des_marca, des_categoria, gmv, volume, pedidos, compradores,
  SAFE_DIVIDE(gmv, SUM(gmv) OVER (PARTITION BY nr_ciclo, des_marca)) AS participacao_gmv_na_marca,
  SAFE_DIVIDE(gmv, SUM(gmv) OVER (PARTITION BY nr_ciclo)) AS participacao_gmv_no_canal
FROM mix;

-- D. Validação simples pós-criação
SELECT 'analitico_canal_ciclo' AS tabela, COUNT(*) AS linhas, COUNT(DISTINCT nr_ciclo) AS ciclos_distintos
FROM `SEU_PROJETO.SEUDATASET.analitico_canal_ciclo`
UNION ALL
SELECT 'analitico_marca_ciclo', COUNT(*), COUNT(DISTINCT nr_ciclo)
FROM `SEU_PROJETO.SEUDATASET.analitico_marca_ciclo`
UNION ALL
SELECT 'analitico_mix_ciclo', COUNT(*), COUNT(DISTINCT nr_ciclo)
FROM `SEU_PROJETO.SEUDATASET.analitico_mix_ciclo`;

-- Nota: gmv_por_comprador é métrica derivada de demonstração e não substitui o RPA oficial (GMV/Ativas).
-- A simulação de reinício dos CSVs é uma aproximação didática, não uma regra oficial do case original.
