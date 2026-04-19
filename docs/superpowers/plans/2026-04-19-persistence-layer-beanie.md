# Persistence Layer (Beanie + MongoDB) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the persistence layer using Beanie ODM, ensuring domain entities remain pure and the system supports multi-tenancy via `tenant_id` filters.

**Architecture:** Use multiple inheritance for Beanie Documents (`class TenantDocument(Document, Tenant)`), initialize connection via FastAPI lifespan, and implement repository patterns for data access.

**Tech Stack:** Python 3.12, Beanie ODM, Motor (MongoDB driver), Pydantic Settings, FastAPI.

---

### Task 1: Update Database Settings

**Files:**
- Modify: `src/amon_claw/core/settings/db.py`

- [ ] **Step 1: Update `DatabaseConfig` to support MongoDB**

```python
class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        case_sensitive=False,
        extra='ignore',
    )

    uri: str = Field(default='mongodb://localhost:27017/amon_claw')
    db_name: str = Field(default='amon_claw')
```

- [ ] **Step 2: Commit**
```bash
git add src/amon_claw/core/settings/db.py
git commit -m "chore: update database settings for MongoDB/Beanie"
```

---

### Task 2: Implement Beanie Documents

**Files:**
- Create: `src/amon_claw/infrastructure/database/mongodb/models/tenant.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/models/professional.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/models/service.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/models/customer.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/models/appointment.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/models/__init__.py`

- [ ] **Step 1: Create `TenantDocument`**
```python
from beanie import Document
from amon_claw.domain.entities.tenant import Tenant

class TenantDocument(Document, Tenant):
    class Settings:
        name = "tenants"
        indexes = ["phone"]
```

- [ ] **Step 2: Create remaining documents (Professional, Service, Customer, Appointment)**
Following the same pattern, inheriting from domain entities and `beanie.Document`.

- [ ] **Step 3: Commit**
```bash
git add src/amon_claw/infrastructure/database/mongodb/models/
git commit -m "feat: add Beanie documents for all domain entities"
```

---

### Task 3: Database Initialization & FastAPI Integration

**Files:**
- Create: `src/amon_claw/infrastructure/database/mongodb/client.py`
- Modify: `src/amon_claw/presentation/api/app.py`

- [ ] **Step 1: Implement `init_db` in `client.py`**
```python
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from amon_claw.core.config import settings_singleton
from amon_claw.infrastructure.database.mongodb.models import __all_models__

async def init_db():
    settings = settings_singleton()
    client = AsyncIOMotorClient(settings.db.uri)
    await init_beanie(
        database=client[settings.db.db_name],
        document_models=__all_models__
    )
```

- [ ] **Step 2: Integrate `lifespan` in `app.py`**
```python
from contextlib import asynccontextmanager
from amon_claw.infrastructure.database.mongodb.client import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
```

- [ ] **Step 3: Commit**
```bash
git add src/amon_claw/infrastructure/database/mongodb/client.py src/amon_claw/presentation/api/app.py
git commit -m "feat: integrate Beanie initialization with FastAPI lifespan"
```

---

### Task 4: Repository Pattern Implementation

**Files:**
- Create: `src/amon_claw/application/interfaces/repositories/base.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/base.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/tenant_repository.py`

- [ ] **Step 1: Define Base Repository Interface**
- [ ] **Step 2: Implement Mongo Repository for Tenant**
- [ ] **Step 3: Commit**
```bash
git add src/amon_claw/application/interfaces/repositories/ src/amon_claw/infrastructure/database/mongodb/repositories/
git commit -m "feat: implement repository pattern for Tenant"
```
