FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY services/account_service/ ./services/account_service/

ENV PYTHONPATH=/app

EXPOSE 8002

CMD ["uvicorn", "services.account_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
