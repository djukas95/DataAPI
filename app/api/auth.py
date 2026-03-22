import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings

bearer_scheme = HTTPBearer()


def require_curator(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> None:
    a = credentials.credentials.encode("utf-8")
    b = settings.api_token.encode("utf-8")
    if len(a) != len(b) or not secrets.compare_digest(a, b):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_INVALID_CREDENTIALS",
                "message": "Invalid credentials",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
