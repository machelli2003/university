"""Section 47: Librarian Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/librarian", tags=["librarian-dashboard"])
@router.get("/officer/dashboard/library", tags=["librarian-dashboard"])
async def get_librarian_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["librarian", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_books": 15000,
        "available_books": 11200,
        "checked_out_books": 3800,
        "overdue_books": 45,
        "total_members": 2500,
        "recent_checkouts": [
            {"checkout_id": "CHK-001", "member_name": "Yaw Boateng", "book_title": "Introduction to Computer Science", "checkout_date": "2026-08-01", "due_date": "2026-08-15", "status": "active"},
            {"checkout_id": "CHK-002", "member_name": "Akosua Prempeh", "book_title": "Principles of Macroeconomics", "checkout_date": "2026-07-20", "due_date": "2026-08-03", "status": "overdue"},
        ],
        "top_books": [
            {"book_id": "BK-001", "title": "Data Structures & Algorithms in Python", "isbn": "978-0134853987", "total_copies": 25, "available_copies": 5},
            {"book_id": "BK-002", "title": "Calculus: Early Transcendentals", "isbn": "978-1337613927", "total_copies": 30, "available_copies": 12},
        ]
    }

