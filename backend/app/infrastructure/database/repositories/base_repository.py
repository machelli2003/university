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
        try:
            return await self.model.get(doc_id)
        except Exception:
            return None

    async def get_one(self, **kwargs) -> Optional[T]:
        return await self.model.find_one(kwargs)

    async def find_one(self, query: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[T]:
        if query and isinstance(query, dict):
            if kwargs:
                merged = {**query, **kwargs}
                return await self.model.find_one(merged)
            return await self.model.find_one(query)
        return await self.model.find_one(kwargs)

    def find(self, query: Optional[Dict[str, Any]] = None, **kwargs):
        if query and isinstance(query, dict):
            if kwargs:
                merged = {**query, **kwargs}
                return self.model.find(merged)
            return self.model.find(query)
        return self.model.find(kwargs)

    async def get_all(self, **kwargs) -> List[T]:
        return await self.model.find(kwargs).to_list(None)

    async def update(self, doc_id: str, data: Dict[str, Any]) -> Optional[T]:
        try:
            doc = await self.model.get(doc_id)
            if not doc:
                return None
            await doc.update({"$set": data})
            return await self.model.get(doc_id)
        except Exception:
            return None

    async def delete(self, doc_id: str) -> bool:
        try:
            doc = await self.model.get(doc_id)
            if not doc:
                return False
            await doc.delete()
            return True
        except Exception:
            return False

    async def count(self, **kwargs) -> int:
        return await self.model.find(kwargs).count()

    async def exists(self, **kwargs) -> bool:
        return await self.model.find_one(kwargs) is not None

    async def find_many(self, query: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Query documents with a raw MongoDB filter dict and return as plain dicts."""
        q = query or {}
        docs = await self.model.find(q).skip(skip).limit(limit).to_list(None)
        result = []
        for doc in docs:
            try:
                d = doc.model_dump()
            except AttributeError:
                d = doc.dict()
            # Ensure _id is a plain string
            d["_id"] = str(doc.id) if hasattr(doc, "id") else d.get("id", "")
            result.append(d)
        return result

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
