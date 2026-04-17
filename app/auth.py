from fastapi import Header, HTTPException, status
from app.config import settings

def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key không hợp lệ.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return "system_agent_id"