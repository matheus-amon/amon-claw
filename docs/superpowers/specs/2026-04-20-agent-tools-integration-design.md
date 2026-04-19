# Design Spec: Integração das Tools no LangGraph e Pydantic AI

**Data:** 2026-04-20
**Tópico:** Integração das Ferramentas de Agendamento
**Status:** Approved (YOLO Mode)

## 1. Objetivo
Conectar as ferramentas recém-criadas (`list_services`, `list_professionals`, `check_availability`, `book_appointment`) ao `SchedulingAgent` e injetar as dependências (`AgentDeps`) necessárias a partir do nó `user_node` no LangGraph.

## 2. Arquitetura de Integração

### 2.1 Pydantic AI Agent (`SchedulingAgent`)
A classe `SchedulingAgent` precisa registrar as ferramentas no objeto `Agent`.
- Importaremos as funções de `infrastructure.llm.tools.read` e `infrastructure.llm.tools.write`.
- Registraremos via `self._agent.tool(func)`.
- Atualizaremos o `system_prompt` para guiar o modelo a usar essas ferramentas (ex: "Sempre verifique a disponibilidade antes de agendar").

### 2.2 LangGraph Node (`user_node`)
O `user_node` é responsável por invocar o agente. Ele precisa construir a instância de `AgentDeps` antes de chamar `agent.run(deps=deps, message=...)`.
- Como os repositórios (Beanie) são stateless e dependem da configuração global do banco, podemos instanciá-los diretamente dentro da criação de dependências.
- `tenant_id` e `customer_id` já estão no `SDRState`.

### 2.3 Dummy Calendar Adapter
Para viabilizar o teste ponta a ponta do fluxo MVP sem precisar de chaves reais do Google agora, criaremos um `DummyCalendarAdapter` (implementando `ICalendarAdapter`) que sempre retorna horários disponíveis fixos e finge criar o evento, retornando um ID mockado.

## 3. Componentes Afetados

1. **`src/amon_claw/infrastructure/llm/adapters/dummy_calendar.py` (Novo)**
   - Implementa `ICalendarAdapter`.
   - `get_free_slots` retorna slots simulados para o dia solicitado.
   - `create_event` retorna um UUID falso como `external_calendar_id`.

2. **`src/amon_claw/infrastructure/llm/agents/scheduling_agent.py`**
   - Importar ferramentas.
   - Atualizar a inicialização do `Agent(..., deps_type=AgentDeps)`.
   - Adicionar os decorators ou o método `.tool(...)`.

3. **`src/amon_claw/infrastructure/llm/agents/sdr_graph.py`**
   - No `user_node`, instanciar os repositórios (`TenantRepository`, `ServiceRepository`, `ProfessionalRepository`, `AppointmentRepository`).
   - Instanciar o `DummyCalendarAdapter`.
   - Construir o objeto `AgentDeps` passando o `tenant_id` e `customer_id` presentes no `state`.
   - Repassar o `deps` no `.run()`.

## 4. Testes e Validação
- Os testes unitários do grafo e do agente precisarão ser ajustados para mockar essas novas injeções caso falhem.
- Esta estrutura nos permite substituir o `DummyCalendarAdapter` pelo `GoogleCalendarAdapter` real de forma transparente, apenas mudando a injeção em `sdr_graph.py` (ou via um injetor/container de dependência futuro).