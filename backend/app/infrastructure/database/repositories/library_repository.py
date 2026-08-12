from app.infrastructure.models.library import LibraryBook, Borrowing, Reservation
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional
from datetime import datetime, timedelta

class LibraryBookRepository(BaseRepository[LibraryBook]):
    def __init__(self):
        super().__init__(LibraryBook)

    async def search(self, tenant_id: str, query: str) -> List[LibraryBook]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
            ]
        }).to_list(None)

    async def get_available(self, tenant_id: str) -> List[LibraryBook]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "available_copies": {"$gt": 0}
        }).to_list(None)

class BorrowingRepository(BaseRepository[Borrowing]):
    def __init__(self):
        super().__init__(Borrowing)

    async def get_by_student(self, tenant_id: str, student_id: str) -> List[Borrowing]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id
        }).to_list(None)

    async def get_active_borrowings(self, tenant_id: str, student_id: str) -> List[Borrowing]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "student_id": student_id,
            "return_date": None
        }).to_list(None)

    async def get_overdue(self, tenant_id: str) -> List[Borrowing]:
        return await self.model.find({
            "tenant_id": tenant_id,
            "return_date": None,
            "due_date": {"$lt": datetime.utcnow()}
        }).to_list(None)

class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self):
        super().__init__(Reservation)

    async def get_by_book(self, book_id: str) -> List[Reservation]:
        return await self.model.find({
            "book_id": book_id,
            "status": "pending"
        }).to_list(None)
