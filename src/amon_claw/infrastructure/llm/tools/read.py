from pydantic_ai import RunContext
from amon_claw.infrastructure.llm.agents.deps import AgentDeps

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