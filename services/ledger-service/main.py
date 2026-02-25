#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List
from services.ledger_service.models import LedgerEntryCreate, LedgerEntryResponse
from common.auth import get_api_key
from services.ledger_service.service import create_ledger_entry, get_entries_by_payment

app = FastAPI(
    title="Ledger Service",
    description="Immutable transaction ledger for payments."
)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post(
    "/entries",
    response_model=LedgerEntryResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_ledger_entry_endpoint(entry: LedgerEntryCreate, request: Request):
    user = request.headers.get('X-API-Key', '?')
    try:
        db_entry = create_ledger_entry(entry, user)
        return db_entry
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get(
    "/entries/{payment_id}",
    response_model=List[LedgerEntryResponse],
    responses={
        404: {"description": "No ledger entries found for this payment_id"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_entries_by_payment_endpoint(payment_id: str, request: Request):
    user = request.headers.get('X-API-Key', '?')
    try:
        entries = get_entries_by_payment(payment_id, user)
        if not entries:
            raise HTTPException(
                status_code=404,
                detail="No ledger entries found for this payment_id"
            )
        return entries
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
