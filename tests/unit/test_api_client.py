import pytest
from aioresponses import aioresponses
from app.api_client import APIClient

@pytest.fixture
def api_client():
    return APIClient(api_url="http://test-api.com/email")

@pytest.mark.asyncio
async def test_send_email_payload_success(api_client):
    payload = {"sender": "test@example.com", "subject": "Test"}
    
    with aioresponses() as m:
        m.post("http://test-api.com/email", status=200)
        
        result = await api_client.send_email_payload(payload)
        assert result is True

@pytest.mark.asyncio
async def test_send_email_payload_failure(api_client):
    payload = {"sender": "test@example.com", "subject": "Test"}
    
    with aioresponses() as m:
        m.post("http://test-api.com/email", status=500)
        
        result = await api_client.send_email_payload(payload)
        assert result is False

@pytest.mark.asyncio
async def test_send_email_payload_timeout(api_client):
    payload = {"sender": "test@example.com", "subject": "Test"}
    
    with aioresponses() as m:
        m.post("http://test-api.com/email", timeout=True)
        
        result = await api_client.send_email_payload(payload)
        assert result is False
