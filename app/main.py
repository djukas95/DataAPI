from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.api.deps import get_store
from app.api.routes import exhibits, health
from app.core.responses import error_json
from app.models.exhibit import ExhibitCreate


def _sample_exhibits() -> list[ExhibitCreate]:
    return [
        ExhibitCreate(
            title="The Night Watch",
            artist="Rembrandt van Rijn",
            year=1642,
            room="Gallery 2",
        ),
        ExhibitCreate(
            title="The Milkmaid",
            artist="Johannes Vermeer",
            year=1658,
            room="Gallery 1",
        ),
    ]


@asynccontextmanager
async def lifespan(_: FastAPI):
    store = get_store()
    if not store.list():
        store.seed(_sample_exhibits())
    yield


app = FastAPI(
    title="City Museum — Catalog",
    description=(
        "Small demo API for cataloguing exhibits. Data is kept in memory. "
        "Every API path requires a valid Bearer token (same value as `API_TOKEN`). "
        "Use Authorize in Swagger before Try it out. `/docs` and `/openapi.json` stay "
        "unauthenticated so the UI can load; lock them in production if needed."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    details: list[dict[str, str]] = []
    for err in exc.errors():
        loc = err.get("loc") or ()
        field = ".".join(str(x) for x in loc)
        details.append({"field": field, "message": err.get("msg", "Invalid value")})
    return error_json(
        "Validation failed",
        "VALIDATION_ERROR",
        details=details,
        status_code=422,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        err: dict[str, object] = {"code": detail["code"]}
        if detail.get("details"):
            err["details"] = detail["details"]
        body = {
            "success": False,
            "message": detail.get("message", "Error"),
            "error": err,
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=body,
            headers=getattr(exc, "headers", None),
        )

    text = detail if isinstance(detail, str) else str(detail)
    status = exc.status_code
    if status == 403 and ("Not authenticated" in text or "not authenticated" in text.lower()):
        return error_json(
            "Authentication required",
            "AUTH_REQUIRED",
            status_code=403,
        )
    if status == 401:
        return error_json("Invalid credentials", "AUTH_INVALID_CREDENTIALS", status_code=401)
    if status == 403:
        return error_json("Forbidden", "AUTH_FORBIDDEN", status_code=403)
    if status == 404:
        return error_json(text or "Not found", "NOT_FOUND", status_code=404)
    return error_json(text or "Error", "HTTP_ERROR", status_code=status)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, __: Exception):
    return error_json(
        "Internal server error",
        "INTERNAL_ERROR",
        status_code=500,
    )


app.include_router(health.router)
app.include_router(exhibits.router)
