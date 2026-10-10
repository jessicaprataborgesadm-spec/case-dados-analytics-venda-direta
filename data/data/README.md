# Dados sintéticos

Esta pasta contém dados inteiramente artificiais para reconstruir a estrutura analítica do projeto em um portfólio público. Não há dados, identificadores, registros nem valores corporativos originais.

## Arquivos

- `raw_pedidos.csv`: pedido + revendedora + SKU; GMV, volume e desconto.
- `raw_base.csv`: ciclo + revendedora; flags de base e movimentação.
- `raw_materiais.csv`: SKU, marca e categoria.
- `raw_cadastro.csv`: cadastro fictício das revendedoras.
- `raw_orcamento.csv`: orçamento sintético por ciclo, KPI e marca.
- `generate_synthetic_data.py`: gerador reproduzível, usando apenas Python padrão.

## Importante

- `BOT` e `BOTI` são rótulos distintos no conjunto sintético, para demonstrar cuidado com classificações.
- O gerador usa um intervalo de sete posições de ciclo como aproximação didática para simular reinícios. Isso é **uma suposição da simulação**, não uma regra oficial do case.
- Os valores sintéticos do ciclo `202516` foram configurados para gerar desvios ilustrativos. Não representam resultados reais.
- RPA e UPA não são orçados diretamente neste conjunto; só devem ser derivados se numerador e denominador usarem escopos compatíveis.

## Regerar os CSVs

Com Python 3 instalado, dentro desta pasta execute:

```bash
python generate_synthetic_data.py
```
