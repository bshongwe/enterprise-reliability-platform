import os
import httpx
from services.payments_api.models import PaymentRequest
from common.audit import audit_log

LEDGER_URL = os.getenv("LEDGER_URL", "http://localhost:8001")
API_KEY = os.getenv("API_KEY", "")

payments_db = {}

def create_payment_record(payment: PaymentRequest, user: str):
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
        r = httpx.post(
            f"{LEDGER_URL}/entries",
            json=ledger_payload,
            headers={"X-API-Key": API_KEY},
            timeout=5.0
        )
        r.raise_for_status()
        payments_db[payment_id]["status"] = "RECORDED"
        audit_log(user, "create_payment", payment_id, "success")
        return payment_id, "RECORDED", "Payment recorded in ledger."
    except Exception as e:
        payments_db[payment_id]["status"] = "FAILED"
        audit_log(
            user,
            "create_payment",
            payment_id,
            "fail",
            f"error={type(e).__name__}"
        )
        raise

def get_payment_record(payment_id: str, user: str):
    payment = payments_db.get(payment_id)
    if not payment:
        audit_log(user, "get_payment", payment_id, "not_found")
        return None
    audit_log(user, "get_payment", payment_id, "success")
    return payment
