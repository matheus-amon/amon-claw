from pydantic_ai import RunContext
from uuid import UUID
from datetime import datetime, timedelta
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.domain.entities.appointment import Appointment, AppointmentStatus

async def book_appointment(ctx: RunContext[AgentDeps], professional_id: UUID, service_id: UUID, start_time: datetime) -> str:
    """Agenda um serviço no calendário do profissional e salva no banco de dados."""
    professional = await ctx.deps.professional_repository.get_by_id(professional_id)
    service = await ctx.deps.service_repository.get_by_id(service_id)
    
    if not professional or not service:
        return "Profissional ou Serviço inválido."
        
    end_time = start_time + timedelta(minutes=service.duration)
    
    try:
        ext_id = await ctx.deps.calendar_adapter.create_event(
            calendar_id=professional.calendar_id,
            summary=f"Agendamento: {service.name}",
            description=f"Cliente ID: {ctx.deps.customer_id}",
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        return f"Falha ao agendar no calendário externo: {str(e)}"
        
    appointment = Appointment(
        tenant_id=ctx.deps.tenant_id,
        professional_id=professional_id,
        customer_id=ctx.deps.customer_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status=AppointmentStatus.CONFIRMADO,
        external_calendar_id=ext_id
    )
    
    await ctx.deps.appointment_repository.save(appointment)
    return f"Agendamento confirmado com sucesso! ID: {appointment.id}"
