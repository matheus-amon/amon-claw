# Design Spec: Orquestração de Agentes com LangGraph e Pydantic AI

**Data:** 19/04/2026  
**Status:** Draft  
**Autor:** Gemini CLI (Modo PO/Arquiteto)

## 1. Objetivo
Definir a arquitetura do "cérebro" do Amon Claw, utilizando LangGraph para orquestração de estado e Pydantic AI para execução determinística de agentes especialistas. O sistema deve suportar dois fluxos distintos (Admin e Usuário Final) no mesmo canal de comunicação.

## 2. Arquitetura de Alto Nível

### 2.1 Componentes Principais
- **Orquestrador (LangGraph):** Gerencia o grafo de estados, transições entre nós e persistência de curto prazo (checkpointers).
- **Executores (Pydantic AI):** Agentes especializados com `result_type` estrito e `deps_type` para injeção de dependências.
- **Modelos:** Gemini 1.5 Flash ou GPT-4o-mini com temperatura 0.

### 2.2 Camadas (Clean Architecture)
- **Presentation:** Controladores de API ou Webhooks (ex: WhatsApp) que recebem `user_id` e `message`.
- **Application (Use Case):** Contém a interface `IBrain` e sua implementação `LangGraphBrain`. É aqui que o grafo reside.
- **Domain:** Entidades (`Tenant`, `Appointment`, etc.) e lógica de negócio pura.
- **Infrastructure:** Implementações de Repositórios (MongoDB/Beanie), ferramentas de LLM e clientes de mensageria.

## 3. Design de Interfaces

### 3.1 Interface de Entrada (`IBrain`)
```python
class IBrain(ABC):
    @abstractmethod
    async def process_message(self, tenant_id: str, user_id: str, message: str) -> str:
        """Processa uma mensagem e retorna a resposta do SDR."""
        pass
```

### 3.2 Interface de Agente (`BaseAgent`)
```python
from pydantic_ai import Agent
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseAgent(ABC, Generic[T]):
    @property
    @abstractmethod
    def agent(self) -> Agent:
        """Retorna a instância do agente Pydantic AI configurada."""
        pass
    
    @abstractmethod
    async def run(self, deps: Any, message: str) -> T:
        """Executa a lógica do agente."""
        pass
```

## 4. Separação de Fluxos

### 4.1 Fluxo Admin (Dono do Negócio)
- **Ativação:** Comando `/admin <hash>`.
- **Agente:** `AdminConfigAgent`.
- **Funcionalidades:** Configurar serviços, preços, horários de funcionamento e visualizar métricas via chat.
- **Vibe:** "Funcionário virtual" ajudando na gestão.

### 4.2 Fluxo Usuário Final (Cliente)
- **Ativação:** Fluxo padrão.
- **Agente:** `SchedulingAgent`.
- **Funcionalidades:** Consulta de disponibilidade, reserva de horários e esclarecimento de dúvidas sobre serviços.

## 5. Persistência e Dados

### 5.1 Estado da Conversa (Checkpointer)
- Utilização do checkpointer nativo do LangGraph (Postgres ou MongoDB) para garantir continuidade e memória de curto prazo.

### 5.2 Persistência de Negócio e Métricas
- **Beanie (MongoDB):** Armazenamento de entidades de domínio.
- **Métricas para MVP:**
    - Taxa de conversão (mensagens vs. agendamentos).
    - Serviços mais procurados.
    - Horários de pico.
    - Tempo médio de fechamento.

## 6. Estratégia de Implementação
1. Criar a interface abstrata `IBrain` e `BaseAgent`.
2. Implementar o `AdminConfigAgent` com Pydantic AI.
3. Implementar o `SchedulingAgent` com Pydantic AI.
4. Orquestrar ambos no `LangGraph` com um nó de roteamento inicial baseado no comando `/admin`.
5. Injetar Repositories como dependências (`deps`) nos agentes.
