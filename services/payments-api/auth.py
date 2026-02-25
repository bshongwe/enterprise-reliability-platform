from fastapi import HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader

API_KEY = "supersecretkey"  # Set securely in prod
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return api_key
