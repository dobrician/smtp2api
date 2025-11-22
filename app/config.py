import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """
    Centralized configuration management.
    """
    API_URL: str = os.getenv('API_URL', 'http://localhost:8000/api/email')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', 8025))
    SMTP_HOST: str = os.getenv('SMTP_HOST', '0.0.0.0')
    SENTRY_DSN: str = os.getenv('SENTRY_DSN', '')

settings = Settings()
