from typing import TypeVar, Generic, Optional, List, Dict, Any
from beanie import Document
from pymongo import UpdateOne

T = TypeVar('T', bound=Document)

class BaseRepository(Generic[T]):
    """Base repository with CRUD operations"""

    def __init__(self, model: type):
        self.model = model

    async def create(self, data: Dict[str, Any]) -> T:
        document = self.model(**data)
        await document.insert()
        return document

    async def get_by_id(self, doc_id: str) -> Optional[T]:
        return await self.model.get(doc_id)

    async def get_one(self, **kwargs) -> Optional[T]:
        return await self.model.find_one(kwargs)

    async def get_all(self, **kwargs) -> List[T]:
        return await self.model.find(kwargs).to_list(None)

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Optional[T]:
        doc = await self.model.get(doc_id)
        if not doc:
            return None
        await doc.update({"$set": data})
        return await self.model.get(doc_id)

    async def delete(self, doc_id: str) -> bool:
        doc = await self.model.get(doc_id)
        if not doc:
            return False
        await doc.delete()
        return True

    async def count(self, **kwargs) -> int:
        return await self.model.find(kwargs).count()

    async def exists(self, **kwargs) -> bool:
        return await self.model.find_one(kwargs) is not None

    async def find_paginated(self, skip: int = 0, limit: int = 10, **filters):
        query = self.model.find(filters)
        total = await query.count()
        items = await query.skip(skip).limit(limit).to_list(None)
        return items, total

    async def bulk_update(self, updates: List[UpdateOne]) -> Dict[str, Any]:
        result = await self.model.get_motor_collection().bulk_write(updates)
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        }
