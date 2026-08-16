"""
Repository for PermanentCredential documents.

Handles database operations for permanent credentials.
"""

from typing import Optional, List
from app.infrastructure.models import PermanentCredential, CredentialStatusEnum


class PermanentCredentialRepository:
    """
    Repository for PermanentCredential data access.
    """
    
    async def create(self, credential: PermanentCredential) -> PermanentCredential:
        """Save a new credential"""
        await credential.save()
        return credential
    
    async def get_by_id(self, credential_id: str) -> Optional[PermanentCredential]:
        """Get credential by MongoDB ID"""
        return await PermanentCredential.get(credential_id)
    
    async def get_by_username(self, username: str) -> Optional[PermanentCredential]:
        """Get credential by username (case-insensitive)"""
        return await PermanentCredential.find_one({
            "username": username.lower(),
            "is_active": True,
        })
    
    async def get_by_email(self, email: str) -> Optional[PermanentCredential]:
        """Get credential by email"""
        return await PermanentCredential.find_one({
            "email": email.lower(),
            "is_active": True,
        })
    
    async def get_by_applicant_id(self, applicant_id: str) -> Optional[PermanentCredential]:
        """Get credential by applicant ID"""
        return await PermanentCredential.find_one({
            "applicant_id": applicant_id,
            "is_active": True,
        })
    
    async def get_by_application_form_id(self, application_form_id: str) -> Optional[PermanentCredential]:
        """Get credential by application form ID"""
        return await PermanentCredential.find_one({
            "application_form_id": application_form_id,
            "is_active": True,
        })
    
    async def get_all_by_status(
        self,
        status: CredentialStatusEnum,
        admission_cycle_id: Optional[str] = None,
    ) -> List[PermanentCredential]:
        """Get all credentials by status"""
        query = {"status": status}
        
        if admission_cycle_id:
            query["admission_cycle_id"] = admission_cycle_id
        
        return await PermanentCredential.find(query).to_list()
    
    async def get_by_admission_cycle(
        self,
        admission_cycle_id: str,
    ) -> List[PermanentCredential]:
        """Get all credentials issued in a cycle"""
        return await PermanentCredential.find({
            "admission_cycle_id": admission_cycle_id,
            "is_active": True,
        }).to_list()
    
    async def update(self, credential_id: str, data: dict) -> Optional[PermanentCredential]:
        """Update credential"""
        credential = await PermanentCredential.get(credential_id)
        if not credential:
            return None
        
        await credential.update({"$set": data})
        return await PermanentCredential.get(credential_id)
    
    async def save(self, credential: PermanentCredential) -> PermanentCredential:
        """Save (insert or update) credential"""
        await credential.save()
        return credential
    
    async def delete(self, credential_id: str) -> bool:
        """Delete credential"""
        result = await PermanentCredential.delete(credential_id)
        return result.deleted_count > 0
    
    async def count_active(self, admission_cycle_id: Optional[str] = None) -> int:
        """Count active credentials"""
        query = {"is_active": True}
        
        if admission_cycle_id:
            query["admission_cycle_id"] = admission_cycle_id
        
        return await PermanentCredential.find(query).count()
    
    async def count_requiring_password_change(self) -> int:
        """Count credentials that need password change"""
        return await PermanentCredential.find({
            "password_change_required": True,
            "is_active": True,
        }).count()
