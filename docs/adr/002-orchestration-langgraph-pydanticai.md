# ADR 002: Orchestration with LangGraph and Pydantic AI

## Contexto
O fluxo de agendamento não é linear. O cliente pode mudar de ideia, perguntar sobre preços no meio da escolha de horários, ou pedir para falar com um humano.

## Decisão
Utilizar o **LangGraph** para a orquestração do grafo de estado da conversa e **Pydantic AI** para a execução de micro-agentes determinísticos que utilizam Tools.

## Status
Aceito.

## Consequências
- **Prós:**
  - Controle granular sobre os nós do grafo (Saudação -> Coleta de Info -> Agendamento).
  - Persistência de estado facilitada (checkpointers) para retomar conversas.
  - Tipagem forte e validação de dados via Pydantic.
- **Contras:**
  - Curva de aprendizado da DSL do LangGraph.
  - Complexidade adicional na gestão do `State`.

## Mitigação
- Manter o grafo o mais modular possível, com nós pequenos e responsabilidades únicas.
- Uso extensivo de `SharedState` para passar dados entre os nós.
