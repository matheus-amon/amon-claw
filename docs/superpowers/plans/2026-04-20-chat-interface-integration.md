# Chat Interface Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a multi-provider chat interface (Twilio and Evolution API) for WhatsApp, allowing tenants to receive messages via webhooks and reply using the SDR LangGraph.

**Architecture:** We'll use a Strategy pattern for messaging clients. Webhooks in the presentation layer will capture incoming messages, resolve the tenant, and invoke the LangGraph. The graph will use an abstracted messaging client to respond.

**Tech Stack:** FastAPI, LangGraph, Beanie (MongoDB), Pydantic, HTTPX.

---

### Task 1: Update Tenant Entity and Models

**Files:**
- Modify: `src/amon_claw/domain/entities/tenant.py`
- Modify: `src/amon_claw/infrastructure/database/mongodb/models/tenant.py`
- Test: `tests/infrastructure/database/mongodb/repositories/test_tenant_repository.py`

- [ ] **Step 1: Update Domain Entity**
Add `MessagingProvider` enum and `TenantMessagingConfig` to the domain entity.

- [ ] **Step 2: Update MongoDB Model**
Update the Beanie model to persist the new configuration.

- [ ] **Step 3: Run existing tenant tests**
Ensure we didn't break anything.

- [ ] **Step 4: Commit**

---

### Task 2: Messaging Infrastructure (Clients) [COMPLETED]

**Files:**
- Create: `src/amon_claw/infrastructure/llm/tools/messaging_client.py`
- Test: `tests/infrastructure/llm/tools/test_messaging_clients.py`

- [x] **Step 1: Create BaseMessagingClient and implementations**
Define the ABC and the Twilio/Evolution clients.

- [x] **Step 2: Add factory**

- [x] **Step 3: Commit**

---

### Task 3: Webhook Presentation Layer

**Files:**
- Create: `src/amon_claw/presentation/api/routes/webhooks.py`
- Modify: `src/amon_claw/presentation/api/app.py`
- Test: `tests/presentation/api/test_webhooks.py`

- [ ] **Step 1: Create Webhook Routes**
Implement the endpoints for Twilio and Evolution.

- [ ] **Step 2: Register Router in App**

- [ ] **Step 3: Commit**

---

### Task 4: Integration with LangGraph

**Files:**
- Modify: `src/amon_claw/infrastructure/llm/agents/sdr_graph.py`
- Modify: `src/amon_claw/presentation/api/routes/webhooks.py`

- [ ] **Step 1: Invoke Graph from Webhooks**
Update webhooks to call the `sdr_assistant`.

- [ ] **Step 2: Finalize and Test**
Verify the end-to-end flow with mocks.
