from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
import logging
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI(title="Ledger Service", description="Immutable transaction ledger for payments.")

# Simple API key auth (replace with OAuth/JWT for production)
API_KEY = "supersecretkey"  # Set securely in prod
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key

DATABASE_URL = "sqlite:///./ledger.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, index=True)
    sender_account = Column(String)
    receiver_account = Column(String)
    amount = Column(Float)
    currency = Column(String)
    reference = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

class LedgerEntryCreate(BaseModel):
    payment_id: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    reference: str

    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
    
    @classmethod
    def validate_currency(cls, v):
        allowed = {"ZAR", "USD", "EUR", "GBP"}
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v

class LedgerEntryResponse(BaseModel):
    id: int
    payment_id: str
    sender_account: str
    receiver_account: str
    amount: float
    currency: str
    reference: str
    timestamp: datetime.datetime

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post(
    "/entries",
    response_model=LedgerEntryResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_ledger_entry(entry: LedgerEntryCreate, request: Request):
    db = SessionLocal()
    try:
        # Input validation
        LedgerEntryCreate.validate_amount(entry.amount)
        LedgerEntryCreate.validate_currency(entry.currency)
        db_entry = LedgerEntry(**entry.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        logging.info(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=create_ledger_entry payment_id={entry.payment_id} status=success")
        return db_entry
    except Exception as e:
        db.rollback()
        logging.error(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=create_ledger_entry payment_id={entry.payment_id} status=fail error={type(e).__name__}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()

@app.get(
    "/entries/{payment_id}",
    response_model=List[LedgerEntryResponse],
    responses={
        404: {"description": "No ledger entries found for this payment_id"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_entries_by_payment(payment_id: str, request: Request):
    db = SessionLocal()
    try:
        entries = db.query(LedgerEntry).filter(LedgerEntry.payment_id == payment_id).all()
        if not entries:
            logging.warning(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_entries_by_payment payment_id={payment_id} status=not_found")
            raise HTTPException(status_code=404, detail="No ledger entries found for this payment_id")
        logging.info(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_entries_by_payment payment_id={payment_id} status=success count={len(entries)}")
        return entries
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"AUDIT: user={request.headers.get('X-API-Key','?')} action=get_entries_by_payment payment_id={payment_id} status=fail error={type(e).__name__}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db.close()
