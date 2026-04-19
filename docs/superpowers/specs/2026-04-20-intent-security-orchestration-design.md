# Spec: Intent and Security Orchestration for SDR Graph

## Context
To ensure a robust, deterministic, and secure scheduling experience, we are implementing a "Security First" orchestration layer within the LangGraph-based SDR assistant. This layer filters user input to prevent "papo furado" (off-topic chatter), prompt injection, and other malicious behaviors, notifying developers and owners when critical issues arise.

## Goals
- **Determinism:** Ensure the conversation stays focused on scheduling.
- **Security:** Detect and block prompt injection or inappropriate content.
- **Observability:** Notify developers and business owners of security events or persistent off-topic behavior.
- **Robustness:** Use a modular graph structure to handle non-linear interactions safely.

## Proposed Design

### 1. Updated `SDRState`
The state will be expanded to include tracking for intent and security flags.
- `intent_type`: (str) e.g., 'scheduling', 'greeting', 'off_topic', 'human_request'.
- `security_flag`: (str) e.g., 'none', 'potential_injection', 'inappropriate'.
- `off_topic_count`: (int) Counter for consecutive off-topic messages.

### 2. New Graph Nodes
- **`IntentSecurityNode`:**
    - **Purpose:** First point of contact for user messages.
    - **Logic:** Uses an LLM/classifier to determine `intent_type` and `security_flag`.
    - **Routing:** 
        - If `security_flag != 'none'` -> `SecurityActionNode`.
        - If `intent_type == 'scheduling'` -> `SchedulingCoreNode`.
        - Else -> `OffTopicResponderNode`.
- **`OffTopicResponderNode`:**
    - **Purpose:** Politely redirect the user to the scheduling goal.
    - **Logic:** Increments `off_topic_count`. If `off_topic_count > threshold` (e.g., 3), routes to `SecurityActionNode`.
- **`SecurityActionNode`:**
    - **Purpose:** Handle threats and persistent off-topic behavior.
    - **Logic:** Sends a final generic message to the user and triggers high-priority notifications (logs/webhooks) containing `tenant_id`, `customer_id`, and the malicious message content.
    - **End State:** This is a terminal node.

### 3. Notification Payload
When `SecurityActionNode` is triggered:
- **Tenant ID / Customer ID**
- **Security Flag / Reason**
- **Message History Snippet** (last 3 messages)
- **Timestamp**

## Technical Constraints
- Must use `langgraph` and `Pydantic AI` for deterministic execution.
- Security checks should be lightweight to minimize latency.
- Notifications must be asynchronous to avoid blocking the user response (even if terminal).

## Verification Strategy
- **Unit Tests:** Verify `IntentSecurityNode` correctly classifies known injection patterns.
- **Integration Tests:** Ensure `off_topic_count` increments and triggers the security node at the threshold.
- **Manual QA:** Attempt prompt injections and verify that notifications are sent and the session ends.
