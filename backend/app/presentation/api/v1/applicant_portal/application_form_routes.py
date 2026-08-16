"""
Application Form Purchase Routes - PIN & Serial Number System

This module handles the purchase of application forms with PIN and Serial numbers.
The workflow is:
1. Applicant requests to purchase form (pays via Paystack)
2. After payment, generate PIN and Serial
3. Applicant receives PIN and Serial to login
4. On login, verify PIN and Serial, create applicant account
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from pydantic import EmailStr

from app.presentation.api.v1.applicant_portal.application_form_schemas import (
    PurchaseApplicationFormRequest,
    PurchaseApplicationFormResponse,
    VerifyApplicationFormPurchaseRequest,
    ApplicationFormPurchaseConfirmation,
    ApplicationFormCredentials,
)
from app.infrastructure.services.paystack_service import ApplicationFormPurchaseService
from app.infrastructure.database.repositories.application_form_repository import ApplicationFormRepository
from app.infrastructure.models import ApplicationForm

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== DEPENDENCIES ====================

async def get_paystack_service() -> ApplicationFormPurchaseService:
    """Get Paystack payment service with API key from env"""
    paystack_key = os.getenv("PAYSTACK_SECRET_KEY")
    if not paystack_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment service not configured"
        )
    return ApplicationFormPurchaseService(paystack_key)


async def get_application_form_repo() -> ApplicationFormRepository:
    """Get application form repository"""
    return ApplicationFormRepository()


# ==================== PUBLIC ENDPOINTS ====================

@router.post(
    "/purchase",
    response_model=PurchaseApplicationFormResponse,
    tags=["Application Form Purchase"],
    summary="Initiate Application Form Purchase",
    description="Start payment process for application form. Redirects to Paystack.",
)
async def purchase_application_form(
    request: PurchaseApplicationFormRequest,
    paystack_service: ApplicationFormPurchaseService = Depends(get_paystack_service),
):
    """
    Initiate purchase of application form.
    
    - Validates applicant info
    - Creates Paystack payment link
    - Returns payment URL for applicant to proceed with payment
    """
    try:
        # Get application fee from configuration
        # For now, using a fixed amount - should be configurable per admission cycle
        application_fee = 50.0  # 50 GHS
        
        # Build callback URL (frontend should handle redirect)
        callback_url = os.getenv(
            "PAYSTACK_CALLBACK_URL",
            "http://localhost:5173/payment-verification"
        )
        
        payment_info = await paystack_service.initialize_payment(
            email=request.email,
            amount=application_fee,
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
            admission_cycle_id=request.admission_cycle_id,
            academic_year="2024/2025",  # Should come from request or config
            callback_url=callback_url,
        )
        
        return PurchaseApplicationFormResponse(
            payment_url=payment_info["payment_url"],
            reference=payment_info["reference"],
            access_code=payment_info["access_code"],
            amount=payment_info["amount"],
        )
        
    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/verify-payment",
    response_model=ApplicationFormPurchaseConfirmation,
    tags=["Application Form Purchase"],
    summary="Verify Payment and Generate Credentials",
    description="After payment, verify and generate PIN + Serial number",
)
async def verify_application_form_purchase(
    request: VerifyApplicationFormPurchaseRequest,
    paystack_service: ApplicationFormPurchaseService = Depends(get_paystack_service),
    application_form_repo: ApplicationFormRepository = Depends(get_application_form_repo),
):
    """
    Verify Paystack payment and generate PIN + Serial.
    
    - Verifies payment with Paystack
    - Generates unique PIN and Serial number
    - Creates ApplicationForm record
    - Returns credentials to applicant
    """
    try:
        # Verify payment with Paystack
        payment_data = await paystack_service.verify_payment(request.reference)
        
        # Check if we already created a form for this payment
        existing_form = await application_form_repo.get_by_paystack_reference(request.reference)
        if existing_form:
            logger.warning(f"Form already exists for reference {request.reference}")
            return ApplicationFormPurchaseConfirmation(
                success=True,
                message="Form already purchased",
                credentials=ApplicationFormCredentials(
                    pin=existing_form.pin,
                    serial_number=existing_form.serial_number,
                    payment_reference=existing_form.payment_reference,
                ),
                email=existing_form.applicant_email,
            )
        
        # Extract metadata from Paystack
        metadata = payment_data.get("metadata", {})
        
        # Create application form with PIN and Serial
        form = await paystack_service.create_application_form(
            applicant_email=metadata.get("email") or payment_data["customer"].get("email"),
            first_name=metadata.get("first_name", ""),
            last_name=metadata.get("last_name", ""),
            phone_number=metadata.get("phone_number", ""),
            admission_cycle_id=metadata.get("admission_cycle_id", ""),
            academic_year=metadata.get("academic_year", "2024/2025"),
            amount=payment_data["amount"],
            paystack_reference=request.reference,
        )
        
        logger.info(f"Generated credentials for {form.applicant_email}: PIN={form.pin}, Serial={form.serial_number}")
        
        return ApplicationFormPurchaseConfirmation(
            success=True,
            message="Payment verified. PIN and Serial generated successfully.",
            credentials=ApplicationFormCredentials(
                pin=form.pin,
                serial_number=form.serial_number,
                payment_reference=form.payment_reference,
            ),
            email=form.applicant_email,
        )
        
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/check-form/{pin}/{serial_number}",
    tags=["Application Form Verification"],
    summary="Check if PIN/Serial is Valid",
    description="Verify if a PIN and Serial number are valid and unused",
)
async def check_application_form_validity(
    pin: str,
    serial_number: str,
    application_form_repo: ApplicationFormRepository = Depends(get_application_form_repo),
):
    """
    Check if a PIN and Serial number are valid.
    Used before login attempt.
    """
    try:
        form = await application_form_repo.get_active_by_pin_and_serial(pin, serial_number)
        
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid PIN or Serial number"
            )
        
        return {
            "valid": True,
            "message": "PIN and Serial are valid",
            "admission_cycle_id": form.admission_cycle_id,
            "academic_year": form.academic_year,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking form: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error validating form"
        )


# ==================== ADMIN ENDPOINTS ====================

@router.get(
    "/forms/by-cycle/{admission_cycle_id}",
    tags=["Admin - Application Forms"],
    summary="Get Forms by Admission Cycle",
    description="Get all purchased forms for an admission cycle (Admin only)",
)
async def get_forms_by_cycle(
    admission_cycle_id: str,
    application_form_repo: ApplicationFormRepository = Depends(get_application_form_repo),
):
    """
    Get all application forms for a specific admission cycle.
    Admin endpoint for monitoring sales.
    """
    try:
        forms = await application_form_repo.get_by_admission_cycle(admission_cycle_id)
        
        return {
            "count": len(forms),
            "admission_cycle_id": admission_cycle_id,
            "forms": [
                {
                    "id": str(form.id),
                    "pin": form.pin,
                    "serial_number": form.serial_number,
                    "status": form.status,
                    "applicant_email": form.applicant_email,
                    "amount": form.amount,
                    "created_at": form.created_at,
                    "used_at": form.used_at,
                }
                for form in forms
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching forms: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error fetching forms"
        )


@router.get(
    "/stats/by-cycle/{admission_cycle_id}",
    tags=["Admin - Application Forms"],
    summary="Get Purchase Statistics",
    description="Get statistics for application form sales",
)
async def get_purchase_statistics(
    admission_cycle_id: str,
    application_form_repo: ApplicationFormRepository = Depends(get_application_form_repo),
):
    """
    Get statistics about application form purchases.
    """
    try:
        purchased_count = await application_form_repo.count_by_status(
            "purchased",
            admission_cycle_id
        )
        used_count = await application_form_repo.count_by_status(
            "used",
            admission_cycle_id
        )
        
        forms = await application_form_repo.get_by_admission_cycle(admission_cycle_id)
        total_revenue = sum(f.amount for f in forms)
        
        return {
            "admission_cycle_id": admission_cycle_id,
            "total_purchased": purchased_count + used_count,
            "total_used": used_count,
            "total_unused": purchased_count,
            "total_revenue": total_revenue,
            "currency": "GHS",
        }
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error calculating statistics"
        )
