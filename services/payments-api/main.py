#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
import logging
from pydantic import BaseModel, validator
from typing import List
import httpx


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI(title="Payments API", description="Handles payment initiation and orchestration.")

# Simple API key auth (replace with OAuth/JWT for production)
API_KEY = "supersecretkey"  # Set securely in prod
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key


class PaymentRequest(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    reference: str

    @validator('amount')
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('currency')
    def currency_allowed(cls, v):
        allowed = {"ZAR", "USD", "EUR", "GBP"}
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v


class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str


payments_db = {}


LEDGER_URL = "http://localhost:8001"  # Adjust as needed for deployment


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post(
    "/payments",
    response_model=PaymentResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_payment(payment: PaymentRequest, request: Request):
    payment_id = f"pay_{len(payments_db)+1}"
    payments_db[payment_id] = {**payment.dict(), "status": "PENDING"}
    ledger_payload = {
        "payment_id": payment_id,
        "sender_account": payment.sender_account,
        "receiver_account": payment.receiver_account,
        "amount": payment.amount,
        "currency": payment.currency,
        "reference": payment.reference
    }
    try:
        r = httpx.post(f"{LEDGER_URL}/entries", json=ledger_payload, headers={"X-API-Key": API_KEY}, timeout=5.0)
        r.raise_for_status()
        payments_db[payment_id]["status"] = "RECORDED"
        logging.info(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=create_payment payment_id={payment_id} status=success")
        return PaymentResponse(payment_id=payment_id, status="RECORDED", message="Payment recorded in ledger.")
    except Exception as e:
        payments_db[payment_id]["status"] = "FAILED"
        logging.error(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=create_payment payment_id={payment_id} status=fail error={type(e).__name__}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    responses={
        404: {"description": "Payment not found"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_payment(payment_id: str, request: Request):
    try:
        payment = payments_db.get(payment_id)
        if not payment:
            logging.warning(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_payment payment_id={payment_id} status=not_found")
            raise HTTPException(status_code=404, detail="Payment not found")
        logging.info(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_payment payment_id={payment_id} status=success")
        return PaymentResponse(payment_id=payment_id, status=payment["status"], message="Payment status fetched.")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_payment payment_id={payment_id} status=fail error={type(e).__name__}")
        raise HTTPException(status_code=500, detail="Internal server error")
