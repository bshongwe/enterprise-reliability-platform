from pydantic import BaseModel, validator
from enum import Enum
from typing import Optional
import datetime


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class AccountType(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"
    BUSINESS = "business"


class AccountCreate(BaseModel):
    user_id: str
    account_type: AccountType
    currency: str
    initial_balance: float = 0.0

    @validator('initial_balance')
    def balance_non_negative(cls, v):
        if v < 0:
            raise ValueError('Initial balance cannot be negative')
        return v

    @validator('currency')
    def currency_allowed(cls, v):
        allowed = {"ZAR", "USD", "EUR", "GBP"}
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v


class AccountResponse(BaseModel):
    account_id: str
    user_id: str
    account_type: AccountType
    currency: str
    balance: float
    status: AccountStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime


class AccountUpdate(BaseModel):
    status: Optional[AccountStatus] = None


class BalanceUpdate(BaseModel):
    amount: float
    operation: str
    reference: str

    @validator('operation')
    def operation_valid(cls, v):
        if v not in ["credit", "debit"]:
            raise ValueError('Operation must be credit or debit')
        return v
