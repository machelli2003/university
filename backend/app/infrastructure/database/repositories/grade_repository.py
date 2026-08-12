from app.infrastructure.models.exam import Grade, Transcript, GradeAppeal
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class GradeRepository(BaseRepository[Grade]):
    def __init__(self):
        super().__init__(Grade)

    async def get_by_student_semester(self, tenant_id: str, student_id: str, academic_year: str, semester: str) -> List[Grade]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "academic_year": academic_year,
            "semester": semester
        }).to_list(None)

    async def get_pending_approval(self, tenant_id: str) -> List[Grade]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": {"$in": ["submitted", "under_review"]}
        }).to_list(None)

    async def get_approved_for_period(self, tenant_id: str, academic_year: str, semester: str) -> List[Grade]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "academic_year": academic_year,
            "semester": semester,
            "status": "approved"
        }).to_list(None)

    async def get_by_course(self, course_id: str) -> List[Grade]:
        return await self.model.find({
            "course_id": course_id
        }).to_list(None)

    async def get_by_submitter(self, tenant_id: str, submitted_by: str) -> List[Grade]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "submitted_by": submitted_by,
        }).to_list(None)

class TranscriptRepository(BaseRepository[Transcript]):
    def __init__(self):
        super().__init__(Transcript)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[Transcript]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).sort("academic_year", -1).to_list(None)

    async def get_latest_transcript(self, tenant_id: str, student_id: str) -> Optional[Transcript]:
        transcripts = await self.get_by_student(tenant_id, student_id)
        return transcripts[0] if transcripts else None

class GradeAppealRepository(BaseRepository[GradeAppeal]):
    def __init__(self):
        super().__init__(GradeAppeal)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[GradeAppeal]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).to_list(None)

    async def get_pending_appeals(self, tenant_id: str) -> List[GradeAppeal]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "status": "pending"
        }).to_list(None)
