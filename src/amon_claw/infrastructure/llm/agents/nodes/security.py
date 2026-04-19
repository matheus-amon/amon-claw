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
    
    # Simple heuristic for off-topic detection (for testing and basic use cases)
    off_topic_keywords = ["joke", "weather", "news", "music"]
    for keyword in off_topic_keywords:
        if keyword in content:
            return {
                "security_flag": "safe",
                "intent_type": "off_topic"
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

async def security_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles identified security threats by sending alerts and preparing a defensive response.
    """
    from amon_claw.infrastructure.notifications.alerts import send_security_alert
    
    await send_security_alert(state)
    
    return {
        "messages": state.get("messages", []) + [
            {
                "role": "assistant",
                "content": "I apologize, but I cannot fulfill this request due to security policy violations."
            }
        ]
    }
