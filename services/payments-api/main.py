from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

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

# In-memory store for demo purposes
payments_db = {}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest):
    # In production, add validation, fraud checks, etc.
    payment_id = f"pay_{len(payments_db)+1}"
    payments_db[payment_id] = {**payment.dict(), "status": "PENDING"}
    # Here, you would call the Ledger service to record the transaction
    return PaymentResponse(payment_id=payment_id, status="PENDING", message="Payment initiated.")

@app.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str):
    payment = payments_db.get(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse(payment_id=payment_id, status=payment["status"], message="Payment status fetched.")
