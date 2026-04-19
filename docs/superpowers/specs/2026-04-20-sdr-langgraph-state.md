# Spec: SDR LangGraph Conversation State

## Context
We are building an SDR (Sales Development Representative) assistant using LangGraph. The assistant needs to maintain state throughout the conversation, including tenant and customer identifiers, the message history, and information extracted from the user's intent.

## Requirements
- Define `SDRState` using `typing.TypedDict`.
- Support LangGraph's message history with `add_messages`.
- Store business-related identifiers (`tenant_id`, `customer_id`).
- Store a dictionary for information extracted during the flow (e.g., `service_id`, `professional_id`).
- Include a field for explicit routing (`next_node`).

## Proposed Design

### `SDRState` Schema
- `tenant_id`: `UUID`
- `customer_id`: `UUID`
- `messages`: `Annotated[list[BaseMessage], add_messages]`
- `extracted_info`: `dict[str, Any]`
- `next_node`: `str | None`

### Location
`src/amon_claw/infrastructure/llm/agents/state.py`

## Dependencies
- `langgraph.graph.add_messages`
- `langchain_core.messages.BaseMessage`
- `uuid.UUID`
- `typing.TypedDict`, `Annotated`, `Any`

## Verification Strategy
- Create the file and ensure it passes linting (ruff).
- Verify imports are valid.
- Test that the TypedDict can be instantiated.
