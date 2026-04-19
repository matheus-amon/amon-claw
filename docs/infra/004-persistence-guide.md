# Guia Técnico: Camada de Persistência (Beanie + MongoDB)

## 1. Visão Geral
A persistência do Amon Claw utiliza **Beanie ODM** sobre o driver assíncrono **Motor**. O design foca em manter as entidades de domínio puras, enquanto os documentos do banco estendem essas entidades para adicionar funcionalidades de banco de dados.

## 2. Estrutura de Modelos
Localização: `src/amon_claw/infrastructure/database/mongodb/models/`

Todos os modelos seguem o padrão de paridade de ID com o domínio:
- O campo `id` da entidade (UUID) é mapeado para o `_id` do MongoDB.
- Isso evita a complexidade de converter entre `ObjectId` e `UUID` no código de aplicação.

Exemplo:
```python
class TenantDocument(Document, Tenant):
    id: UUID = Field(default_factory=uuid4, alias="_id")
```

## 3. Repositórios
Localização: `src/amon_claw/infrastructure/database/mongodb/repositories/`

Utilizamos o **Repository Pattern** para abstrair as consultas. Todos os repositórios herdam de `MongoRepository`, que fornece:
- `save(entity)`: Insere ou atualiza uma entidade.
- `get_by_id(id)`: Busca uma entidade pelo UUID.
- `delete(id)`: Remove uma entidade.

### Repositórios Disponíveis:
- `TenantRepository`
- `ProfessionalRepository`
- `ServiceRepository`
- `CustomerRepository` (inclui `get_by_phone`)
- `AppointmentRepository`

## 4. Como Usar (Exemplo)
```python
from amon_claw.infrastructure.database.mongodb.repositories import TenantRepository
from amon_claw.domain.entities.tenant import Tenant

repo = TenantRepository()
new_tenant = Tenant(name="Barbearia do Amon", phone="+5511...")
await repo.save(new_tenant)

tenant = await repo.get_by_phone("+5511...")
```

## 5. Testes
Os testes utilizam `mongomock-motor` para rodar um banco MongoDB em memória, garantindo velocidade e isolamento.
Comando para rodar: `uv run pytest tests/infrastructure/database/mongodb/repositories/`
