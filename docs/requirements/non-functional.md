# Requisitos Não-Funcionais (RNF)

## Escalabilidade e Performance
- **RNF01:** O sistema deve responder às mensagens do WhatsApp em menos de 5 segundos.
- **RNF02:** O sistema deve suportar até 100 Tenants simultâneos no MVP sem degradação.
- **RNF03:** O banco de dados deve usar índices compostos por `tenant_id` para otimizar as consultas.

## Segurança e Isolamento
- **RNF04:** Os dados de um Tenant nunca devem vazar para outro (isolamento lógico por ID).
- **RNF05:** As chaves de API (Google, Evolution, OpenRouter) devem ser armazenadas no AWS Secret Manager.
- **RNF06:** O sistema deve manter logs de auditoria para ações críticas (excluir agendamento).

## Disponibilidade
- **RNF07:** A aplicação deve ser implantada usando AWS Lambda (Serverless) para garantir alta disponibilidade.
- **RNF08:** Devem ser usados checkpointers persistentes (MongoDB) no LangGraph para que interrupções de conexão não causem perda de estado.

## Observabilidade
- **RNF09:** Deve haver logs estruturados de cada passo do LangGraph.
- **RNF10:** Deve ser possível rastrear o custo de tokens por Tenant.
