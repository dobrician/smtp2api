import base64
import logging
from email import policy
from email.parser import BytesParser as EmailBytesParser

logger = logging.getLogger(__name__)

class EmailParser:
    """
    Responsible for parsing raw email bytes into a structured dictionary.
    """
    
    def parse(self, content_bytes: bytes, mail_from: str, rcpt_tos: list, client_ip: str = None, auth_data: dict = None) -> dict:
        """
        Parses email content and constructs the payload.
        """
        try:
            # Parse the email content
            msg = EmailBytesParser(policy=policy.default).parsebytes(content_bytes)
            
            # Extract headers
            headers = {k: v for k, v in msg.items()}

            # Extract body and attachments
            body_text = ""
            body_html = ""
            attachments = []

            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            file_content = part.get_payload(decode=True)
                            attachments.append({
                                "filename": filename,
                                "content_type": content_type,
                                "content": base64.b64encode(file_content).decode('utf-8')
                            })
                    elif content_type == "text/plain" and "attachment" not in content_disposition:
                        body_text += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
                    elif content_type == "text/html" and "attachment" not in content_disposition:
                        body_html += part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
            else:
                # Single part
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='replace')
                if content_type == "text/plain":
                    body_text = payload
                elif content_type == "text/html":
                    body_html = payload

            # Construct payload
            payload = {
                "sender": mail_from,
                "recipients": rcpt_tos,
                "client_ip": client_ip,
                "subject": headers.get("Subject", ""),
                "headers": headers,
                "body_text": body_text,
                "body_html": body_html,
                "attachments": attachments,
                "auth_data": auth_data
            }
            
            return payload
            
        except Exception as e:
            logger.error(f"Failed to parse email: {e}", exc_info=True)
            raise
