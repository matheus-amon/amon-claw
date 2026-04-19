# Log de Atividades - 18/04/2026

## Atividade: Reset do Projeto e Definição de Domínio

### O que foi feito:
- **Faxina Geral (The Clean Slate):** Removemos todo o código de estudo legado que estava nas pastas `src/amon_claw/application`, `domain` e `infrastructure`. O objetivo foi eliminar distrações e focar na implementação profissional do SDR.
- **Reestruturação Clean Architecture:** Recriamos a estrutura de diretórios para suportar o desenvolvimento modular:
  - `application/`: Casos de uso e interfaces.
  - `domain/entities/`: Onde mora o coração do negócio.
  - `infrastructure/`: Implementações de banco (Mongo/Beanie) e agentes (Pydantic AI).
  - `presentation/`: API FastAPI.
- **Implementação do Domínio Base:** Criamos as entidades Pydantic fundamentais para o sistema multi-tenant:
  - `Tenant`: Representa o negócio (ex: barbearia).
  - `Professional`: O prestador de serviço.
  - `Service`: O que é oferecido e por quanto.
  - `Customer`: O cliente final do WhatsApp.
  - `Appointment`: O registro do agendamento propriamente dito.

### Status Técnico:
- **Dependencies:** `pyproject.toml` ajustado para Python `>=3.12` e `uv` como gerenciador oficial.
- **Docker:** `Dockerfile` pronto para AWS Lambda (Web Adapter) e `compose.yml` unificado com Mongo/Redis.
- **Health Check:** Endpoint `/health` implementado em `src/amon_claw/presentation/api/app.py`.
- **Persistência:** Definido uso de Beanie ODM com separação entre Domínio (Puro) e Infra (Models).

### Próximos Passos:
- Implementar os modelos do Beanie em `infrastructure/database/mongodb/models/` herdando do domínio.
- Configurar o `init_db` no startup da aplicação.
- Implementar repositórios básicos para CRUD das entidades.
- Configurar as `Pydantic Settings` para gestão profissional de variáveis de ambiente.
- Iniciar o desenho do grafo do **LangGraph**.
