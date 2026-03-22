from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExhibitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Night Watch"])
    artist: str = Field(..., min_length=1, max_length=120, examples=["Rembrandt"])
    year: int = Field(..., ge=1000, le=2100, examples=[1642])
    room: str = Field(..., min_length=1, max_length=80, examples=["Gallery 2"])


class ExhibitCreate(ExhibitBase):
    pass


class ExhibitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    artist: Optional[str] = Field(None, min_length=1, max_length=120)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    room: Optional[str] = Field(None, min_length=1, max_length=80)


class ExhibitRead(ExhibitBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoomSummary(BaseModel):
    name: str
    count: int
