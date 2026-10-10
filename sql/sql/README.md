# SQL | Case Dados & Analytics

Scripts em BigQuery Standard SQL para a versão de portfólio com dados sintéticos.

## Ordem de execução

1. `01_auditoria_fontes.sql` — contagens, nulos, duplicidades, integridade referencial e domínios.
2. `02_tabelas_analiticas.sql` — cria `analitico_canal_ciclo`, `analitico_marca_ciclo` e `analitico_mix_ciclo`.
3. `03_realizado_x_orcado.sql` — cria a comparação entre realizado e orçado.

## Preparar o BigQuery

1. Crie um dataset para o projeto de portfólio.
2. Carregue os CSVs sintéticos da pasta `data/` como tabelas `raw_pedidos`, `raw_base`, `raw_materiais`, `raw_cadastro` e `raw_orcamento`.
3. Em cada script, substitua `SEU_PROJETO.SEUDATASET` pelo seu ID de projeto e nome do dataset.
4. Execute os scripts na ordem acima.

## Premissas de modelagem

- Todos os dados usados nesta versão são sintéticos.
- `analitico_canal_ciclo`: 1 linha por ciclo.
- `analitico_marca_ciclo`: 1 linha por ciclo + marca.
- `analitico_mix_ciclo`: 1 linha por ciclo + marca + categoria.
- `realizado_x_orcado_ciclo`: 1 linha por ciclo + KPI + marca.
- Penetração da marca = compradores distintos da marca / ativas totais do canal.
- `gmv_por_comprador` é uma métrica derivada demonstrativa, não substitui a definição de RPA do case.
- A simulação de reinício nos dados sintéticos é uma aproximação didática e não uma regra oficial do case original.
- RPA e UPA não possuem orçamento direto; não invente orçamento ausente nem compare escopos incompatíveis.
