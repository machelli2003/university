import pytest_asyncio
from beanie import Document, init_beanie
from mongomock_motor import AsyncMongoMockClient

import app.infrastructure.models as model_module


def _document_models():
    models = []
    for value in vars(model_module).values():
        if isinstance(value, type) and issubclass(value, Document):
            module_name = getattr(value, "__module__", "")
            if module_name.startswith("app.infrastructure.models"):
                models.append(value)
    return models


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_test_database():
    client = AsyncMongoMockClient()
    db = client["test_db"]
    await init_beanie(database=db, document_models=_document_models())
    yield
    client.close()
