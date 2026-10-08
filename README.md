# Case Dados & Analytics | Diagnóstico de Performance em Venda Direta

## Sobre o projeto

Este repositório apresenta a reconstrução técnica, para portfólio, de um case de Dados & Analytics voltado ao diagnóstico de performance de um canal de Venda Direta.

O trabalho foi estruturado para transformar diferentes fontes operacionais em uma visão analítica capaz de acompanhar a performance do canal e aprofundar a análise do ciclo 2025-16.

> **Nota de confidencialidade:** os dados, acessos e ambientes utilizados no processo seletivo original eram corporativos e não são disponibilizados neste repositório. A publicação para portfólio preserva a lógica analítica, a estrutura de modelagem e o storytelling, sem expor informações proprietárias.

## Pergunta de negócio

**Como transformar diferentes fontes do canal em uma visão confiável de performance para apoiar o diagnóstico e a tomada de decisão?**

## Escopo da análise

O case trabalha com cinco fontes principais:

- `TB_PEDIDOS` — pedidos, GMV e volume
- `TB_BASE` — base e movimentação das revendedoras
- `TB_MATERIAIS` — SKU, marca e categoria
- `TB_CADASTRO` — informações cadastrais da revendedora
- `TB_ORÇAMENTO` — planejamento por ciclo, KPI e marca

A principal unidade temporal da análise é o **ciclo comercial**.

## Pipeline

FONTES
   ↓
AUDITORIA
   ↓
TRATAMENTO
   ↓
REGRAS DE NEGÓCIO
   ↓
MODELAGEM
   ↓
REALIZADO × ORÇADO
   ↓
DASHBOARD
