# Pesquisa: Melhores Práticas LangGraph + Pydantic AI

## 1. Integração LangGraph & Pydantic AI
A melhor forma de integrar os dois é tratar o **LangGraph** como a camada de **orquestração** (estado, ciclos, roteamento) e o **Pydantic AI** como a camada de **execução** (agentes tipados, ferramentas, validação de saída).

### Estratégia de Implementação
- **Nós como Agentes:** Cada nó no LangGraph invoca um agente do Pydantic AI.
- **Estado Compartilhado:** O `State` do LangGraph é passado para os agentes, e o resultado validado (`result_type`) do Pydantic AI atualiza o estado do grafo.
- **Injeção de Dependências:** Usar o `deps_type` do Pydantic AI para injetar conexões de banco de dados e clientes de API nos agentes dentro dos nós do grafo.

## 2. Interface Abstrata para Agentes
Para garantir desacoplamento e testabilidade, devemos usar uma interface abstrata.

```python
from abc import ABC, abstractmethod
from pydantic_ai import Agent
from typing import Any, TypeVar, Generic

T = TypeVar("T")

class BaseAgent(ABC, Generic[T]):
    @property
    @abstractmethod
    def agent(self) -> Agent:
        pass

    @abstractmethod
    async def run(self, context: Any) -> T:
        pass
```

## 3. Separação de Fluxos (Admin vs. Usuário Final)

### Fluxo Admin (Configuração)
- **Objetivo:** Permitir que o dono do negócio configure o SDR (horários, serviços, preços, tom de voz).
- **Interface:** Chat-based ou Dashboard-integrated. O agente aqui atua como um "Consultor de Configuração".
- **Estado:** Focado em entidades de `Tenant`, `Professional` e `Service`.

### Fluxo Usuário Final (Agendamento)
- **Objetivo:** Clientes agendando serviços.
- **Interface:** Chat direto (WhatsApp, Webchat).
- **Estado:** Focado em `Appointment`, `Customer` e disponibilidade em tempo real.

## 4. Por que usar ambos?
- **Pydantic AI:** Evita erros de JSON malformado e garante que o LLM siga o esquema.
- **LangGraph:** Gerencia lógica complexa de "vai e volta" (ex: se o cliente mudar de ideia no meio do pagamento, volta para a escolha de horário).
