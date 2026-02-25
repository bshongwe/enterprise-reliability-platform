
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import httpx

app = FastAPI(title="Payments API", description="Handles payment initiation and orchestration.")

class PaymentRequest(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    reference: str

class PaymentResponse(BaseModel):
    payment_id: str
    status: str
    message: str

payments_db = {}

LEDGER_URL = "http://localhost:8001"  # Adjust as needed for deployment

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest):
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
        r = httpx.post(f"{LEDGER_URL}/entries", json=ledger_payload, timeout=5.0)
        r.raise_for_status()
        payments_db[payment_id]["status"] = "RECORDED"
        return PaymentResponse(payment_id=payment_id, status="RECORDED", message="Payment recorded in ledger.")
    except Exception as e:
        payments_db[payment_id]["status"] = "FAILED"
        return PaymentResponse(payment_id=payment_id, status="FAILED", message=f"Ledger error: {str(e)}")

@app.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    responses={404: {"description": "Payment not found"}}
)
def get_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse(payment_id=payment_id, status=payment["status"], message="Payment status fetched.")
