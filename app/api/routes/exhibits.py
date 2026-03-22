from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.auth import require_curator
from app.api.deps import StoreDep
from app.core.responses import success_json
from app.models.exhibit import ExhibitCreate, ExhibitRead, ExhibitUpdate

router = APIRouter(
    prefix="/exhibits",
    tags=["exhibits"],
    dependencies=[Depends(require_curator)],
)


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "EXHIBIT_NOT_FOUND",
            "message": "Exhibit not found",
        },
    )


@router.get("")
def list_exhibits(
    store: StoreDep,
    room: Optional[str] = Query(None, description="Filter by room name (exact match, case-insensitive)"),
    year_from: Optional[int] = Query(None, ge=1000, le=2100),
    year_to: Optional[int] = Query(None, ge=1000, le=2100),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    rows = store.list(room=room, year_from=year_from, year_to=year_to)
    total = len(rows)
    start = (page - 1) * limit
    page_items: List[ExhibitRead] = rows[start : start + limit]
    meta = {"page": page, "limit": limit, "total": total}
    return success_json("Exhibits fetched", page_items, meta=meta)


@router.get("/rooms/summary")
def rooms_summary(store: StoreDep):
    return success_json("Room summary fetched", store.rooms())


@router.get("/{exhibit_id}")
def get_exhibit(exhibit_id: UUID, store: StoreDep):
    row = store.get(exhibit_id)
    if row is None:
        raise _not_found()
    return success_json("Exhibit fetched", row)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_exhibit(payload: ExhibitCreate, store: StoreDep):
    created = store.add(payload)
    return success_json("Exhibit created", created, status_code=201)


@router.patch("/{exhibit_id}")
def patch_exhibit(exhibit_id: UUID, payload: ExhibitUpdate, store: StoreDep):
    row = store.update(exhibit_id, payload)
    if row is None:
        raise _not_found()
    return success_json("Exhibit updated", row)


@router.delete("/{exhibit_id}")
def delete_exhibit(exhibit_id: UUID, store: StoreDep):
    if not store.delete(exhibit_id):
        raise _not_found()
    return success_json("Exhibit deleted", None)
