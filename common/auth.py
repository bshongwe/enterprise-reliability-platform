import os
from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from passlib.context import CryptContext

API_KEY = os.getenv("API_KEY", "")
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_api_key(api_key: str = Depends(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Return a sanitized identifier for logging/audit purposes
    return pwd_context.hash(api_key[:72])[:16]
