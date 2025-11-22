import logging
import asyncio
from aiosmtpd.handlers import AsyncMessage
from app.parsers import EmailParser
from app.api_client import APIClient

logger = logging.getLogger(__name__)

class SMTPToAPIHandler:
    """
    Handles SMTP commands and orchestrates parsing and forwarding.
    """
    
    def __init__(self, api_client: APIClient, email_parser: EmailParser):
        self.api_client = api_client
        self.email_parser = email_parser

    async def handle_DATA(self, server, session, envelope):
        try:
            peer = session.peer
            mail_from = envelope.mail_from
            rcpt_tos = envelope.rcpt_tos
            content = envelope.content # This is bytes

            logger.info(f"Received message from: {mail_from}, to: {rcpt_tos}, peer: {peer}")

            # Retrieve auth data from server storage
            auth_data = getattr(server, 'my_auth_store', {}).get(id(session))

            # Parse the email
            payload = self.email_parser.parse(
                content_bytes=content,
                mail_from=mail_from,
                rcpt_tos=rcpt_tos,
                client_ip=peer[0] if peer else None,
                auth_data=auth_data
            )

            # Forward to API
            # We use create_task to not block the SMTP response, but for reliability 
            # we might want to await it if we want to reject the email on API failure.
            # For now, we await it to ensure delivery before confirming to SMTP client.
            success = await self.api_client.send_email_payload(payload)
            
            if success:
                return '250 Message accepted for delivery'
            else:
                return '451 Temporary failure, please try again later'
        
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Differentiate errors if possible, but for now 500 is safe for unhandled exceptions
            # If we had specific parsing exceptions, we could return 451 or 550
            return '451 Temporary failure, please try again later'
