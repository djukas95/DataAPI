from fastapi import APIRouter, Depends

from app.api.auth import require_curator
from app.core.responses import success_json

router = APIRouter(tags=["health"], dependencies=[Depends(require_curator)])


@router.get("/health")
def health():
    return success_json("Service healthy", {"status": "ok"})
