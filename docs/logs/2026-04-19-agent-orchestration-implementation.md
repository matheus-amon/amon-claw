# Log de Implementação: Orquestração de Agentes (LangGraph + Pydantic AI)

**Data:** 19/04/2026  
**Status:** Concluído  

## Resumo das Atividades
Nesta sessão, implementamos o "Cérebro" do Amon Claw, utilizando LangGraph para a orquestração de estados e Pydantic AI para a execução determinística dos agentes.

## O que foi feito
1.  **Interface Abstrata:**
    - Criada a interface `IBrain` (`src/amon_claw/application/interfaces/brain.py`) para isolar a camada de apresentação da lógica do grafo.
    - Criada a interface `BaseAgent` (`src/amon_claw/infrastructure/llm/agents/base.py`) para padronizar a criação de agentes com Pydantic AI.
2.  **Estado do SDR:**
    - Atualizado o `SDRState` para suportar controle de fluxo (`admin` vs `user`) e autenticação.
3.  **Roteamento Inteligente:**
    - Implementado nó de roteamento que identifica o comando `/admin` e chaveia o fluxo da conversa.
4.  **Agente de Agendamento:**
    - Implementado o `SchedulingAgent` como o primeiro executor real do fluxo de usuário.
5.  **Integração no Grafo:**
    - O `sdr_graph.py` foi atualizado para conectar o roteador ao agente de agendamento.
6.  **Compatibilidade Pydantic AI:**
    - Corrigidas incompatibilidades com a versão `1.70.0` da `pydantic-ai` (mudança de `result_type` para `output_type` e de `.data` para `.output`).

## Desafios e Soluções
- **API da Pydantic AI:** A versão instalada tinha mudanças significativas na assinatura da classe `Agent` e na estrutura do `AgentRunResult`. Realizamos uma investigação via scripts e corrigimos o código e os testes para garantir a conformidade.
- **Segurança do Grafo:** Adicionadas proteções no `user_node` para lidar com estados de mensagens vazias e evitar erros de índice.

## Próximos Passos
- Implementar o `AdminFlow` para permitir que o dono do negócio configure o SDR via chat.
- Injetar os repositórios reais (Beanie/MongoDB) nos agentes para persistência de dados de agendamento.
- Integrar o `LangGraphBrain` nos controladores da API.
