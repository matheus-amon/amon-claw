# Log: Intent and Security Orchestration Implementation

**Data:** 2026-04-20
**Tópico:** Implementação de Camada de Segurança e Classificação de Intenção no Grafo SDR

## Contexto
Para garantir que o assistente SDR seja robusto contra "malandragem" (prompt injection) e mantenha o foco no agendamento, implementamos uma camada de segurança determinística no LangGraph.

## Atividades Realizadas
1.  **Expansão do `SDRState`**: Adicionados campos `intent_type`, `security_flag` e `off_topic_count` para rastreamento de estado de segurança.
2.  **`IntentSecurityNode`**: Implementado nó inicial que atua como filtro, classificando a intenção do usuário e detectando tentativas de injeção de prompt via heurísticas (preparado para LLM/PydanticAI futuramente).
3.  **`OffTopicResponderNode`**: Implementado "xerife" da conversa que incrementa um contador de desvios toda vez que o usuário sai do tópico de agendamento.
4.  **`SecurityActionNode`**: Implementado botão de pânico que encerra a sessão de forma segura e dispara alertas críticos.
5.  **Sistema de Notificações**: Criada infraestrutura básica de alertas em `src/amon_claw/infrastructure/notifications/alerts.py` que gera logs `CRITICAL` com o payload da ameaça (Tenant, Customer, Flag).
6.  **Integração no Grafo**: Amarrada a lógica de roteamento condicional (`should_continue`) para garantir que o fluxo respeite as flags de segurança.

## Resultados
- **Determinismo**: O robô não "entra na onda" de conversas fiadas após o limite definido (threshold).
- **Segurança**: Bloqueio imediato de prompts de injeção conhecidos.
- **Observabilidade**: Alertas críticos gerados automaticamente para auditoria de dev e dono do negócio.
- **Testes**: 100% de cobertura nos novos nós e testes de integração de fluxo completo passando.

## Próximos Passos
- Evoluir as heurísticas do `IntentSecurityNode` para usar uma LLM dedicada ou modelo de classificação especializado.
- Integrar o sistema de notificações com canais externos (Slack/Email Webhooks).
- Implementar política de bloqueio temporário (ban) no banco de dados para IDs persistentes de ataque.
