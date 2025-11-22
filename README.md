# SMTP to REST API Translator

A Dockerized Python SMTP server that receives emails and forwards them to a RESTful API endpoint.

## Features

- **SMTP Server**: Listens for incoming SMTP connections
- **Email Parsing**: Extracts email content, headers, and attachments
- **Authentication Support**: Captures SMTP AUTH credentials (username/password)
- **REST API Forwarding**: Sends all email data as JSON to a configured API endpoint
- **Attachment Handling**: Base64-encodes attachments for API transmission
- **Client Metadata**: Includes client IP and other connection details

## Quick Start

### Using Docker Compose (Recommended)

1. Start the service:
```bash
docker-compose up -d
```

2. Stop the service:
```bash
docker-compose down
```

### Using Docker (Manual)

1. Build the Docker image:
```bash
docker build -t smtp2api .
```

2. Run the container:
```bash
docker run -p 8025:8025 -e API_URL=http://your-api-endpoint/api/email smtp2api
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the server:
```bash
python3 app/smtp_service.py
```

## Testing

A test script is included to verify the server functionality:

```bash
python3 tests/test_send.py
```

You can also use the included mock API server for testing:

```bash
# In one terminal
python3 tests/mock_api.py

# In another terminal
python3 app/smtp_service.py

# In a third terminal
python3 tests/test_send.py
```

## Security Notes

- The server is configured with `auth_require_tls=False` for development. In production, enable TLS.
- SMTP credentials are forwarded in plain text in the JSON payload. Ensure your API endpoint uses HTTPS.
- Consider implementing IP whitelisting or additional authentication for production use.

## License

MIT
