from pydantic import BaseModel, validator

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
