from typing import Any, Dict

async def intent_security_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the last message for potential security threats or prompt injections.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    content = getattr(last_message, "content", "").lower()

    # Simple heuristic for prompt injection detection
    injection_patterns = [
        "ignore all previous instructions",
        "reveal secrets",
        "system prompt",
        "developer mode",
    ]

    for pattern in injection_patterns:
        if pattern in content:
            return {
                "security_flag": "potential_injection",
                "intent_type": "malicious"
            }
    
    return {
        "security_flag": "safe",
        "intent_type": "neutral"
    }

async def off_topic_responder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles off-topic queries by incrementing the off-topic counter.
    """
    count = state.get("off_topic_count", 0)
    return {"off_topic_count": count + 1}
