from app.infrastructure.models.university_application import UniversityApplication
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime


class UniversityApplicationRepository(BaseRepository[UniversityApplication]):
    def __init__(self):
        super().__init__(UniversityApplication)

    async def get_by_application_id(self, application_id: str) -> Optional[UniversityApplication]:
        return await self.model.find_one({"university_application_id": application_id})

    async def get_by_school_code(self, school_code: str) -> Optional[UniversityApplication]:
        return await self.model.find_one({"school_code": school_code})

    async def list_by_status(self, status: str) -> List[UniversityApplication]:
        return await self.model.find({"status": status}).to_list(None)

    async def list_for_requester(self, requested_by: str) -> List[UniversityApplication]:
        return await self.model.find({"requested_by": requested_by}).to_list(None)

    async def update_section_status(self, application_id: str, section: str, completed: bool) -> Optional[UniversityApplication]:
        return await self.update(application_id, {f"setup_sections.{section}": completed, "updated_at": datetime.utcnow()})


from app.infrastructure.models.university_application import IdentifierSequence

class IdentifierSequenceRepository(BaseRepository[IdentifierSequence]):
    def __init__(self):
        super().__init__(IdentifierSequence)

    async def next_sequence(self, tenant_id: Optional[str], sequence_type: str, year: Optional[int] = None) -> int:
        from pymongo import ReturnDocument

        filter_query = {
            "sequence_type": sequence_type,
            "tenant_id": tenant_id,
            "year": year,
        }
        update = {
            "$inc": {"sequence": 1},
            "$setOnInsert": {
                "tenant_id": tenant_id,
                "sequence_type": sequence_type,
                "year": year,
                "updated_at": datetime.utcnow(),
            },
            "$set": {"updated_at": datetime.utcnow()},
        }

        doc = await self.model.get_motor_collection().find_one_and_update(
            filter_query,
            update,
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return doc["sequence"]
