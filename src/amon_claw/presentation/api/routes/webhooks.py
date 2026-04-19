import logging
from fastapi import APIRouter, Request, Form, Response
from typing import Dict, Any

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
    Expects application/x-www-form-urlencoded data.
    """
    logger.info(f"Received Twilio message for tenant {tenant_id}: From={From}, Body={Body}, SID={MessageSid}")
    
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
    Expects application/json data.
    """
    logger.info(f"Received Evolution payload for tenant {tenant_id}: {payload}")
    
    # Basic filtering as per spec
    event = payload.get("event")
    if event == "messages.upsert":
        data = payload.get("data", {})
        key = data.get("key", {})
        from_me = key.get("fromMe")
        
        if not from_me:
            message = data.get("message", {})
            # This is a simplification; in a real scenario we'd handle different message types
            text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text")
            logger.info(f"Evolution message from {key.get('remoteJid')}: {text}")

    return {"status": "success"}
