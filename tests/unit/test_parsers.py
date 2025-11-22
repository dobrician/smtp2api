import pytest
import base64
from email.message import EmailMessage
from app.parsers import EmailParser

@pytest.fixture
def parser():
    return EmailParser()

def test_parse_simple_text_email(parser):
    # Create a simple text email
    msg = EmailMessage()
    msg.set_content("Hello World")
    msg["Subject"] = "Test Subject"
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    
    content_bytes = msg.as_bytes()
    
    payload = parser.parse(
        content_bytes=content_bytes,
        mail_from="sender@example.com",
        rcpt_tos=["recipient@example.com"]
    )
    
    assert payload["sender"] == "sender@example.com"
    assert payload["recipients"] == ["recipient@example.com"]
    assert payload["subject"] == "Test Subject"
    assert "Hello World" in payload["body_text"]
    assert payload["body_html"] == ""
    assert len(payload["attachments"]) == 0

def test_parse_email_with_attachment(parser):
    # Create email with attachment
    msg = EmailMessage()
    msg.set_content("Please see attached.")
    msg["Subject"] = "Attachment Test"
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    
    # Add attachment
    file_content = b"This is a test file"
    msg.add_attachment(
        file_content,
        maintype="application",
        subtype="octet-stream",
        filename="test.txt"
    )
    
    content_bytes = msg.as_bytes()
    
    payload = parser.parse(
        content_bytes=content_bytes,
        mail_from="sender@example.com",
        rcpt_tos=["recipient@example.com"]
    )
    
    assert len(payload["attachments"]) == 1
    attachment = payload["attachments"][0]
    assert attachment["filename"] == "test.txt"
    assert attachment["content"] == base64.b64encode(file_content).decode('utf-8')

def test_parse_html_email(parser):
    # Create HTML email
    msg = EmailMessage()
    msg.set_content("Plain text fallback")
    msg.add_alternative("<h1>Hello HTML</h1>", subtype="html")
    msg["Subject"] = "HTML Test"
    
    content_bytes = msg.as_bytes()
    
    payload = parser.parse(
        content_bytes=content_bytes,
        mail_from="sender@example.com",
        rcpt_tos=["recipient@example.com"]
    )
    
    assert "<h1>Hello HTML</h1>" in payload["body_html"]
    assert "Plain text fallback" in payload["body_text"]
