from pydantic_ai import RunContext
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from datetime import date, datetime, timedelta
from uuid import UUID

async def list_services(ctx: RunContext[AgentDeps]) -> str:
    """Retorna a lista de serviços oferecidos pelo estabelecimento (tenant)."""
    services = await ctx.deps.service_repository.get_all()
    filtered = [s for s in services if s.tenant_id == ctx.deps.tenant_id]
    
    if not filtered:
        return "Nenhum serviço encontrado."
        
    lines = []
    for s in filtered:
        lines.append(f"ID: {s.id} | Nome: {s.name} | Preço: R${s.price:.2f} | Duração: {s.duration} min")
    return "\n".join(lines)

async def list_professionals(ctx: RunContext[AgentDeps]) -> str:
    """Retorna a lista de profissionais disponíveis no estabelecimento."""
    professionals = await ctx.deps.professional_repository.get_all()
    filtered = [p for p in professionals if p.tenant_id == ctx.deps.tenant_id]
    
    if not filtered:
        return "Nenhum profissional encontrado."
        
    lines = []
    for p in filtered:
        lines.append(f"ID: {p.id} | Nome: {p.name}")
    return "\n".join(lines)

async def check_availability(ctx: RunContext[AgentDeps], professional_id: UUID, target_date: date, service_duration_min: int) -> str:
    """Consulta os horários livres de um profissional em uma data específica."""
    professional = await ctx.deps.professional_repository.get_by_id(professional_id)
    if not professional:
        return "Profissional não encontrado."
    if not professional.calendar_id:
        return "Profissional não possui agenda configurada."
        
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    
    slots = await ctx.deps.calendar_adapter.get_free_slots(
        calendar_id=professional.calendar_id,
        start_date=start_dt,
        end_date=end_dt,
        duration_minutes=service_duration_min
    )
    
    if not slots:
        return f"Não há horários disponíveis no dia {target_date.isoformat()}."
        
    return "\n".join([s.strftime("%Y-%m-%d %H:%M") for s in slots])
