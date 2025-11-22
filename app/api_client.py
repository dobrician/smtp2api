import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)

class APIClient:
    """
    Handles HTTP communication with the target API using aiohttp.
    """
    
    def __init__(self, api_url: str):
        self.api_url = api_url

    async def send_email_payload(self, payload: dict):
        """
        Sends the email payload to the configured API endpoint asynchronously.
        """
        logger.info(f"Forwarding email to {self.api_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, timeout=10) as response:
                    response.raise_for_status()
                    logger.info(f"Successfully forwarded email. API Response: {response.status}")
                    return True
        except aiohttp.ClientError as e:
            logger.error(f"Failed to forward email to API: {e}")
            return False
        except asyncio.TimeoutError:
            logger.error(f"Timeout forwarding email to API {self.api_url}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error forwarding email: {e}", exc_info=True)
            return False
