#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from prometheus_client import make_asgi_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from services.notification_api.models import (
    NotificationRequest,
    NotificationResponse
)
from common.auth import get_api_key
from common.metrics import http_requests_total
from services.notification_api.service import send_notification

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Notification API",
    description="Handles Slack/email notification delivery."
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post(
    "/notifications",
    response_model=NotificationResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
@limiter.limit("10/minute")
def send_notification_endpoint(
    notification: NotificationRequest,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        notification_id, delivery_status = send_notification(
            notification,
            user_id
        )
        return NotificationResponse(
            notification_id=notification_id,
            status=delivery_status,
            message="Notification sent"
        )
    except Exception as e:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from e
    finally:
        http_requests_total.labels(
            service="notification",
            method="POST",
            endpoint="/notifications",
            status=status
        ).inc()
