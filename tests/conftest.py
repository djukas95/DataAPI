import os

os.environ["API_TOKEN"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_store
from app.main import app
from app.services.catalog import CatalogStore


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-secret"}


@pytest.fixture()
def store() -> CatalogStore:
    return CatalogStore()


@pytest.fixture()
def client(store: CatalogStore):
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
