# Log de Atividades - 20/04/2026 - Pydantic AI Tools & Google Calendar

## Contexto
O SDR precisava de ferramentas ("mãos e olhos") para interagir com o mundo real, especificamente para buscar serviços, profissionais e agendar horários no Google Calendar através de agentes Pydantic AI.

## Atividades Realizadas
1. **Google Calendar Dependencies:** Instalação das bibliotecas `google-api-python-client` e `google-auth`.
2. **Contexto de Agente (AgentDeps):** Criação de um modelo Pydantic em `src/amon_claw/infrastructure/llm/agents/deps.py` para injeção de dependências (repositórios e adapter do calendário).
3. **Interface do Calendário:** Criação de `ICalendarAdapter` definindo os contratos `get_free_slots` e `create_event`.
4. **Tools de Leitura (Read):** Implementação de `list_services` e `list_professionals` para listar dados do MongoDB filtrados por Tenant.
5. **Tools de Escrita (Write):** Implementação de `check_availability` para consultar horários livres e `book_appointment` para salvar a entidade no banco de dados e inserir o evento no calendário simultaneamente.

## Resultados
- Todas as ferramentas foram implementadas seguindo a abordagem de **Test-Driven Development (TDD)** com 100% dos novos testes isolados passando.
- A orquestração do LangGraph agora tem as tools necessárias para as consultas determinísticas e ações de transação.

## Próximos Passos
- Conectar o Pydantic AI Agent (`SchedulingAgent`) ao grafo do LangGraph com as tools injetadas.
- Lidar com a implementação concreta do `GoogleCalendarAdapter` utilizando as chaves de serviço.
- Adicionar verificações rigorosas de segurança na Tool de agendamento (ex: checar se o serviço pertence ao profissional).