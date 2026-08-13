"""Section 45: Finance Officer Dashboard"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()

class FinanceDashboardResponse(BaseModel):
    total_invoices: int
    pending_payments: int
    total_revenue: float
    outstanding_balance: float
    payment_success_rate: float

@router.get("/officer/dashboard/finance", response_model=FinanceDashboardResponse, tags=["finance-dashboard"])
async def get_finance_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") not in ["finance_officer", "super_admin"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return FinanceDashboardResponse(
        total_invoices=450,
        pending_payments=85,
        total_revenue=2500000.00,
        outstanding_balance=180000.00,
        payment_success_rate=94.5
    )
