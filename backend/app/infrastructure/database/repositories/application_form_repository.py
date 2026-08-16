"""
Repository for ApplicationForm documents.

Handles database operations for application forms (PIN + Serial numbers).
"""

from typing import Optional, List
from app.infrastructure.models import ApplicationForm, ApplicationFormStatusEnum


class ApplicationFormRepository:
    """
    Repository for ApplicationForm data access.
    """
    
    async def create(self, application_form: ApplicationForm) -> ApplicationForm:
        """Save a new application form"""
        await application_form.save()
        return application_form
    
    async def get_by_id(self, form_id: str) -> Optional[ApplicationForm]:
        """Get form by MongoDB ID"""
        return await ApplicationForm.get(form_id)
    
    async def get_by_pin_and_serial(
        self,
        pin: str,
        serial_number: str,
    ) -> Optional[ApplicationForm]:
        """
        Get form by PIN and serial number.
        This is the primary lookup method for applicants.
        """
        return await ApplicationForm.find_one({
            "pin": pin,
            "serial_number": serial_number,
        })
    
    async def get_active_by_pin_and_serial(
        self,
        pin: str,
        serial_number: str,
    ) -> Optional[ApplicationForm]:
        """
        Get active (unused) form by PIN and serial number.
        """
        return await ApplicationForm.find_one({
            "pin": pin,
            "serial_number": serial_number,
            "status": ApplicationFormStatusEnum.PURCHASED,
        })
    
    async def get_by_applicant_id(
        self,
        applicant_id: str,
    ) -> Optional[ApplicationForm]:
        """Get the application form linked to an applicant"""
        return await ApplicationForm.find_one({
            "applicant_id": applicant_id,
        })
    
    async def get_by_admission_cycle(
        self,
        admission_cycle_id: str,
        status: Optional[ApplicationFormStatusEnum] = None,
    ) -> List[ApplicationForm]:
        """
        Get all forms for an admission cycle.
        
        Args:
            admission_cycle_id: The admission cycle ID
            status: Filter by status (optional)
        
        Returns:
            List of ApplicationForm documents
        """
        query = {"admission_cycle_id": admission_cycle_id}
        
        if status:
            query["status"] = status
        
        return await ApplicationForm.find(query).to_list()
    
    async def get_by_email(self, email: str) -> List[ApplicationForm]:
        """Get all forms purchased by an email"""
        return await ApplicationForm.find({
            "applicant_email": email.lower(),
        }).to_list()
    
    async def get_by_paystack_reference(
        self,
        paystack_reference: str,
    ) -> Optional[ApplicationForm]:
        """Get form by Paystack payment reference"""
        return await ApplicationForm.find_one({
            "paystack_reference": paystack_reference,
        })
    
    async def update(self, form_id: str, data: dict) -> Optional[ApplicationForm]:
        """Update an application form"""
        form = await ApplicationForm.get(form_id)
        if not form:
            return None
        
        await form.update({"$set": data})
        return await ApplicationForm.get(form_id)
    
    async def save(self, application_form: ApplicationForm) -> ApplicationForm:
        """Save (insert or update) an application form"""
        await application_form.save()
        return application_form
    
    async def delete(self, form_id: str) -> bool:
        """Delete an application form"""
        result = await ApplicationForm.delete(form_id)
        return result.deleted_count > 0
    
    async def count_by_status(
        self,
        status: ApplicationFormStatusEnum,
        admission_cycle_id: Optional[str] = None,
    ) -> int:
        """
        Count forms by status.
        
        Args:
            status: The status to filter by
            admission_cycle_id: Filter by cycle (optional)
        
        Returns:
            Count of matching forms
        """
        query = {"status": status}
        
        if admission_cycle_id:
            query["admission_cycle_id"] = admission_cycle_id
        
        return await ApplicationForm.find(query).count()
