from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from app.models.exhibit import ExhibitCreate, ExhibitRead, ExhibitUpdate, RoomSummary


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CatalogStore:
    """Keeps exhibits in memory. Fine for demos and tests; swap for a DB for production."""

    def __init__(self) -> None:
        self._items: Dict[UUID, ExhibitRead] = {}

    def seed(self, samples: List[ExhibitCreate]) -> None:
        for payload in samples:
            self.add(payload)

    def list(
        self,
        room: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[ExhibitRead]:
        rows = list(self._items.values())
        if room is not None:
            rr = room.strip().lower()
            rows = [r for r in rows if r.room.lower() == rr]
        if year_from is not None:
            rows = [r for r in rows if r.year >= year_from]
        if year_to is not None:
            rows = [r for r in rows if r.year <= year_to]
        rows.sort(key=lambda r: (r.title.lower(), r.id))
        return rows

    def get(self, exhibit_id: UUID) -> Optional[ExhibitRead]:
        return self._items.get(exhibit_id)

    def add(self, payload: ExhibitCreate) -> ExhibitRead:
        eid = uuid4()
        row = ExhibitRead(
            id=eid,
            created_at=_utcnow(),
            title=payload.title.strip(),
            artist=payload.artist.strip(),
            year=payload.year,
            room=payload.room.strip(),
        )
        self._items[eid] = row
        return row

    def update(self, exhibit_id: UUID, payload: ExhibitUpdate) -> Optional[ExhibitRead]:
        existing = self._items.get(exhibit_id)
        if existing is None:
            return None
        data = existing.model_dump()
        patch = payload.model_dump(exclude_unset=True)
        data.update(patch)
        if "title" in patch:
            data["title"] = str(patch["title"]).strip()
        if "artist" in patch:
            data["artist"] = str(patch["artist"]).strip()
        if "room" in patch:
            data["room"] = str(patch["room"]).strip()
        updated = ExhibitRead(**data)
        self._items[exhibit_id] = updated
        return updated

    def delete(self, exhibit_id: UUID) -> bool:
        if exhibit_id not in self._items:
            return False
        del self._items[exhibit_id]
        return True

    def rooms(self) -> List[RoomSummary]:
        counts: Dict[str, int] = {}
        for row in self._items.values():
            name = row.room.strip()
            counts[name] = counts.get(name, 0) + 1
        out = [RoomSummary(name=k, count=v) for k, v in counts.items()]
        out.sort(key=lambda r: r.name.lower())
        return out
