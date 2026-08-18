"""
Section 40: Admissions Officer Dashboard
Backend aggregation endpoints for admissions officer role.

Aggregates:
- Pending applications by status
- WASSCE verifications needed
- Recent activity
- Quick statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from app.dependencies import get_current_user
from app.infrastructure.database.repositories import ApplicantRepository
from app.infrastructure.models.applicant import ApplicationStatusEnum, VerificationStatusEnum

router = APIRouter()

admissions_officer_repo = ApplicantRepository()


# Response Schemas
class PendingApplicationSummary(BaseModel):
    applicant_id: str
    full_name: str
    email: str
    phone: str
    application_date: datetime
    current_status: ApplicationStatusEnum
    verification_status: VerificationStatusEnum
    time_in_current_state: int  # hours
    priority: str  # "urgent", "high", "normal"


class ApplicationStatusStats(BaseModel):
    status: ApplicationStatusEnum
    count: int
    percentage: float


class AdmissionsOfficerDashboardResponse(BaseModel):
    # Quick Statistics
    total_applications: int
    total_pending_verification: int
    total_under_review: int
    total_eligible: int
    total_rejected: int
    
    # Status Distribution
    status_breakdown: List[ApplicationStatusStats]
    
    # Recent Activity
    recent_applications: List[PendingApplicationSummary]
    pending_verifications: List[PendingApplicationSummary]
    under_review_applications: List[PendingApplicationSummary]
    
    # Alert Items
    applications_over_5_days: List[PendingApplicationSummary]
    applications_over_10_days: List[PendingApplicationSummary]
    
    # Metrics
    avg_time_in_review_hours: float
    verification_completion_rate: float  # percentage


@router.get(
    "/officer/dashboard/admissions",
    response_model=AdmissionsOfficerDashboardResponse,
    tags=["admissions-officer-dashboard"],
    summary="Admissions Officer Dashboard Data"
)
async def get_admissions_officer_dashboard(
    current_user = Depends(get_current_user),
    days: int = Query(30, ge=1, le=90, description="Number of days to look back for stats")
):
    """
    Get comprehensive dashboard data for admissions officer.
    
    Requires: role = 'admissions_officer'
    
    Returns:
    - Application counts by status
    - Pending WASSCE verifications
    - Applications awaiting review
    - SLA alerts (applications stuck in states)
    - Performance metrics
    """
    
    # Verify user role
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role not in ["admissions_officer", "university_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Only admissions officers can access this")
    
    tenant_id = str(getattr(current_user, "tenant_id", "single-university") or "single-university")
    
    try:
        # Get all applications for this tenant
        all_applications = await admissions_officer_repo.find_many(
            {"tenant_id": tenant_id},
            skip=0,
            limit=10000
        )
        
        total_apps = len(all_applications)
        
        # Calculate statistics
        status_counts = {}
        for app in all_applications:
            status = app.get("status", "draft")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Build status breakdown
        status_breakdown = []
        for status in ApplicationStatusEnum:
            count = status_counts.get(status.value, 0)
            percentage = (count / total_apps * 100) if total_apps > 0 else 0
            status_breakdown.append(ApplicationStatusStats(
                status=status,
                count=count,
                percentage=round(percentage, 2)
            ))
        
        # Get pending verifications
        pending_verifications = await admissions_officer_repo.find_many(
            {
                "tenant_id": tenant_id,
                "verification_status": VerificationStatusEnum.PENDING_VERIFICATION.value
            },
            skip=0,
            limit=50
        )
        
        # Get applications under review
        under_review_applications = await admissions_officer_repo.find_many(
            {
                "tenant_id": tenant_id,
                "status": ApplicationStatusEnum.UNDER_REVIEW.value
            },
            skip=0,
            limit=50
        )
        
        # Get recent applications (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_applications = await admissions_officer_repo.find_many(
            {
                "tenant_id": tenant_id,
                "application_date": {"$gte": cutoff_date}
            },
            skip=0,
            limit=20
        )
        
        # Get SLA alerts (applications stuck > 5 and > 10 days)
        five_days_ago = datetime.utcnow() - timedelta(days=5)
        ten_days_ago = datetime.utcnow() - timedelta(days=10)
        
        over_5_days = await admissions_officer_repo.find_many(
            {
                "tenant_id": tenant_id,
                "application_date": {"$lt": five_days_ago},
                "status": {"$in": [
                    ApplicationStatusEnum.SUBMITTED.value,
                    ApplicationStatusEnum.UNDER_REVIEW.value,
                    ApplicationStatusEnum.DEPARTMENT_REVIEW.value
                ]}
            },
            skip=0,
            limit=50
        )
        
        over_10_days = await admissions_officer_repo.find_many(
            {
                "tenant_id": tenant_id,
                "application_date": {"$lt": ten_days_ago},
                "status": {"$in": [
                    ApplicationStatusEnum.SUBMITTED.value,
                    ApplicationStatusEnum.UNDER_REVIEW.value,
                    ApplicationStatusEnum.DEPARTMENT_REVIEW.value
                ]}
            },
            skip=0,
            limit=50
        )
        
        # Build response summaries
        def build_summary(app_dict) -> PendingApplicationSummary:
            app_date = app_dict.get("application_date", datetime.utcnow())
            hours_elapsed = int((datetime.utcnow() - app_date).total_seconds() / 3600)
            
            # Determine priority
            if hours_elapsed > 240:  # > 10 days
                priority = "urgent"
            elif hours_elapsed > 120:  # > 5 days
                priority = "high"
            else:
                priority = "normal"
            
            return PendingApplicationSummary(
                applicant_id=str(app_dict.get("_id", "")),
                full_name=f"{app_dict.get('first_name', '')} {app_dict.get('last_name', '')}",
                email=app_dict.get("email", ""),
                phone=app_dict.get("phone", ""),
                application_date=app_date,
                current_status=app_dict.get("status", ApplicationStatusEnum.DRAFT),
                verification_status=app_dict.get("verification_status", VerificationStatusEnum.PENDING_VERIFICATION),
                time_in_current_state=hours_elapsed,
                priority=priority
            )
        
        recent_summaries = [build_summary(app) for app in recent_applications[:10]]
        pending_verification_summaries = [build_summary(app) for app in pending_verifications[:10]]
        under_review_summaries = [build_summary(app) for app in under_review_applications[:10]]
        over_5_days_summaries = [build_summary(app) for app in over_5_days[:5]]
        over_10_days_summaries = [build_summary(app) for app in over_10_days[:5]]
        
        # Calculate metrics
        total_verified = len([app for app in all_applications 
                             if app.get("verification_status") == VerificationStatusEnum.VERIFIED.value])
        verification_rate = (total_verified / len(pending_verifications) * 100) if pending_verifications else 100
        
        # Calculate average review time
        reviewed_apps = [app for app in all_applications 
                        if app.get("status") in [
                            ApplicationStatusEnum.OFFERED.value,
                            ApplicationStatusEnum.REJECTED.value,
                            ApplicationStatusEnum.ENROLLED.value
                        ]]
        if reviewed_apps:
            avg_hours = sum([
                (app.get("updated_at", datetime.utcnow()) - app.get("application_date", datetime.utcnow())).total_seconds() / 3600
                for app in reviewed_apps
            ]) / len(reviewed_apps)
        else:
            avg_hours = 0
        
        return AdmissionsOfficerDashboardResponse(
            total_applications=total_apps,
            total_pending_verification=len(pending_verifications),
            total_under_review=len(under_review_applications),
            total_eligible=status_counts.get(ApplicationStatusEnum.ELIGIBLE.value, 0),
            total_rejected=status_counts.get(ApplicationStatusEnum.REJECTED.value, 0),
            status_breakdown=status_breakdown,
            recent_applications=recent_summaries,
            pending_verifications=pending_verification_summaries,
            under_review_applications=under_review_summaries,
            applications_over_5_days=over_5_days_summaries,
            applications_over_10_days=over_10_days_summaries,
            avg_time_in_review_hours=round(avg_hours, 2),
            verification_completion_rate=round(verification_rate, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard: {str(e)}")
