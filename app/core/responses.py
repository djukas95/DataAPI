from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_json(
    message: str,
    data: Any = None,
    *,
    meta: dict[str, Any] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data),
    }
    if meta is not None:
        payload["meta"] = meta
    return JSONResponse(status_code=status_code, content=payload)


def error_json(
    message: str,
    code: str,
    *,
    details: list[dict[str, str]] | None = None,
    status_code: int = 400,
) -> JSONResponse:
    err: dict[str, Any] = {"code": code}
    if details:
        err["details"] = details
    body = {"success": False, "message": message, "error": err}
    return JSONResponse(status_code=status_code, content=body)
