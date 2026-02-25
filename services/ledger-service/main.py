from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

app = FastAPI(title="Ledger Service", description="Immutable transaction ledger for payments.")

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

@app.post("/entries", response_model=LedgerEntryResponse)
def create_ledger_entry(entry: LedgerEntryCreate):
    db = SessionLocal()
    db_entry = LedgerEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    db.close()
    return db_entry

@app.get("/entries/{payment_id}", response_model=List[LedgerEntryResponse])
def get_entries_by_payment(payment_id: str):
    db = SessionLocal()
    entries = db.query(LedgerEntry).filter(LedgerEntry.payment_id == payment_id).all()
    db.close()
    if not entries:
        raise HTTPException(status_code=404, detail="No ledger entries found for this payment_id")
    return entries
