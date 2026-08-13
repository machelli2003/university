"""Section 47: Librarian Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class LibrarianDashboardResponse(BaseModel):
    total_books: int
    available_books: int
    checked_out: int
    overdue_items: int
    active_borrowers: int

@router.get("/officer/dashboard/librarian", response_model=LibrarianDashboardResponse, tags=["librarian-dashboard"])
async def get_librarian_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["librarian", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return LibrarianDashboardResponse(
        total_books=8500,
        available_books=7200,
        checked_out=1200,
        overdue_items=45,
        active_borrowers=2100
    )
