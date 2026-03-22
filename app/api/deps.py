from typing import Annotated

from fastapi import Depends

from app.services.catalog import CatalogStore

_store = CatalogStore()


def get_store() -> CatalogStore:
    return _store


StoreDep = Annotated[CatalogStore, Depends(get_store)]
