# Dashboard — Streamlit

Web app em Python para explorar a versão sintética do case.

## Fonte dos dados
A app lê CSVs de `../data/` na raiz do repositório. Os cinco arquivos devem existir:
- `raw_pedidos.csv`
- `raw_base.csv`
- `raw_materiais.csv`
- `raw_cadastro.csv`
- `raw_orcamento.csv`

## Rodar localmente

Na raiz do repositório:

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

## Publicar no Streamlit Community Cloud

1. Entre em https://share.streamlit.io/ e conecte ao GitHub.
2. Clique em **Create app**.
3. Escolha o repositório `case-dados-analytics-venda-direta`, branch `main`.
4. Informe `dashboard/app.py` como **Main file path**.
5. O arquivo `dashboard/requirements.txt` instala as dependências.
6. Clique em **Deploy**.

A app lê arquivos CSV públicos do repositório e não usa chaves, tokens ou credenciais do BigQuery. Dessa forma, o dashboard demonstrativo não dispara consultas pagas no BigQuery.

## Observação técnica
Para manter a demonstração independente de credenciais, as agregações visuais são calculadas a partir dos CSVs sintéticos. As consultas SQL equivalentes estão documentadas na pasta `sql/`; em uma próxima iteração, podemos exportar as tabelas analíticas validadas e fazer o dashboard consumir esses resultados, evitando manter lógica duplicada.
