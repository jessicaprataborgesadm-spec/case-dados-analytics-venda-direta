
# SQL | Case Dados & Analytics

Esta pasta contém as consultas SQL utilizadas na reconstrução técnica do case de Dados & Analytics para portfólio.

Os scripts foram preparados para **BigQuery Standard SQL** e utilizam exclusivamente as fontes sintéticas disponíveis na pasta `data/`.

## Scripts

### `01_auditoria_fontes.sql`
Executa verificações de qualidade: volume de registros, valores nulos, duplicidades, integridade referencial e validações de domínio.

### `02_tabelas_analiticas.sql`
Constrói três camadas analíticas:

- `analitico_ciclo`: uma linha por ciclo.
- `analitico_marca_ciclo`: uma linha por ciclo e marca.
- `analitico_mix_ciclo`: uma linha por ciclo, marca e categoria.

### `03_realizado_x_orcado.sql`
Compara realizado e orçado por ciclo, KPI e marca, calculando diferenças e atingimento percentual.

## Ordem de execução

1. Executar `01_auditoria_fontes.sql`.
2. Executar `02_tabelas_analiticas.sql`.
3. Executar `03_realizado_x_orcado.sql`.

Antes da execução, é necessário carregar os CSVs como tabelas no BigQuery e substituir `SEU_PROJETO.SEUDATASET` pelo identificador real do projeto e dataset.

## Cuidados analíticos

- Preservar a granularidade de cada fonte.
- Evitar duplicações ao integrar tabelas.
- Manter `BOT` e `BOTI` separados quando não existir regra documentada de equivalência.
- Não comparar realizado e orçamento com escopos incompatíveis.
- Não tratar premissas dos dados sintéticos como regras oficiais do case original.

**Nota:** os dados deste repositório são sintéticos e destinados exclusivamente à demonstração técnica.
