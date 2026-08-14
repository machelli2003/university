"""
Finance Officer Dashboard Endpoints
Item 46: Finance Officer Frontend - API endpoints providing financial analytics

Provides:
- Payment statistics (total, pending, overdue)
- Fee collection analytics
- Student accounts overview
- Financial reports
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.dependencies import (
    get_current_user, require_roles, get_payment_repo, 
    get_student_repo, get_fee_repo
)
from app.infrastructure.models.user import User
from pydantic import BaseModel

router = APIRouter()


class PaymentStats(BaseModel):
    total_invoices: int
    total_paid: float
    total_pending: float
    total_overdue: float
    payment_success_rate: float
    outstanding_balance: float


class FinanceDashboardData(BaseModel):
    statistics: PaymentStats
    recent_payments: List[Dict[str, Any]]
    pending_invoices: List[Dict[str, Any]]
    overdue_invoices: List[Dict[str, Any]]
    top_debtors: List[Dict[str, Any]]
    monthly_revenue: List[Dict[str, Any]]


@router.get("/officer/dashboard/finance", response_model=FinanceDashboardData)
async def get_finance_dashboard(
    current_user: User = Depends(require_roles("finance_officer", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    student_repo=Depends(get_student_repo),
    month: int = Query(1, ge=1, le=12),
    year: int = Query(datetime.utcnow().year),
):
    """
    Item 46: Finance Officer Dashboard
    Returns comprehensive financial analytics and payment status.
    """
    tenant_id = str(current_user.tenant_id)
    
    try:
        # Get all payments for tenant
        all_payments = await payment_repo.find({
            "tenant_id": tenant_id,
        })
        
        # Calculate statistics
        total_paid = sum(p.get("amount", 0) for p in all_payments if p.get("status") == "confirmed")
        total_pending = sum(p.get("amount", 0) for p in all_payments if p.get("status") == "pending")
        
        now = datetime.utcnow()
        overdue_date = now - timedelta(days=30)
        total_overdue = sum(
            p.get("amount", 0) for p in all_payments
            if p.get("status") == "pending" and p.get("created_at", now) < overdue_date
        )
        
        total_invoices = len(all_payments)
        total_revenue = total_paid + total_pending + total_overdue
        outstanding_balance = total_pending + total_overdue
        
        success_rate = (total_paid / total_revenue * 100) if total_revenue > 0 else 0
        
        # Get recent payments (last 10)
        recent_payments = sorted(
            all_payments,
            key=lambda p: p.get("created_at", datetime.utcnow()),
            reverse=True
        )[:10]
        
        # Get pending invoices
        pending_invoices = [p for p in all_payments if p.get("status") == "pending"][:20]
        
        # Get overdue invoices
        overdue_invoices = [
            p for p in all_payments
            if p.get("status") == "pending" and p.get("created_at", now) < overdue_date
        ][:20]
        
        # Calculate monthly revenue (simplified)
        monthly_revenue = [
            {"month": f"{datetime(year, month, 1).strftime('%B')}", "amount": total_revenue}
        ]
        
        return FinanceDashboardData(
            statistics=PaymentStats(
                total_invoices=total_invoices,
                total_paid=total_paid,
                total_pending=total_pending,
                total_overdue=total_overdue,
                payment_success_rate=success_rate,
                outstanding_balance=outstanding_balance,
            ),
            recent_payments=[
                {
                    "payment_id": str(p.get("id", "")),
                    "student_id": p.get("student_id"),
                    "amount": p.get("amount"),
                    "status": p.get("status"),
                    "date": p.get("created_at").isoformat() if p.get("created_at") else None,
                }
                for p in recent_payments
            ],
            pending_invoices=[
                {
                    "invoice_id": str(p.get("id", "")),
                    "student_id": p.get("student_id"),
                    "amount": p.get("amount"),
                    "due_date": (p.get("created_at") + timedelta(days=30)).isoformat() if p.get("created_at") else None,
                }
                for p in pending_invoices
            ],
            overdue_invoices=[
                {
                    "invoice_id": str(p.get("id", "")),
                    "student_id": p.get("student_id"),
                    "amount": p.get("amount"),
                    "days_overdue": (now - p.get("created_at", now)).days if p.get("created_at") else 0,
                }
                for p in overdue_invoices
            ],
            top_debtors=[
                {
                    "student_id": p.get("student_id"),
                    "outstanding": sum(
                        x.get("amount", 0) for x in all_payments
                        if x.get("student_id") == p.get("student_id") and x.get("status") == "pending"
                    ),
                }
                for p in all_payments
            ][:10],
            monthly_revenue=monthly_revenue,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch finance dashboard: {str(e)}"
        )


@router.get("/officer/dashboard/finance/export")
async def export_finance_report(
    current_user: User = Depends(require_roles("finance_officer", "super_admin")),
    payment_repo=Depends(get_payment_repo),
    format: str = Query("csv", regex="^(csv|json)$"),
):
    """
    Export finance report in CSV or JSON format.
    """
    tenant_id = str(current_user.tenant_id)
    
    try:
        payments = await payment_repo.find({"tenant_id": tenant_id})
        
        if format == "json":
            return {
                "exported_at": datetime.utcnow().isoformat(),
                "total_records": len(payments),
                "payments": [
                    {
                        "id": str(p.get("id", "")),
                        "student_id": p.get("student_id"),
                        "amount": p.get("amount"),
                        "status": p.get("status"),
                        "created_at": p.get("created_at").isoformat() if p.get("created_at") else None,
                    }
                    for p in payments
                ],
            }
        
        # CSV format
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["payment_id", "student_id", "amount", "status", "date"]
        )
        writer.writeheader()
        
        for p in payments:
            writer.writerow({
                "payment_id": str(p.get("id", "")),
                "student_id": p.get("student_id"),
                "amount": p.get("amount"),
                "status": p.get("status"),
                "date": p.get("created_at").isoformat() if p.get("created_at") else "",
            })
        
        return {"csv_content": output.getvalue()}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
