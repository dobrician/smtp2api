import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_test_email():
    sender_email = "test@example.com"
    receiver_email = "recipient@example.com"
    password = "password123"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Test Email with Attachment and Auth"

    body = "This is a test email sent to the Python SMTP server."
    message.attach(MIMEText(body, "plain"))

    # Attachment
    filename = "test.txt"
    attachment_content = "This is a text attachment."
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment_content.encode('utf-8'))
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(part)

    text = message.as_string()

    try:
        # Connect to the server
        server = smtplib.SMTP("localhost", 8025)
        server.set_debuglevel(1)
        
        # Identify
        server.ehlo()
        
        # Auth
        # Note: Our server is configured to accept PLAIN auth even without TLS for testing
        # But smtplib might refuse to send credentials over plain text without TLS unless we force it or use localhost?
        # smtplib usually allows it on localhost.
        try:
            server.login(sender_email, password)
            print("Authentication successful")
        except Exception as e:
            print(f"Authentication failed (expected if not fully implemented or strict): {e}")

        # Send email
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

if __name__ == "__main__":
    send_test_email()
