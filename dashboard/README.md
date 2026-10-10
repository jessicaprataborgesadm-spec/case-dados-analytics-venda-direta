# Dashboard | Performance em Venda Direta

Aplicação interativa de portfólio desenvolvida com **Python, Streamlit, Pandas e Plotly** para explorar um cenário sintético de performance em venda direta.

> **Aviso:** todos os dados, identificadores, marcas e valores desta aplicação são fictícios. O cenário é demonstrativo e não representa resultados reais de nenhuma empresa.

## O que o dashboard explora

A aplicação está organizada em cinco páginas:

1. **Visão geral:** indicadores principais e evolução por ciclo.
2. **Conciliação do GMV:** comparação entre GMV total do canal, GMV das marcas orçadas e orçamento dessas marcas.
3. **Diagnóstico do ciclo:** indicadores do ciclo selecionado.
4. **Produtividade:** métricas de produção e atividade.
5. **Mix de produtos:** composição por marca e categoria.

## Marcas fictícias

- `LUMI` — possui orçamento sintético.
- `VEL` — possui orçamento sintético.
- `LUO` — possui orçamento sintético.
- `NUV` — possui orçamento sintético.
- `PAM` — não possui orçamento sintético; pode aparecer no realizado.

A comparação entre realizado e orçado respeita o escopo do orçamento. A ausência de orçamento para `PAM` não é preenchida com um valor artificial.

## Fonte de dados

A aplicação lê os arquivos CSV da pasta `../data/` na raiz do repositório:

- `raw_pedidos.csv`
- `raw_base.csv`
- `raw_materiais.csv`
- `raw_cadastro.csv`
- `raw_orcamento.csv`

O dashboard atual calcula as visualizações a partir desses CSVs sintéticos. Não exige credenciais do BigQuery nem executa consultas pagas para carregar as páginas.

## Executar localmente

A partir da raiz do repositório, execute:

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## Publicar no Streamlit Community Cloud

1. Acesse https://share.streamlit.io/ e conecte ao GitHub.
2. Crie ou abra a aplicação vinculada a este repositório.
3. Selecione a branch `main`.
4. Defina `dashboard/app.py` como **Main file path**.
5. Confirme que as dependências estão em `dashboard/requirements.txt`.

## Relação com os scripts SQL

Os scripts em [`SQL/`](../SQL/) documentam uma camada analítica separada em BigQuery Standard SQL: auditoria das fontes, criação de tabelas analíticas e comparação entre realizado e orçado. Nesta versão, o dashboard **não consome tabelas materializadas no BigQuery**; ele lê diretamente os CSVs sintéticos. Portanto, não há integração em tempo de execução entre a aplicação e as tabelas SQL.

## Limitações da simulação

- Os valores e identificadores são gerados artificialmente.
- A regra demonstrativa de reinício usa uma aproximação de sete posições de ciclo sem compra; não é uma regra oficial de negócio.
- `PAM` não possui orçamento sintético.
- RPA e UPA não possuem orçamento direto. Não se deve comparar valores de escopos incompatíveis.
