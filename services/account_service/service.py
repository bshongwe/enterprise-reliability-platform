from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import uuid
from datetime import timezone
from services.account_service.models import (
    AccountCreate,
    AccountStatus,
    AccountType,
    BalanceUpdate
)
from common.audit import audit_log
from common.metrics import db_operations_total


DATABASE_URL = os.getenv(
    "ACCOUNT_DB_URL", "sqlite:///./accounts.db"
)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    account_type = Column(SQLEnum(AccountType))
    currency = Column(String)
    balance = Column(Float, default=0.0)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime, default=lambda: datetime.datetime.now(timezone.utc)
    )


Base.metadata.create_all(bind=engine)


def create_account(account: AccountCreate, user: str):
    db = SessionLocal()
    try:
        account_id = f"ACC{uuid.uuid4().hex[:10].upper()}"
        db_account = Account(
            account_id=account_id,
            user_id=account.user_id,
            account_type=account.account_type,
            currency=account.currency,
            balance=account.initial_balance,
            status=AccountStatus.ACTIVE
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        db_operations_total.labels(
            service="account",
            operation="create",
            status="success"
        ).inc()
        audit_log(user, "create_account", account_id, "success")
        return db_account
    except Exception as e:
        db.rollback()
        db_operations_total.labels(
            service="account",
            operation="create",
            status="error"
        ).inc()
        audit_log(
            user, "create_account", account.user_id, "fail",
            f"error={type(e).__name__}"
        )
        raise
    finally:
        db.close()


def get_account(account_id: str, user: str):
    db = SessionLocal()
    try:
        account = db.query(Account).filter(
            Account.account_id == account_id
        ).first()
        if account:
            audit_log(user, "get_account", account_id, "success")
        else:
            audit_log(user, "get_account", account_id, "not_found")
        return account
    finally:
        db.close()


def update_balance(
    account_id: str, balance_update: BalanceUpdate, user: str
):
    db = SessionLocal()
    try:
        account = db.query(Account).filter(
            Account.account_id == account_id
        ).first()
        if not account:
            audit_log(user, "update_balance", account_id, "not_found")
            return None

        if balance_update.operation == "credit":
            account.balance += balance_update.amount
        else:
            if account.balance < balance_update.amount:
                audit_log(
                    user, "update_balance", account_id, "fail",
                    "insufficient_funds"
                )
                raise ValueError("Insufficient funds")
            account.balance -= balance_update.amount

        account.updated_at = datetime.datetime.now(timezone.utc)
        db.commit()
        db.refresh(account)
        db_operations_total.labels(
            service="account",
            operation="update_balance",
            status="success"
        ).inc()
        audit_log(
            user, "update_balance", account_id, "success",
            f"op={balance_update.operation},amt={balance_update.amount}"
        )
        return account
    except Exception as e:
        db.rollback()
        db_operations_total.labels(
            service="account",
            operation="update_balance",
            status="error"
        ).inc()
        audit_log(
            user, "update_balance", account_id, "fail",
            f"error={type(e).__name__}"
        )
        raise
    finally:
        db.close()


def get_user_accounts(user_id: str, user: str):
    db = SessionLocal()
    try:
        accounts = db.query(Account).filter(
            Account.user_id == user_id
        ).all()
        audit_log(
            user, "get_user_accounts", user_id, "success",
            f"count={len(accounts)}"
        )
        return accounts
    finally:
        db.close()
