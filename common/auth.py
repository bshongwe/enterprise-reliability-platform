import os
from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

API_KEY_HASH = os.getenv("API_KEY_HASH", "")
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)
ph = PasswordHasher()


def get_api_key(api_key: str = Depends(api_key_header)):
    # For testing: if no hash is set, allow test-key
    if not API_KEY_HASH:
        if api_key == "test-key":
            return api_key[:16]
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        ph.verify(API_KEY_HASH, api_key)
        return api_key[:16]
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
