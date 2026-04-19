from typing import Any

from pydantic_ai import Agent, RunContext

from amon_claw.infrastructure.llm.agents.base import BaseAgent
from amon_claw.infrastructure.llm.agents.deps import AgentDeps
from amon_claw.domain.entities.tenant import BusinessHours
from amon_claw.domain.entities.service import Service


async def update_business_hours(ctx: RunContext[AgentDeps], day: str, open_time: str, close_time: str) -> str:
    """
    Atualiza o horário de funcionamento para um dia específico.
    """
    tenant = await ctx.deps.tenant_repository.get_by_id(ctx.deps.tenant_id)
    if not tenant:
        return "Tenant não encontrado."
    
    # Normalizar o dia para lowercase para consistência
    day_key = day.lower()
    
    tenant.business_hours[day_key] = BusinessHours(open=open_time, close=close_time)
    await ctx.deps.tenant_repository.update(tenant)
    
    return f"Horário de {day} atualizado para {open_time} - {close_time} com sucesso!"


async def upsert_service(ctx: RunContext[AgentDeps], name: str, price: float, duration: int) -> str:
    """
    Cria ou atualiza um serviço no catálogo.
    """
    # Buscar serviços do tenant
    services = await ctx.deps.service_repository.get_all()
    # Filtrar pelo tenant_id (idealmente o repositório teria um método para isso)
    # Mas como o BaseRepository get_all retorna tudo, vamos filtrar aqui por enquanto
    # TODO: Adicionar get_by_tenant_id no ServiceRepository
    
    tenant_services = [s for s in services if s.tenant_id == ctx.deps.tenant_id]
    
    existing_service = next((s for s in tenant_services if s.name.lower() == name.lower()), None)
    
    if existing_service:
        existing_service.price = price
        existing_service.duration = duration
        await ctx.deps.service_repository.update(existing_service)
        return f"Serviço {name} atualizado com sucesso!"
    else:
        new_service = Service(
            tenant_id=ctx.deps.tenant_id,
            name=name,
            price=price,
            duration=duration
        )
        await ctx.deps.service_repository.create(new_service)
        return f"Serviço {name} criado com sucesso!"


async def list_catalog(ctx: RunContext[AgentDeps]) -> str:
    """
    Lista os horários de funcionamento e o catálogo de serviços atuais.
    """
    tenant = await ctx.deps.tenant_repository.get_by_id(ctx.deps.tenant_id)
    if not tenant:
        return "Tenant não encontrado."
    
    services = await ctx.deps.service_repository.get_all()
    tenant_services = [s for s in services if s.tenant_id == ctx.deps.tenant_id]
    
    output = "=== Horários de Funcionamento ===\n"
    for day, hours in tenant.business_hours.items():
        output += f"{day.capitalize()}: {hours.open} - {hours.close}\n"
    
    output += "\n=== Catálogo de Serviços ===\n"
    if not tenant_services:
        output += "Nenhum serviço cadastrado."
    else:
        for s in tenant_services:
            output += f"- {s.name}: R$ {s.price:.2f} ({s.duration} min)\n"
            
    return output


class AdminAgent(BaseAgent[str]):
    def __init__(self):
        self._agent = Agent(
            'google-gla:gemini-1.5-flash',
            deps_type=AgentDeps,
            system_prompt=(
                "Você é o assistente administrativo do Amon-Claw. "
                "Seu objetivo é ajudar o dono do negócio a configurar horários de funcionamento e catálogo de produtos/serviços. "
                "Seja direto e execute as ferramentas conforme solicitado. "
                "Quando o usuário pedir para listar, mostre os horários e serviços atuais."
            ),
            output_type=str,
        )

        # Registrar ferramentas
        self._agent.tool(update_business_hours)
        self._agent.tool(upsert_service)
        self._agent.tool(list_catalog)

    @property
    def agent(self) -> Agent:
        return self._agent

    async def run(self, deps: AgentDeps, message: str) -> str:
        result = await self._agent.run(message, deps=deps)
        return result.output
