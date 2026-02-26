from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from models import LedgerEntryCreate
from common.audit import audit_log
from common.metrics import db_operations_total

DATABASE_URL = "sqlite:///./ledger.db"
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
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

def create_ledger_entry(entry: LedgerEntryCreate, user: str):
    db = SessionLocal()
    try:
        db_entry = LedgerEntry(**entry.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        db_operations_total.labels(
            service="ledger",
            operation="write",
            status="success"
        ).inc()
        audit_log(user, "create_ledger_entry", entry.payment_id, "success")
        return db_entry
    except Exception as e:
        db.rollback()
        db_operations_total.labels(
            service="ledger",
            operation="write",
            status="error"
        ).inc()
        audit_log(
            user, "create_ledger_entry", entry.payment_id, "fail",
            f"error={type(e).__name__}"
        )
        raise
    finally:
        db.close()

def get_entries_by_payment(payment_id: str, user: str):
    db = SessionLocal()
    try:
        entries = db.query(LedgerEntry).filter(
            LedgerEntry.payment_id == payment_id
        ).all()
        if not entries:
            audit_log(user, "get_entries_by_payment", payment_id, "not_found")
            return None
        audit_log(
            user, "get_entries_by_payment", payment_id, "success",
            f"count={len(entries)}"
        )
        return entries
    except Exception as e:
        audit_log(
            user, "get_entries_by_payment", payment_id, "fail",
            f"error={type(e).__name__}"
        )
        raise
    finally:
        db.close()
