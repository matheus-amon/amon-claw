# Domínio e Entidades

## Entidades Principais

### Tenant (Negócio)
- `id`: UUID
- `name`: Nome do estabelecimento
- `phone`: Número do WhatsApp conectado
- `business_hours`: { dia_semana: { open: string, close: string } }
- `settings`: { human_in_the_loop: boolean, buffer_time: number }

### Professional (Prestador)
- `id`: UUID
- `tenant_id`: FK
- `name`: Nome do profissional
- `calendar_id`: ID do Google Calendar associado
- `services`: List[ServiceID]

### Service (Serviço)
- `id`: UUID
- `tenant_id`: FK
- `name`: Nome do serviço (ex: Corte de Cabelo)
- `description`: Descrição opcional
- `price`: Valor monetário
- `duration`: Duração em minutos

### Customer (Cliente Final)
- `id`: UUID
- `tenant_id`: FK
- `name`: Nome (extraído da conversa)
- `phone`: Número do WhatsApp
- `history`: Lista de agendamentos passados

### Appointment (Agendamento)
- `id`: UUID
- `tenant_id`: FK
- `professional_id`: FK
- `customer_id`: FK
- `service_id`: FK
- `start_time`: DateTime
- `end_time`: DateTime
- `status`: [PENDENTE, CONFIRMADO, CANCELADO, FINALIZADO]
- `external_calendar_id`: ID do evento no Google Calendar
