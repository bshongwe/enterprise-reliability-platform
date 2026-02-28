FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY services/notification_api/ ./services/notification_api/

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["uvicorn", "services.notification_api.main:app", "--host", "0.0.0.0", "--port", "8002"]
