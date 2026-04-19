# Complete Persistence Layer (Beanie + MongoDB)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardize model IDs and implement all missing repositories for the persistence layer.

**Architecture:** Update Beanie documents to use `UUID` as `_id` (matching domain entities) and implement the repository pattern for all entities using `MongoRepository` base class.

**Tech Stack:** Python 3.12, Beanie ODM, Motor, Pytest.

---

### Task 1: Standardize Model IDs

**Files:**
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/professional.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/service.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/customer.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/appointment.py`

- [ ] **Step 1: Update ProfessionalDocument**
```python
from uuid import UUID, uuid4
from pydantic import Field
from beanie import Document
from amon_claw.domain.entities.professional import Professional

class ProfessionalDocument(Document, Professional):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    class Settings:
        name = "professionals"
        indexes = ["tenant_id"]
```

- [ ] **Step 2: Update ServiceDocument**
```python
from uuid import UUID, uuid4
from pydantic import Field
from beanie import Document
from amon_claw.domain.entities.service import Service

class ServiceDocument(Document, Service):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    class Settings:
        name = "services"
        indexes = ["tenant_id"]
```

- [ ] **Step 3: Update CustomerDocument**
```python
from uuid import UUID, uuid4
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from beanie import Document
from amon_claw.domain.entities.customer import Customer

class CustomerDocument(Document, Customer):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    class Settings:
        name = "customers"
        indexes = [
            IndexModel(
                [("tenant_id", ASCENDING), ("phone", ASCENDING)],
                unique=True
            )
        ]
```

- [ ] **Step 4: Update AppointmentDocument**
```python
from uuid import UUID, uuid4
from pydantic import Field
from pymongo import IndexModel, ASCENDING
from beanie import Document
from amon_claw.domain.entities.appointment import Appointment

class AppointmentDocument(Document, Appointment):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    class Settings:
        name = "appointments"
        indexes = [
            IndexModel([("tenant_id", ASCENDING), ("start_time", ASCENDING)]),
            "professional_id"
        ]
```

- [ ] **Step 5: Commit changes**
```bash
git add src/amon_claw/infrastructure/database/mongodb/models/
git commit -m "refactor: standardize all Beanie documents to use UUID as _id"
```

---

### Task 2: Implement Missing Repositories

**Files:**
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/professional_repository.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/service_repository.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/customer_repository.py`
- Create: `src/amon_claw/infrastructure/database/mongodb/repositories/appointment_repository.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/repositories/__init__.py`

- [ ] **Step 1: Create ProfessionalRepository**
```python
from amon_claw.domain.entities.professional import Professional
from amon_claw.infrastructure.database.mongodb.models.professional import ProfessionalDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class ProfessionalRepository(MongoRepository[Professional, ProfessionalDocument]):
    def __init__(self):
        super().__init__(ProfessionalDocument, Professional)
```

- [ ] **Step 2: Create ServiceRepository**
```python
from amon_claw.domain.entities.service import Service
from amon_claw.infrastructure.database.mongodb.models.service import ServiceDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class ServiceRepository(MongoRepository[Service, ServiceDocument]):
    def __init__(self):
        super().__init__(ServiceDocument, Service)
```

- [ ] **Step 3: Create CustomerRepository**
```python
from typing import Optional
from uuid import UUID
from amon_claw.domain.entities.customer import Customer
from amon_claw.infrastructure.database.mongodb.models.customer import CustomerDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class CustomerRepository(MongoRepository[Customer, CustomerDocument]):
    def __init__(self):
        super().__init__(CustomerDocument, Customer)

    async def get_by_phone(self, tenant_id: UUID, phone: str) -> Optional[Customer]:
        doc = await self.document_model.find_one(
            CustomerDocument.tenant_id == tenant_id,
            CustomerDocument.phone == phone
        )
        if doc:
            return self.entity_class(**doc.model_dump())
        return None
```

- [ ] **Step 4: Create AppointmentRepository**
```python
from amon_claw.domain.entities.appointment import Appointment
from amon_claw.infrastructure.database.mongodb.models.appointment import AppointmentDocument
from amon_claw.infrastructure.database.mongodb.repositories.base import MongoRepository

class AppointmentRepository(MongoRepository[Appointment, AppointmentDocument]):
    def __init__(self):
        super().__init__(AppointmentDocument, Appointment)
```

- [ ] **Step 5: Update Repositories __init__.py**
```python
from .tenant_repository import TenantRepository
from .professional_repository import ProfessionalRepository
from .service_repository import ServiceRepository
from .customer_repository import CustomerRepository
from .appointment_repository import AppointmentRepository

__all__ = [
    "TenantRepository",
    "ProfessionalRepository",
    "ServiceRepository",
    "CustomerRepository",
    "AppointmentRepository",
]
```

- [ ] **Step 6: Commit changes**
```bash
git add src/amon_claw/infrastructure/database/mongodb/repositories/
git commit -m "feat: implement Professional, Service, Customer and Appointment repositories"
```

---

### Task 3: Verify with Integration Tests

**Files:**
- Create: `tests/infrastructure/database/mongodb/repositories/test_all_repositories.py`

- [ ] **Step 1: Create exhaustive tests for all repositories**
Use `mongomock_motor` (already configured in `conftest.py`) to test CRUD for all 4 new repos.

- [ ] **Step 2: Run tests**
Run: `uv run pytest tests/infrastructure/database/mongodb/repositories/test_all_repositories.py`
Expected: 100% PASS.

- [ ] **Step 3: Final Commit**
```bash
git add tests/infrastructure/database/mongodb/repositories/test_all_repositories.py
git commit -m "test: add integration tests for all remaining repositories"
```
