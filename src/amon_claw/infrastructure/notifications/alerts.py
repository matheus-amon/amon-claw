import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

async def send_security_alert(state: Dict[str, Any]) -> None:
    """
    Sends a security alert notification based on the current state.
    Currently, it logs a CRITICAL alert.
    """
    tenant_id = state.get("tenant_id", "unknown")
    customer_id = state.get("customer_id", "unknown")
    security_flag = state.get("security_flag", "no_flag")
    
    alert_msg = f"SECURITY ALERT: {security_flag} detected for tenant {tenant_id} and customer {customer_id}"
    logger.critical(alert_msg)
