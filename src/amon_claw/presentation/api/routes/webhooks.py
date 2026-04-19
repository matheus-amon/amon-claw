import logging
from fastapi import APIRouter, Request, Form, Response, HTTPException
from typing import Dict, Any

from amon_claw.infrastructure.database.mongodb.models.tenant import TenantDocument
from amon_claw.infrastructure.llm.agents.sdr_graph import sdr_assistant
from amon_claw.infrastructure.llm.tools.messaging_client import get_messaging_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])

@router.post("/twilio/{tenant_id}")
async def twilio_webhook(
    tenant_id: str,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """
    Webhook for Twilio WhatsApp messages.
    """
    logger.info(f"Received Twilio message for tenant {tenant_id}: From={From}, Body={Body}, SID={MessageSid}")
    
    tenant = await TenantDocument.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Invoke LangGraph
    config = {"configurable": {"thread_id": From}}
    input_state = {"messages": [("user", Body)]}
    result = await sdr_assistant.ainvoke(input_state, config=config)
    
    # Send response back
    last_message = result["messages"][-1]
    if last_message.type == "assistant":
        client = get_messaging_client(tenant.messaging_config.provider)
        # Convert TenantMessagingConfig to dict for the client
        config_dict = tenant.messaging_config.model_dump()
        await client.send_text(to=From, text=last_message.content, config=config_dict)

    # Return an empty TwiML response to acknowledge receipt
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    return Response(content=twiml, media_type="text/xml")

@router.post("/evolution/{tenant_id}")
async def evolution_webhook(
    tenant_id: str,
    payload: Dict[str, Any]
):
    """
    Webhook for Evolution API WhatsApp messages.
    """
    logger.info(f"Received Evolution payload for tenant {tenant_id}: {payload}")
    
    # Basic filtering as per spec
    event = payload.get("event")
    if event != "messages.upsert":
        return {"status": "ignored"}

    data = payload.get("data", {})
    key = data.get("key", {})
    from_me = key.get("fromMe")
    
    if from_me:
        return {"status": "ignored"}

    tenant = await TenantDocument.get(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    remote_jid = key.get("remoteJid")
    message = data.get("message", {})
    text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text")
    
    if text:
        # Invoke LangGraph
        config = {"configurable": {"thread_id": remote_jid}}
        input_state = {"messages": [("user", text)]}
        result = await sdr_assistant.ainvoke(input_state, config=config)
        
        # Send response back
        last_message = result["messages"][-1]
        if last_message.type == "assistant":
            client = get_messaging_client(tenant.messaging_config.provider)
            config_dict = tenant.messaging_config.model_dump()
            await client.send_text(to=remote_jid, text=last_message.content, config=config_dict)

    return {"status": "success"}

