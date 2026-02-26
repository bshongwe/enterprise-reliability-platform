#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Annotated
from prometheus_client import make_asgi_app
from services.account_service.models import (
    AccountCreate,
    AccountResponse,
    AccountUpdate,
    BalanceUpdate,
    AccountStatus
)
from common.auth import get_api_key
from common.metrics import http_requests_total
from services.account_service.service import (
    create_account,
    get_account,
    update_balance,
    get_user_accounts
)

app = FastAPI(
    title="Account Service",
    description="Manages user accounts and balances."
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post(
    "/accounts",
    response_model=AccountResponse,
    dependencies=[Depends(get_api_key)],
    responses={500: {"description": "Internal server error"}}
)
def create_account_endpoint(
    account: AccountCreate,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        db_account = create_account(account, user_id)
        return db_account
    except Exception:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        http_requests_total.labels(
            service="account",
            method="POST",
            endpoint="/accounts",
            status=status
        ).inc()


@app.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    responses={
        404: {"description": "Account not found"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def get_account_endpoint(
    account_id: str,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        account = get_account(account_id, user_id)
        if not account:
            status = "not_found"
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        return account
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
            service="account",
            method="GET",
            endpoint="/accounts/{account_id}",
            status=status
        ).inc()


@app.post(
    "/accounts/{account_id}/balance",
    response_model=AccountResponse,
    responses={
        404: {"description": "Account not found"},
        400: {"description": "Insufficient funds"},
        500: {"description": "Internal server error"}
    },
    dependencies=[Depends(get_api_key)]
)
def update_balance_endpoint(
    account_id: str,
    balance_update: BalanceUpdate,
    user_id: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        account = update_balance(account_id, balance_update, user_id)
        if not account:
            status = "not_found"
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        return account
    except ValueError as e:
        status = "error"
        raise HTTPException(status_code=400, detail=str(e))
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
            service="account",
            method="POST",
            endpoint="/accounts/{account_id}/balance",
            status=status
        ).inc()


@app.get(
    "/users/{user_id}/accounts",
    response_model=List[AccountResponse],
    responses={500: {"description": "Internal server error"}},
    dependencies=[Depends(get_api_key)]
)
def get_user_accounts_endpoint(
    user_id: str,
    auth_user: Annotated[str, Depends(get_api_key)]
):
    status = "success"
    try:
        accounts = get_user_accounts(user_id, auth_user)
        return accounts
    except Exception:
        status = "error"
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        http_requests_total.labels(
            service="account",
            method="GET",
            endpoint="/users/{user_id}/accounts",
            status=status
        ).inc()
