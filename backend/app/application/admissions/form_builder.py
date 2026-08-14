"""
Application Form Builder Service
Items 19-31: Build and manage dynamic application forms

Service for:
- Creating custom forms per university
- Managing form versions
- Validating form submissions
- Storing applicant responses
"""

from app.domain.models.application_form import (
    ApplicationForm, FormSection, FormField, FilledApplicationForm,
    ApplicationDocument, WAESSESection, FieldType
)
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class FormBuilderService:
    """
    Build and manage university-specific application forms.
    
    Allows universities to customize what data they collect from applicants.
    """
    
    async def create_form(
        self,
        tenant_id: str,
        name: str,
        sections: List[Dict[str, Any]],
        collect_wassce: bool = True,
        collect_documents: bool = True,
        documents_required: List[str] = None,
        application_fee: float = 0.0,
        admission_cycle_id: Optional[str] = None,
    ) -> ApplicationForm:
        """
        Create a new application form.
        
        Args:
            tenant_id: University tenant
            name: Form name
            sections: List of form sections with fields
            collect_wassce: Whether to collect WASSCE results
            collect_documents: Whether to collect supporting documents
            documents_required: List of required document types
            application_fee: Fee to apply
            admission_cycle_id: Optional per-cycle form
        
        Returns:
            Created ApplicationForm
        """
        # Convert section dicts to FormSection objects
        form_sections = []
        for section_data in sections:
            fields = []
            for field_data in section_data.get("fields", []):
                field = FormField(**field_data)
                fields.append(field)
            
            section = FormSection(
                title=section_data["title"],
                description=section_data.get("description"),
                fields=fields,
                order=section_data.get("order", 0),
            )
            form_sections.append(section)
        
        # Create form
        form = ApplicationForm(
            tenant_id=tenant_id,
            name=name,
            sections=form_sections,
            collect_wassce=collect_wassce,
            collect_documents=collect_documents,
            documents_required=documents_required or [],
            application_fee=application_fee,
            admission_cycle_id=admission_cycle_id,
            is_active=True,
        )
        
        await form.save()
        logger.info(f"✅ Form '{name}' created for tenant {tenant_id}")
        return form
    
    async def get_form(self, form_id: str, tenant_id: str) -> Optional[ApplicationForm]:
        """Get form by ID (tenant-scoped)."""
        return await ApplicationForm.find_one(
            ApplicationForm.id == form_id,
            ApplicationForm.tenant_id == tenant_id,
        )
    
    async def get_active_form(
        self,
        tenant_id: str,
        admission_cycle_id: Optional[str] = None,
    ) -> Optional[ApplicationForm]:
        """
        Get the active form for a tenant.
        
        If admission_cycle_id provided, get cycle-specific form.
        Otherwise, get the default active form.
        """
        if admission_cycle_id:
            return await ApplicationForm.find_one(
                ApplicationForm.tenant_id == tenant_id,
                ApplicationForm.admission_cycle_id == admission_cycle_id,
                ApplicationForm.is_active == True,
            )
        
        return await ApplicationForm.find_one(
            ApplicationForm.tenant_id == tenant_id,
            ApplicationForm.admission_cycle_id == None,
            ApplicationForm.is_active == True,
        )
    
    async def update_form(
        self,
        form_id: str,
        tenant_id: str,
        **updates,
    ) -> Optional[ApplicationForm]:
        """Update form fields."""
        form = await self.get_form(form_id, tenant_id)
        if not form:
            return None
        
        # Update allowed fields
        for key, value in updates.items():
            if key in ["name", "description", "sections", "collect_wassce", 
                      "collect_documents", "documents_required", "application_fee"]:
                setattr(form, key, value)
        
        form.updated_at = datetime.utcnow()
        await form.save()
        return form
    
    async def validate_form_submission(
        self,
        form: ApplicationForm,
        form_data: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """
        Validate applicant's form submission against form definition.
        
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check all required fields are present
        for section in form.sections:
            for field in section.fields:
                if field.required and field.name not in form_data:
                    errors.append(f"{field.label} is required")
                    continue
                
                value = form_data.get(field.name)
                if value is None:
                    continue
                
                # Validate field value
                field_errors = self._validate_field(field, value)
                errors.extend(field_errors)
        
        return len(errors) == 0, errors
    
    def _validate_field(self, field: FormField, value: Any) -> List[str]:
        """Validate individual field value."""
        errors = []
        
        # Type validation
        if field.field_type == FieldType.EMAIL:
            if not self._is_valid_email(value):
                errors.append(f"{field.label} must be a valid email")
        
        elif field.field_type == FieldType.PHONE:
            if not self._is_valid_phone(value):
                errors.append(f"{field.label} must be a valid phone number")
        
        elif field.field_type == FieldType.NUMBER:
            try:
                num = float(value)
                if field.min_value and num < field.min_value:
                    errors.append(f"{field.label} must be >= {field.min_value}")
                if field.max_value and num > field.max_value:
                    errors.append(f"{field.label} must be <= {field.max_value}")
            except ValueError:
                errors.append(f"{field.label} must be a number")
        
        elif field.field_type == FieldType.DATE:
            try:
                datetime.fromisoformat(value)
            except:
                errors.append(f"{field.label} must be a valid date")
        
        elif field.field_type == FieldType.TEXT:
            if isinstance(value, str):
                if field.min_length and len(value) < field.min_length:
                    errors.append(f"{field.label} must be at least {field.min_length} chars")
                if field.max_length and len(value) > field.max_length:
                    errors.append(f"{field.label} must be at most {field.max_length} chars")
                if field.pattern:
                    import re
                    if not re.match(field.pattern, value):
                        errors.append(f"{field.label} format is invalid")
        
        elif field.field_type == FieldType.DROPDOWN:
            valid_values = [opt["value"] for opt in (field.options or [])]
            if value not in valid_values:
                errors.append(f"{field.label} has invalid selection")
        
        elif field.field_type == FieldType.RADIO:
            valid_values = [opt["value"] for opt in (field.options or [])]
            if value not in valid_values:
                errors.append(f"{field.label} has invalid selection")
        
        return errors
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Simple email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Simple phone validation."""
        import re
        # Accept +234, 0, or digits
        pattern = r'^[\+]?[0-9]{10,}$'
        return re.match(pattern, phone.replace("-", "").replace(" ", "")) is not None


class FilledFormService:
    """Service for managing filled application forms."""
    
    async def create_filled_form(
        self,
        tenant_id: str,
        applicant_id: str,
        form_id: str,
    ) -> FilledApplicationForm:
        """Create a new blank filled form (draft)."""
        filled = FilledApplicationForm(
            tenant_id=tenant_id,
            applicant_id=applicant_id,
            form_id=form_id,
            status="draft",
        )
        await filled.save()
        return filled
    
    async def get_filled_form(
        self,
        filled_form_id: str,
        tenant_id: str,
        applicant_id: str,
    ) -> Optional[FilledApplicationForm]:
        """Get applicant's filled form."""
        return await FilledApplicationForm.find_one(
            FilledApplicationForm.id == filled_form_id,
            FilledApplicationForm.tenant_id == tenant_id,
            FilledApplicationForm.applicant_id == applicant_id,
        )
    
    async def save_draft(
        self,
        filled_form_id: str,
        tenant_id: str,
        applicant_id: str,
        form_data: Dict[str, Any],
    ) -> Optional[FilledApplicationForm]:
        """Save form as draft (partial submission)."""
        filled = await self.get_filled_form(filled_form_id, tenant_id, applicant_id)
        if not filled:
            return None
        
        filled.form_data = form_data
        filled.status = "draft"
        filled.updated_at = datetime.utcnow()
        await filled.save()
        return filled
    
    async def submit_form(
        self,
        filled_form_id: str,
        tenant_id: str,
        applicant_id: str,
        form_data: Dict[str, Any],
        wassce_data: Optional[WAESSESection] = None,
    ) -> Optional[FilledApplicationForm]:
        """Submit filled form (transition to submitted state)."""
        filled = await self.get_filled_form(filled_form_id, tenant_id, applicant_id)
        if not filled:
            return None
        
        filled.form_data = form_data
        filled.wassce_data = wassce_data
        filled.status = "submitted"
        filled.submitted_at = datetime.utcnow()
        filled.updated_at = datetime.utcnow()
        await filled.save()
        
        logger.info(f"✅ Application submitted by applicant {applicant_id}")
        return filled
    
    async def add_document(
        self,
        filled_form_id: str,
        tenant_id: str,
        applicant_id: str,
        document_type: str,
        file_path: str,
        file_name: str,
        file_size_bytes: int,
    ) -> Optional[FilledApplicationForm]:
        """Add document to application."""
        filled = await self.get_filled_form(filled_form_id, tenant_id, applicant_id)
        if not filled:
            return None
        
        doc = ApplicationDocument(
            document_type=document_type,
            file_path=file_path,
            file_name=file_name,
            file_size_bytes=file_size_bytes,
        )
        filled.documents.append(doc)
        filled.updated_at = datetime.utcnow()
        await filled.save()
        
        logger.info(f"✅ Document '{document_type}' added to application {filled_form_id}")
        return filled
    
    async def mark_payment_verified(
        self,
        filled_form_id: str,
        tenant_id: str,
        applicant_id: str,
        payment_reference: str,
    ) -> Optional[FilledApplicationForm]:
        """Mark payment as verified."""
        filled = await self.get_filled_form(filled_form_id, tenant_id, applicant_id)
        if not filled:
            return None
        
        filled.payment_reference = payment_reference
        filled.payment_verified = True
        filled.payment_verified_at = datetime.utcnow()
        filled.updated_at = datetime.utcnow()
        await filled.save()
        return filled
