# Dados sintéticos

Esta pasta contém dados inteiramente artificiais para reconstruir a estrutura analítica do projeto em um portfólio público. Os dados, identificadores e valores são simulados e não representam registros corporativos reais.

## Arquivos

- `raw_pedidos.csv`: pedido + revendedora + SKU; GMV, volume e desconto.
- `raw_base.csv`: ciclo + revendedora; flags de base e movimentação.
- `raw_materiais.csv`: SKU, marca fictícia e categoria.
- `raw_cadastro.csv`: cadastro fictício das revendedoras.
- `raw_orcamento.csv`: orçamento sintético por ciclo, KPI e marca.
- `generate_synthetic_data.py`: gerador reproduzível, usando apenas Python padrão.

## Convenções e limitações

- As marcas fictícias são `LUMI`, `VEL`, `LUO`, `NUV` e `PAM`.
- `PAM` representa a marca sem orçamento: ela pode aparecer nos pedidos e na dimensão de materiais, mas não possui linhas na tabela de orçamento.
- O intervalo de sete posições de ciclo usado para simular reinícios é uma aproximação didática desta simulação, não uma regra oficial de negócio.
- Os valores foram configurados para gerar desvios ilustrativos no ciclo `202516`; não representam resultados reais.
- RPA e UPA não são orçados diretamente neste conjunto. Só devem ser derivados quando numerador e denominador usarem escopos compatíveis.

## Regerar os CSVs

Com Python 3 instalado, dentro desta pasta execute:

```bash
python generate_synthetic_data.py
```
