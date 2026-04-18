# PRD - SDR & Assistente de Agendamento (Amon Claw)

## 1. Visão Geral do Produto
O **Amon Claw** evoluiu para ser um assistente virtual inteligente (SDR) focado em pequenos negócios de serviço (barbearias, clínicas, estúdios). O objetivo é eliminar o atrito de agendamento no WhatsApp, garantindo atendimento 24/7 e gestão de agenda sem intervenção humana constante.

## 2. Problema e Oportunidade
Donos de pequenos negócios perdem vendas por não conseguirem responder o WhatsApp enquanto prestam serviço. Clientes finais desistem se não tiverem uma confirmação rápida.
**Solução:** Um agente autônomo que conversa, entende a necessidade, consulta a disponibilidade real e fecha o agendamento.

## 3. Público-Alvo (Personas)
- **Dono do Negócio:** Quer delegar o atendimento repetitivo e ter a agenda cheia.
- **Cliente Final:** Quer praticidade para marcar um serviço às 23h sem precisar ligar ou esperar até o dia seguinte.

## 4. Escopo do MVP
- **Integração WhatsApp:** Suporte a múltiplas instâncias (Evolution API/Twilio).
- **Gestão de Agenda:** Sincronização com Google Calendar.
- **Multi-Profissionais:** Suporte a diferentes agendas dentro de um mesmo Tenant.
- **Fluxo Conversacional:** Saudação, consulta de serviços/preços, verificação de disponibilidade, confirmação/edição/cancelamento.
- **Multi-Tenancy:** Uma única aplicação servindo múltiplos estabelecimentos com isolamento de dados.

## 5. Roadmap
- **Fase 1:** Agendamento básico, Multi-Tenant, Google Calendar.
- **Fase 2:** Edição/Cancelamento via IA, Follow-ups automáticos.
- **Fase 3:** Dashboards de gestão, Relatórios de conversão.
- **Fase 4:** Integração de pagamentos (Sinal/PIX).

## 6. Infraestrutura & Deploy (Cloud Native)
Para garantir que o Amon Claw seja "Production-First", a infraestrutura segue o modelo Serverless:
- **Computação:** AWS Lambda rodando container Docker via ECR.
- **API Gateway:** HTTP API para exposição do endpoint.
- **Banco de Dados:** MongoDB Atlas (Tier M0 Free).
- **IaC:** Terraform para gerenciamento de toda a infra.
- **CI/CD:** GitHub Actions para build do Docker e deploy via Terraform.
