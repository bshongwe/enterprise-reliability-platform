#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from prometheus_client import make_asgi_app
from services.payments_api.models import (
    PaymentRequest,
    PaymentResponse
)
from common.auth import get_api_key
from common.metrics import http_requests_total
from services.payments_api.service import (
    create_payment_record,
    get_payment_record
)


app = FastAPI(
    title="Payments API",
    description="Handles payment initiation and orchestration."
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post(
    "/payments",
    response_model=PaymentResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_payment(
    payment: PaymentRequest,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        payment_id, pmt_status, message = create_payment_record(
            payment,
            user_id
        )
        return PaymentResponse(
            payment_id=payment_id,
            status=pmt_status,
            message=message
        )
    except Exception:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        http_requests_total.labels(
            service="payments",
            method="POST",
            endpoint="/payments",
            status=status
        ).inc()


@app.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
    responses={
        404: {"description": "Payment not found"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_payment(
    payment_id: str,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        payment = get_payment_record(payment_id, user_id)
        if not payment:
            status = "not_found"
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )
        return PaymentResponse(
            payment_id=payment_id,
            status=payment["status"],
            message="Payment status fetched."
        )
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
            service="payments",
            method="GET",
            endpoint="/payments/{payment_id}",
            status=status
        ).inc()
