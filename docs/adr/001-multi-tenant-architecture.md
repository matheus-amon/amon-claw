# ADR 001: Multi-Tenant Architecture (Shared Database, Shared Schema)

## Contexto
A aplicação precisa suportar múltiplos negócios (Barbearia X, Clínica Y) de forma escalável e econômica. Cada negócio tem seus próprios clientes, serviços e horários.

## Decisão
Implementar uma arquitetura **Shared Database, Shared Schema**. Todos os registros (Tenants, Customers, Appointments) ficarão no mesmo banco de dados MongoDB, diferenciados por uma chave `tenant_id`.

## Status
Aceito.

## Consequências
- **Prós:**
  - Menor custo operacional (um único banco para gerenciar).
  - Facilidade de atualização de esquema (muda para todos de uma vez).
  - Simplicidade na agregação de dados globais (se necessário).
- **Contras:**
  - Risco de vazamento de dados se as consultas não forem filtradas corretamente pelo `tenant_id`.
  - Impacto de performance de um tenant barulhento sobre os outros (*noisy neighbor*).
  
## Mitigação
- Garantir que todas as camadas (Repository/Service) apliquem o filtro de `tenant_id` de forma compulsória (usar middlewares/interceptors se possível).
- Uso de índices compostos (e.g., `{ tenant_id: 1, phone: 1 }`).
