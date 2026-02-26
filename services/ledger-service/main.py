#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Annotated
from prometheus_client import make_asgi_app
from services.ledger_service.models import (
    LedgerEntryCreate,
    LedgerEntryResponse
)
from common.auth import get_api_key
from common.metrics import http_requests_total, db_operations_total
from services.ledger_service.service import (
    create_ledger_entry,
    get_entries_by_payment
)

app = FastAPI(
    title="Ledger Service",
    description="Immutable transaction ledger for payments."
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post(
    "/entries",
    response_model=LedgerEntryResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_ledger_entry_endpoint(
    entry: LedgerEntryCreate,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        db_entry = create_ledger_entry(entry, user_id)
        return db_entry
    except Exception:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        http_requests_total.labels(
            service="ledger",
            method="POST",
            endpoint="/entries",
            status=status
        ).inc()

@app.get(
    "/entries/{payment_id}",
    response_model=List[LedgerEntryResponse],
    responses={
        404: {
            "description": "No ledger entries found for this payment_id"
        },
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_entries_by_payment_endpoint(
    payment_id: str,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        entries = get_entries_by_payment(payment_id, user_id)
        if not entries:
            status = "not_found"
            raise HTTPException(
                status_code=404,
                detail="No ledger entries found for this payment_id"
            )
        return entries
    except HTTPException:
        raise
    except Exception:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        http_requests_total.labels(
            service="ledger",
            method="GET",
            endpoint="/entries/{payment_id}",
            status=status
        ).inc()
