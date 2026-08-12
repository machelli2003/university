from app.infrastructure.models.attendance import Attendance
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List

class AttendanceRepository(BaseRepository[Attendance]):
    def __init__(self):
        super().__init__(Attendance)

    async def get_by_course_and_date(self, course_id: str, session_date) -> List[Attendance]:
        return await self.model.find({"course_id": course_id, "session_date": session_date}).to_list(None)

    async def get_by_course_and_range(self, course_id: str, start_date, end_date) -> List[Attendance]:
        return await self.model.find({
            "course_id": course_id,
            "session_date": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)

    async def get_by_student(self, student_id: str) -> List[Attendance]:
        return await self.model.find({"student_id": student_id}).to_list(None)
