from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime, timedelta
from app.presentation.api.v1.library.schemas import (
    CreateBookRequest, BorrowBookRequest, ReturnBookRequest, BookResponse
)
from app.infrastructure.database.repositories.library_repository import (
    LibraryBookRepository, BorrowingRepository, ReservationRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_book_repo() -> LibraryBookRepository:
    return LibraryBookRepository()

def get_borrowing_repo() -> BorrowingRepository:
    return BorrowingRepository()

@router.post("/books", response_model=BookResponse)
async def create_book(
    request: CreateBookRequest,
    current_user: User = Depends(require_roles("librarian", "university_admin", "super_admin")),
    book_repo=Depends(get_book_repo),
):
    book = await book_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "available_copies": request.total_copies,
        **request.dict()
    })
    return BookResponse(
        id=str(book.id), title=book.title, author=book.author,
        available_copies=book.available_copies, total_copies=book.total_copies
    )

@router.get("/books/search", response_model=List[BookResponse])
async def search_books(
    query: str,
    current_user: User = Depends(get_current_user),
    book_repo=Depends(get_book_repo),
):
    books = await book_repo.search(current_user.tenant_id or "default", query)
    return [
        BookResponse(id=str(b.id), title=b.title, author=b.author,
                     available_copies=b.available_copies, total_copies=b.total_copies)
        for b in books
    ]

@router.post("/borrow")
async def borrow_book(
    request: BorrowBookRequest,
    current_user: User = Depends(get_current_user),
    book_repo=Depends(get_book_repo),
    borrowing_repo=Depends(get_borrowing_repo),
):
    book = await book_repo.get_by_id(request.book_id)
    if not book or book.available_copies <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book not available")

    due_date = datetime.utcnow() + timedelta(days=request.days)

    borrowing = await borrowing_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "student_id": request.student_id,
        "book_id": request.book_id,
        "due_date": due_date,
    })

    await book_repo.update(request.book_id, {"available_copies": book.available_copies - 1})

    return {"borrowing_id": str(borrowing.id), "due_date": due_date}

@router.post("/return")
async def return_book(
    request: ReturnBookRequest,
    current_user: User = Depends(get_current_user),
    book_repo=Depends(get_book_repo),
    borrowing_repo=Depends(get_borrowing_repo),
):
    borrowing = await borrowing_repo.get_by_id(request.borrowing_id)
    if not borrowing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrowing record not found")

    fine = 0.0
    if datetime.utcnow() > borrowing.due_date:
        days_overdue = (datetime.utcnow() - borrowing.due_date).days
        fine = days_overdue * 0.5

    await borrowing_repo.update(request.borrowing_id, {
        "return_date": datetime.utcnow(),
        "fine_amount": fine,
    })

    book = await book_repo.get_by_id(borrowing.book_id)
    if book:
        await book_repo.update(str(book.id), {"available_copies": book.available_copies + 1})

    return {"status": "returned", "fine_amount": fine}

@router.get("/my-borrowings/{student_id}")
async def get_my_borrowings(
    student_id: str,
    current_user: User = Depends(get_current_user),
    borrowing_repo=Depends(get_borrowing_repo),
):
    borrowings = await borrowing_repo.get_active_borrowings(current_user.tenant_id or "default", student_id)
    return [
        {"id": str(b.id), "book_id": b.book_id, "due_date": b.due_date}
        for b in borrowings
    ]
