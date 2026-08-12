from pydantic import BaseModel
from typing import Optional

class CreateBookRequest(BaseModel):
    title: str
    isbn: Optional[str] = None
    author: str
    publisher: Optional[str] = None
    category: str
    total_copies: int

class BorrowBookRequest(BaseModel):
    student_id: str
    book_id: str
    days: int = 14

class ReturnBookRequest(BaseModel):
    borrowing_id: str

class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    available_copies: int
    total_copies: int
