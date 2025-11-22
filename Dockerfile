FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Expose SMTP port
EXPOSE 8025

# Run the server
CMD ["python", "-m", "app.smtp_service"]
