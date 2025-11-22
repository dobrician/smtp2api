import asyncio
import os
import logging
import sentry_sdk
from aiosmtpd.controller import Controller
from dotenv import load_dotenv

from app.config import settings
from app.handlers import SMTPToAPIHandler
from app.parsers import EmailParser
from app.api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use settings
API_URL = settings.API_URL
SMTP_PORT = settings.SMTP_PORT
SMTP_HOST = settings.SMTP_HOST

class PermissiveAuthenticator:
    def __call__(self, server, session, envelope, mechanism, auth_data):
        fail_auth = 535
        
        method = mechanism.lower()
        username = None
        password = None
        
        if method == 'plain' or method == 'login':
            # auth_data is likely a LoginPassword namedtuple or similar
            try:
                if hasattr(auth_data, 'login') and hasattr(auth_data, 'password'):
                    username = auth_data.login
                    password = auth_data.password
                    # Decode if bytes
                    if isinstance(username, bytes):
                        username = username.decode('utf-8')
                    if isinstance(password, bytes):
                        password = password.decode('utf-8')
                else:
                    # Fallback for raw bytes if that ever happens
                    if isinstance(auth_data, bytes):
                        parts = auth_data.split(b'\0')
                        if len(parts) == 3:
                            username = parts[1].decode('utf-8')
                            password = parts[2].decode('utf-8')
            except Exception as e:
                logger.error(f"Error parsing auth_data: {e}")
                return fail_auth
        
        # Store credentials in server instance
        if not hasattr(server, 'my_auth_store'):
            server.my_auth_store = {}
            
        server.my_auth_store[id(session)] = {
            "username": username,
            "password": password,
            "mechanism": mechanism
        }
        
        return 235

def main():
    # Initialize Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            send_default_pii=True,
        )
        logger.info("Sentry initialized")
    
    # Dependency Injection
    email_parser = EmailParser()
    api_client = APIClient(api_url=API_URL)
    handler = SMTPToAPIHandler(api_client=api_client, email_parser=email_parser)
    
    authenticator = PermissiveAuthenticator()
    
    # Enable AUTH extension
    controller = Controller(
        handler, 
        hostname=SMTP_HOST, 
        port=SMTP_PORT,
        authenticator=authenticator,
        auth_required=False, # We accept mail even without auth, but if they auth, we capture it.
        auth_require_tls=False # For testing/dev. In prod, should be True.
    )
    
    logger.info(f"Starting SMTP server on {SMTP_HOST}:{SMTP_PORT}")
    logger.info(f"Forwarding emails to {API_URL}")
    
    controller.start()
    
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        logger.info("Stopping SMTP server")
        controller.stop()

if __name__ == "__main__":
    main()
