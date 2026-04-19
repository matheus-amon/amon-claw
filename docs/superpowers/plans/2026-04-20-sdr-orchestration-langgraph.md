# SDR Orchestration (LangGraph) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the core conversation graph using LangGraph to manage the SDR flow (Greeting -> Info Gathering -> Scheduling).

**Architecture:** Use a StateGraph with a shared `SDRState`. Micro-agents (nodes) will be implemented using Pydantic AI for deterministic tool calling. Persistence will use a MongoDB checkpointer.

**Tech Stack:** Python 3.12, LangGraph, Pydantic AI, MongoDB.

---

### Task 1: Define Conversation State & Schema

- [ ] **Step 1: Define `SDRState` in `infrastructure/llm/agents/state.py`**
Include fields for `tenant_id`, `customer_id`, `chat_history`, `extracted_info` (service, professional, time).

---

### Task 2: Implement Base Graph Structure

- [ ] **Step 1: Create the graph entry point in `infrastructure/llm/agents/sdr_graph.py`**
- [ ] **Step 2: Add basic nodes: `greeting`, `collect_info`, `check_availability`, `finalize_booking`**
- [ ] **Step 3: Define edges and conditional routing**

---

### Task 3: Node Implementation (Micro-Agents)

- [ ] **Step 1: Implement `collect_info` node using Pydantic AI**
Define tools for listing services and professionals using the repositories created in the previous phase.

---

### Task 4: Integration & Testing

- [ ] **Step 1: Create a CLI test script to simulate a conversation**
- [ ] **Step 2: Verify state persistence in MongoDB between turns**
