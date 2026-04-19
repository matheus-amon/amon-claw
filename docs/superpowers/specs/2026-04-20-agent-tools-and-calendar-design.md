# Design Spec: Pydantic AI Tools e Integração Google Calendar

**Data:** 2026-04-20
**Tópico:** Ferramentas de Leitura/Escrita do Agente e Adapter do Google Calendar
**Status:** Approved (YOLO Mode)

## 1. Objetivo
Fornecer ao `SchedulingAgent` (Pydantic AI) as ferramentas necessárias para interagir com o banco de dados (Beanie/MongoDB) e com o Google Calendar. O foco é alta previsibilidade (determinismo), mantendo a lógica restrita às ferramentas (Tools) e validada via schemas estritos do Pydantic.

## 2. Arquitetura das Ferramentas (Tools)

As ferramentas serão injetadas no contexto do Pydantic AI (`RunContext`). O contexto (`deps`) conterá as instâncias dos repositórios e do adapter do calendário para facilitar os testes (Injeção de Dependências).

### 2.1. Dependências do Contexto (AgentDeps)
```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Any

class AgentDeps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    tenant_id: UUID
    customer_id: UUID
    tenant_repository: Any
    service_repository: Any
    professional_repository: Any
    appointment_repository: Any
    calendar_adapter: Any
```

### 2.2. Tools de Leitura (Read)
As tools devem retornar strings formatadas (ou listas serializáveis) claras para o LLM.

1. **`list_services(ctx: RunContext[AgentDeps]) -> str`**
   - Busca todos os serviços atrelados ao `tenant_id`.
   - Retorno: Lista com Nome, Duração (min), Preço e ID.

2. **`list_professionals(ctx: RunContext[AgentDeps]) -> str`**
   - Busca todos os profissionais atrelados ao `tenant_id`.
   - Retorno: Lista com Nome, Especialidade e ID.

3. **`check_availability(ctx: RunContext[AgentDeps], professional_id: UUID, target_date: date) -> str`**
   - Recebe a data desejada (formato ISO `YYYY-MM-DD`).
   - Busca o `Professional` para obter o `calendar_id`.
   - Chama `calendar_adapter.get_free_slots(...)`.
   - Retorno: Lista de horários disponíveis no dia.

### 2.3. Tool de Escrita (Write)
A tool de agendamento deve ser transacional na medida do possível e extremamente validada.

4. **`book_appointment(ctx: RunContext[AgentDeps], professional_id: UUID, service_id: UUID, start_time: datetime) -> str`**
   - **Validação:** Verifica se o horário ainda está livre no Calendar.
   - **Ação 1:** Cria o evento no Google Calendar via Adapter.
   - **Ação 2:** Salva a entidade `Appointment` no MongoDB com o `external_calendar_id`.
   - Retorno: Mensagem de sucesso com ID da reserva ou falha detalhada.

## 3. Adapter do Google Calendar

Para manter a Clean Architecture, a infraestrutura externa é isolada por interfaces.

### 3.1. Interface (Application Layer)
```python
class ICalendarAdapter(ABC):
    @abstractmethod
    async def get_free_slots(self, calendar_id: str, start_date: datetime, end_date: datetime, duration_minutes: int) -> list[datetime]:
        pass

    @abstractmethod
    async def create_event(self, calendar_id: str, summary: str, description: str, start_time: datetime, end_time: datetime) -> str:
        pass
```

### 3.2. Implementação (Infrastructure Layer)
A classe `GoogleCalendarAdapter` implementará essa interface utilizando a biblioteca `google-api-python-client` ou chamadas HTTP diretas (REST). Para o MVP, usaremos autenticação via *Service Account* (JSON key), onde o bot tem permissão para ler/escrever nas agendas compartilhadas com ele.

## 4. Integração no LangGraph

- **Nó Único para o Agente:** Como o Pydantic AI já gerencia múltiplas chamadas de tool internamente num mesmo "run", o nó `user_node` no LangGraph simplesmente passa a mensagem do usuário para o Pydantic AI e aguarda a resposta final.
- O determinismo vem de **não** tentar fazer o LangGraph decidir qual tool chamar, deixando isso para a máquina de inferência tipada do Pydantic AI, reduzindo o número de nós complexos no grafo.

## 5. Tratamento de Erros e Validação
- Todas as chamadas de Tool usam argumentos tipados via Pydantic. Se o LLM tentar passar uma data em formato inválido, o Pydantic AI automaticamente retorna o erro pro LLM corrigir antes de prosseguir (funcionalidade nativa).
- O Adapter deve tratar falhas de rede (Timeout) e retornar strings descritivas para o LLM ("O calendário do profissional está temporariamente indisponível").
