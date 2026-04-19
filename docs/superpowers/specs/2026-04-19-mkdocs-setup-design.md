# Design Spec: MkDocs Documentation Hub

**Date:** 2026-04-19
**Topic:** MkDocs Setup for Amon-Claw
**Status:** Approved

## 1. Objective
Establish a centralized, visually appealing documentation hub for the `amon-claw` project using MkDocs Material. The goal is to provide a "live" dashboard for features, specs, and architectural decisions, supporting both internal development and external project overview.

## 2. Technical Stack
- **Engine:** [MkDocs](https://www.mkdocs.org/)
- **Theme:** [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- **Dependency Manager:** `uv`
- **Extensions:**
    - `pymdown-extensions` (Admonitions, SuperFences, Checklists, Details)
    - `mermaid` support via SuperFences.

## 3. Navigation Structure (Lifecycle-Based)
The documentation will be organized according to the development lifecycle:

1.  **🚀 Product**
    - PRD: `docs/prd/`
    - Requirements: `docs/requirements/`
2.  **📐 Architecture**
    - Domain Entities: `docs/domain/`
    - ADRs (Architectural Decision Records): `docs/adr/`
3.  **🛠️ Development**
    - Specs & Designs: `docs/superpowers/specs/`
    - Implementation Plans: `docs/superpowers/plans/`
    - Research: `docs/research/`
4.  **☁️ Infrastructure**
    - Cloud Setup & Guides: `docs/infra/`
5.  **📜 Changelog**
    - Daily Logs: `docs/logs/`

## 4. Visual Identity
- **Primary Color:** Deep Purple
- **Accent Color:** Deep Purple
- **Dark Mode:** Automatic system detection with manual toggle.
- **Features:**
    - Search: Instant global search.
    - Navigation: Section folding enabled.
    - Admonitions: Custom stylized boxes for notes, warnings, and tips.

## 5. Implementation Steps
1.  **Add Dependencies:** Use `uv add --dev mkdocs mkdocs-material pymdown-extensions`.
2.  **Configuration:** Create `mkdocs.yml` in the project root.
3.  **Index Page:** Create `docs/index.md` as the landing page.
4.  **Navigation Mapping:** Explicitly map files in `mkdocs.yml` to maintain the desired order.
5.  **Verification:** Run `mkdocs serve` to verify the setup.

## 6. Self-Review
- [x] **Placeholder scan:** No TBDs.
- [x] **Internal consistency:** Navigation structure matches existing folder layout.
- [x] **Scope check:** Focused strictly on MkDocs setup.
- [x] **Ambiguity check:** Colors and extensions are explicitly defined.
