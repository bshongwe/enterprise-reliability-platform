FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY services/notification-api/ ./services/notification-api/

ENV PYTHONPATH=/app

EXPOSE 8003

CMD ["uvicorn", "services.notification-api.main:app", "--host", "0.0.0.0", "--port", "8003"]
