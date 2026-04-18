# Requisitos Funcionais (RF)

## Módulo: Gestão de Tenants (Negócios)
- **RF01:** O sistema deve permitir o cadastro de múltiplos estabelecimentos (Tenants).
- **RF02:** Cada Tenant deve poder configurar seu horário comercial e tempo de intervalo/limpeza.
- **RF03:** Cada Tenant deve poder cadastrar múltiplos profissionais e associar um Google Calendar a cada um.
- **RF04:** O sistema deve permitir configurar o catálogo de serviços (Nome, Preço, Duração).

## Módulo: Agente Conversacional (SDR)
- **RF05:** O sistema deve processar mensagens recebidas via WhatsApp (Evolution/Twilio).
- **RF06:** O agente deve ser capaz de listar serviços disponíveis e seus respectivos preços.
- **RF07:** O agente deve consultar o Google Calendar do profissional para sugerir horários livres.
- **RF08:** O agente deve realizar o agendamento (Create) no Google Calendar e no banco local.
- **RF09:** O agente deve suportar remarcação (Update) e cancelamento (Delete) de agendamentos.
- **RF10:** O agente deve realizar follow-ups se o cliente parar de responder no meio de um fluxo.

## Módulo: Aprovação (Human-in-the-Loop)
- **RF11:** O sistema deve permitir configurar um modo de "Aprovação Manual" por Tenant.
- **RF12:** Se a aprovação estiver ativa, o agendamento fica em estado "Pendente" até o dono confirmar via WhatsApp.

## Módulo: Notificações
- **RF13:** O sistema deve enviar uma confirmação para o cliente final após o agendamento ser concluído.
- **RF14:** O sistema deve notificar o profissional quando um novo agendamento for feito.
