import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
  loop = asyncio.new_event_loop()
  yield loop
  loop.close()


@pytest.fixture()
def client() -> TestClient:
  return TestClient(app)
