# Data | Fontes sintéticas

Esta pasta contém as fontes de dados artificiais criadas para reconstruir a estrutura analítica do projeto de portfólio.

**Nenhum dado corporativo original é disponibilizado neste repositório.**

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `raw_pedidos.csv` | Pedidos, revendedoras, SKUs, GMV, volume e descontos |
| `raw_base.csv` | Base e movimentação das revendedoras por ciclo |
| `raw_materiais.csv` | SKU, marca e categoria |
| `raw_cadastro.csv` | Dados cadastrais fictícios |
| `raw_orcamento.csv` | Orçamento sintético por ciclo, KPI e marca |
| `generate_synthetic_data.py` | Script para regenerar as fontes |

## Granularidade

- **Pedidos:** pedido + revendedora + SKU.
- **Base:** ciclo + revendedora.
- **Materiais:** SKU.
- **Cadastro:** revendedora.
- **Orçamento:** ciclo + KPI + marca.

## Reprodutibilidade

Os dados foram gerados artificialmente para permitir testes de auditoria, consultas SQL, modelagem e desenvolvimento de dashboard.

O script `generate_synthetic_data.py` utiliza uma semente fixa para tornar a geração reproduzível. Algumas regras da simulação são aproximações demonstrativas e não devem ser consideradas regras oficiais do case original.

## Próxima etapa

Carregar os CSVs no BigQuery, executar as auditorias e construir as tabelas analíticas para alimentar o dashboard desenvolvido em Google Apps Script.
