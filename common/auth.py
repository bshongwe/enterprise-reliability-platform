import os
from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
import hashlib

API_KEY = os.getenv("API_KEY", "")
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def get_api_key(api_key: str = Depends(api_key_header)):
    if not API_KEY or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Return a sanitized identifier for logging/audit purposes
    # Note: This is not password hashing - it's for creating a
    # user identifier
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]
