# Design Spec: Persistence Layer with Beanie ODM

**Data:** 2026-04-18
**Status:** Approved
**Tópico:** Implementação da camada de persistência usando Beanie (MongoDB) mantendo o domínio puro.

## 1. Objetivo
Estabelecer como os dados serão persistidos no MongoDB, garantindo que as entidades de domínio permaneçam agnósticas à tecnologia de banco de dados, utilizando o Beanie como ODM para facilitar o mapeamento e validação via Pydantic.

## 2. Arquitetura

### 2.1 Separação de Responsabilidades
- **Domain (`src/amon_claw/domain/entities/`)**: Contém apenas classes `BaseModel` do Pydantic. Nenhuma dependência do Beanie ou Motor.
- **Infrastructure (`src/amon_claw/infrastructure/database/mongodb/models/`)**: Contém as classes `Document` do Beanie. Elas herdarão das entidades de domínio e do `beanie.Document`.
- **Infrastructure (`src/amon_claw/infrastructure/database/mongodb/repositories/`)**: Implementações dos repositórios que encapsulam a lógica de persistência e retornam entidades de domínio.

### 2.2 Estrutura de Documentos
Os documentos serão definidos usando Herança Múltipla para evitar duplicação de campos:

```python
from beanie import Document
from amon_claw.domain.entities.tenant import Tenant

class TenantDocument(Document, Tenant):
    class Settings:
        name = "tenants"
        indexes = ["phone"]
```

## 3. Entidades e Índices

| Coleção | Entidade de Domínio | Índices | Notas |
| :--- | :--- | :--- | :--- |
| `tenants` | `Tenant` | `phone` (Unique) | Identificador principal do bot |
| `professionals` | `Professional` | `tenant_id` | Filtro por negócio |
| `services` | `Service` | `tenant_id` | Catálogo por negócio |
| `customers` | `Customer` | `[tenant_id, phone]` (Unique) | Cliente único por estabelecimento |
| `appointments` | `Appointment` | `[tenant_id, start_time]`, `professional_id` | Busca de agenda e disponibilidade |

## 4. Inicialização
A conexão será gerida por uma função `init_db` que:
1. Obtém a URI do MongoDB via `Settings`.
2. Cria o cliente assíncrono `Motor`.
3. Registra todos os `Document` models no Beanie.

## 5. Próximos Passos
1. Implementar `src/amon_claw/infrastructure/database/mongodb/models/`.
2. Configurar o cliente e inicialização em `src/amon_claw/infrastructure/database/mongodb/client.py`.
3. Criar os repositórios básicos para cada entidade.
