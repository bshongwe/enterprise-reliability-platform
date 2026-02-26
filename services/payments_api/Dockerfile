FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY services/payments_api/ ./services/payments_api/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "services.payments_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
