FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY services/ledger_service/ ./services/ledger_service/

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "services.ledger_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
