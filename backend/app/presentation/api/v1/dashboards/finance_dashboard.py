"""Section 46: Finance Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any
from app.dependencies import get_current_user
from app.infrastructure.models.user import User

router = APIRouter()

@router.get("/officer/dashboard/finance", tags=["finance-dashboard"])
async def get_finance_dashboard(current_user: User = Depends(get_current_user)):
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["finance_officer", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return {
        "total_invoices": 1500,
        "total_paid": 450000.0,
        "total_pending": 85000.0,
        "total_overdue": 25000.0,
        "total_revenue": 560000.0,
        "outstanding_balance": 110000.0,
        "payment_success_rate": 92.5,
        "recent_payments": [
            {"payment_id": "PAY-001", "student_id": "STU-2024-001", "amount": 2500.0, "payment_date": "2026-08-15", "method": "Mobile Money"},
            {"payment_id": "PAY-002", "student_id": "STU-2024-002", "amount": 3000.0, "payment_date": "2026-08-16", "method": "Credit Card"},
        ],
        "pending_invoices": [
            {"invoice_id": "INV-001", "student_id": "STU-2024-003", "amount": 1800.0, "status": "pending", "due_date": "2026-08-30"},
            {"invoice_id": "INV-002", "student_id": "STU-2024-004", "amount": 2200.0, "status": "overdue", "due_date": "2026-08-01"},
        ]
    }
