# MkDocs Documentation Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a centralized, visually appealing documentation hub for the amon-claw project using MkDocs Material with a lifecycle-based navigation.

**Architecture:** Lifecycle-based navigation (Product, Architecture, Development, Infrastructure, Changelog) mapping existing `docs/` subdirectories.

**Tech Stack:** MkDocs, MkDocs Material, uv, pymdown-extensions.

---

### Task 1: Install Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add MkDocs dependencies using uv**

Run:
```bash
uv add --dev mkdocs mkdocs-material pymdown-extensions
```

- [ ] **Step 2: Verify installation in pyproject.toml**

Run: `cat pyproject.toml`
Expected: `mkdocs`, `mkdocs-material`, and `pymdown-extensions` listed in `dev-dependencies` or `dependency-groups.dev`.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "build: add mkdocs dependencies"
```

---

### Task 2: Configure mkdocs.yml

**Files:**
- Create: `mkdocs.yml`

- [ ] **Step 1: Create the mkdocs.yml file with Deep Purple theme and Lifecycle navigation**

```yaml
site_name: Amon-Claw Docs
site_description: Central de documentação do SDR Scheduling Assistant

theme:
  name: material
  language: pt-BR
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/brightness-7
        name: Mudar para modo escuro
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: deep purple
      accent: deep purple
      toggle:
        icon: material/brightness-4
        name: Mudar para modo claro
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets

nav:
  - Home: index.md
  - 🚀 Product:
      - PRD: prd/001-sdr-scheduling-assistant.md
      - Requisitos Funcionais: requirements/functional.md
      - Requisitos Não-Funcionais: requirements/non-functional.md
  - 📐 Architecture:
      - Entidades de Domínio: domain/entities.md
      - ADRs:
          - 001 Multi-tenant: adr/001-multi-tenant-architecture.md
          - 002 Orchestration: adr/002-orchestration-langgraph-pydanticai.md
          - 003 Infrastructure: adr/003-infrastructure-as-code-terraform.md
  - 🛠️ Development:
      - Specs & Designs:
          - Persistence Layer: superpowers/specs/2026-04-18-persistence-layer-beanie.md
          - LangGraph State: superpowers/specs/2026-04-20-sdr-langgraph-state.md
          - MkDocs Setup: superpowers/specs/2026-04-19-mkdocs-setup-design.md
      - Implementation Plans:
          - Persistence Layer: superpowers/plans/2026-04-19-persistence-layer-beanie.md
          - Base SDR Graph: superpowers/plans/2026-04-20-implement-base-sdr-graph.md
      - Research:
          - LangGraph & PydanticAI: research/2026-04-19-langgraph-pydanticai-best-practices.md
  - ☁️ Infrastructure:
      - Cloud Setup: infra/001-cloud-native-setup.md
      - Secrets: infra/002-requirements-and-secrets.md
      - Terraform: infra/003-terraform-structure.md
      - Persistence Guide: infra/004-persistence-guide.md
  - 📜 Changelog:
      - '2026-04-19': logs/2026-04-19-persistence-layer-beanie.md
      - '2026-04-18': logs/2026-04-18-project-reset-and-domain-entities.md
```

- [ ] **Step 2: Commit**

```bash
git add mkdocs.yml
git commit -m "docs: add mkdocs.yml configuration"
```

---

### Task 3: Create Landing Page

**Files:**
- Create: `docs/index.md`

- [ ] **Step 1: Create a welcoming landing page**

```markdown
# Bem-vindo ao Amon-Claw Docs 🚀

Esta é a central de documentação do **Amon-Claw**, seu assistente inteligente de agendamento (SDR).

## 🎯 Objetivo do Projeto
O Amon-Claw foi desenvolvido para automatizar o agendamento de serviços, utilizando uma orquestração avançada com **LangGraph** e **PydanticAI**, persistência em **MongoDB (Beanie)** e infraestrutura escalável.

## 🗺️ Como navegar
Use o menu lateral para explorar os diferentes estágios do projeto:

*   **🚀 Product:** Visão geral do produto e requisitos.
*   **📐 Architecture:** Decisões arquiteturais (ADRs) e modelo de domínio.
*   **🛠️ Development:** Specs técnicas, planos de implementação e pesquisas.
*   **☁️ Infrastructure:** Guias de setup de nuvem e terraform.
*   **📜 Changelog:** Histórico diário de progresso.

---
> Esta documentação é mantida e atualizada dinamicamente pelo **Gemini CLI**.
```

- [ ] **Step 2: Commit**

```bash
git add docs/index.md
git commit -m "docs: add project landing page"
```

---

### Task 4: Verification

- [ ] **Step 1: Check for any broken links in nav**

Run: `mkdocs build --strict`
Expected: Successful build with no "File not found" errors.

- [ ] **Step 2: Inform the user how to run the server**

Run: `echo "Run 'mkdocs serve' to view the documentation locally at http://127.0.0.1:8000"`
