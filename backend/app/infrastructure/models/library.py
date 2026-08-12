from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime

class LibraryBook(Document):
    tenant_id: str
    title: str
    isbn: Optional[str] = None
    author: str
    publisher: Optional[str] = None
    category: str

    total_copies: int
    available_copies: int

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "library_books"

class Borrowing(Document):
    tenant_id: str
    student_id: str
    book_id: str

    borrow_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    return_date: Optional[datetime] = None

    fine_amount: float = 0.0
    fine_paid: bool = False

    class Settings:
        name = "borrowings"
        indexes = [
            [("student_id", 1), ("return_date", 1)],
        ]

class Reservation(Document):
    tenant_id: str
    student_id: str
    book_id: str

    reservation_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"

    class Settings:
        name = "reservations"
