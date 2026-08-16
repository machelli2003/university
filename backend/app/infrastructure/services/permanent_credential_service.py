"""
Permanent Credential Service

Manages the issuance of real, permanent credentials after applicants are accepted.
Handles transition from temporary PIN+Serial to permanent username/password.
"""

import secrets
import string
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.infrastructure.models import PermanentCredential, CredentialStatusEnum, ApplicationForm

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PermanentCredentialService:
    """
    Service for managing permanent credentials issued after acceptance.
    
    Workflow:
    1. Applicant is OFFERED admission
    2. System generates real username and temporary password
    3. PermanentCredential record created
    4. ApplicationForm marked with credential_issued_at
    5. Credentials sent to applicant via email
    6. On first login, applicant must change temporary password
    """
    
    def __init__(self):
        pass
    
    def _generate_username(self, email: str, first_name: str, last_name: str) -> str:
        """
        Generate a unique username from email or name.
        
        Strategy:
        1. Try: firstname.lastname (if not taken)
        2. Try: email prefix (if not taken)
        3. Try: firstname + random suffix (if collision)
        """
        # Extract email prefix
        email_prefix = email.split("@")[0].lower()
        
        # Try simple format first
        base_username = email_prefix
        
        return base_username
    
    def _generate_temporary_password(self, length: int = 12) -> str:
        """
        Generate a strong temporary password.
        
        Requirements:
        - At least 12 characters
        - Mix of upper, lower, digits, special chars
        - Easy to read (no confusing chars like l, 0, O, 1)
        """
        # Character sets (excluding confusing characters)
        lowercase = "abcdefghijkmnpqrstuvwxyz"
        uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        digits = "23456789"
        special = "!@#$%^&*"
        
        # Ensure at least one of each type
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(special),
        ]
        
        # Fill the rest randomly
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle
        secrets.SystemRandom().shuffle(password)
        return "".join(password)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    async def is_username_available(self, username: str) -> bool:
        """Check if username is already taken"""
        existing = await PermanentCredential.find_one({"username": username.lower()})
        return existing is None
    
    async def generate_credentials(
        self,
        applicant_id: str,
        application_form_id: str,
        email: str,
        first_name: str,
        last_name: str,
        admission_cycle_id: str,
        academic_year: str,
        issued_by: str = "system",
    ) -> Dict[str, Any]:
        """
        Generate permanent credentials for an accepted applicant.
        
        Called when applicant is marked as OFFERED.
        
        Args:
            applicant_id: ID of the applicant/user
            application_form_id: ID of the application form
            email: Applicant email
            first_name: First name
            last_name: Last name
            admission_cycle_id: Admission cycle
            academic_year: Academic year
            issued_by: Admin/system ID that issued these
        
        Returns:
            Dict with username and temporary_password
        
        Raises:
            Exception if credentials already exist for this applicant
        """
        try:
            # Check if credentials already exist
            existing = await PermanentCredential.find_one({
                "applicant_id": applicant_id
            })
            
            if existing and existing.status != CredentialStatusEnum.DEACTIVATED:
                logger.warning(f"Credentials already exist for applicant {applicant_id}")
                raise Exception(f"Credentials already generated for this applicant")
            
            # Generate username
            username = self._generate_username(email, first_name, last_name)
            
            # Ensure username is unique
            attempts = 0
            while not await self.is_username_available(username) and attempts < 5:
                # Add random suffix if collision
                random_suffix = ''.join(secrets.choice(string.digits) for _ in range(3))
                username = f"{username}{random_suffix}"
                attempts += 1
            
            if attempts >= 5:
                raise Exception("Failed to generate unique username")
            
            # Generate temporary password
            temporary_password = self._generate_temporary_password()
            temp_password_hash = self._hash_password(temporary_password)
            
            # Generate permanent password (will be set on first login)
            # For now, hash the temporary password
            permanent_password_hash = temp_password_hash
            
            # Create PermanentCredential record
            credential = PermanentCredential(
                applicant_id=applicant_id,
                application_form_id=application_form_id,
                username=username.lower(),
                email=email,
                password_hash=permanent_password_hash,
                temporary_password_hash=temp_password_hash,
                is_temporary_password=True,
                admission_cycle_id=admission_cycle_id,
                academic_year=academic_year,
                status=CredentialStatusEnum.GENERATED,
                issued_by=issued_by,
                issued_reason="admission_offered",
                password_change_required=True,
                activation_deadline=datetime.utcnow() + timedelta(days=30),  # 30 days to activate
            )
            
            await credential.save()
            
            logger.info(f"Generated credentials for applicant {applicant_id}: username={username}")
            
            return {
                "username": username,
                "temporary_password": temporary_password,
                "credential_id": str(credential.id),
                "activation_deadline": credential.activation_deadline,
                "must_change_password": True,
            }
            
        except Exception as e:
            logger.error(f"Error generating credentials: {e}")
            raise
    
    async def issue_credentials_for_applicant(
        self,
        application_form: ApplicationForm,
        issued_by: str = "system",
    ) -> Dict[str, Any]:
        """
        Issue real credentials for an applicant with accepted application.
        
        Args:
            application_form: The ApplicationForm record
            issued_by: Admin/system that issued the credentials
        
        Returns:
            Credentials dictionary with username and password
        """
        try:
            # Generate credentials
            credentials = await self.generate_credentials(
                applicant_id=application_form.applicant_id,
                application_form_id=str(application_form.id),
                email=application_form.applicant_email,
                first_name=application_form.first_name or "Student",
                last_name=application_form.last_name or "User",
                admission_cycle_id=application_form.admission_cycle_id,
                academic_year=application_form.academic_year,
                issued_by=issued_by,
            )
            
            # Update ApplicationForm to mark credentials as issued
            application_form.permanent_credential_id = credentials["credential_id"]
            application_form.has_real_credentials = True
            application_form.credential_issued_at = datetime.utcnow()
            application_form.status = "expired"  # PIN/Serial no longer valid
            await application_form.save()
            
            logger.info(f"Issued real credentials for application {application_form.id}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error issuing credentials: {e}")
            raise
    
    async def verify_password(self, credential_id: str, password: str) -> bool:
        """Verify a password against stored hash"""
        credential = await PermanentCredential.get(credential_id)
        if not credential:
            return False
        
        return pwd_context.verify(password, credential.password_hash)
    
    async def change_password(
        self,
        credential_id: str,
        old_password: str,
        new_password: str,
    ) -> bool:
        """
        Change password for permanent credentials.
        
        Called when applicant logs in for first time with temp password.
        """
        credential = await PermanentCredential.get(credential_id)
        if not credential:
            raise Exception("Credential not found")
        
        # Verify old password (could be temporary or existing)
        if not pwd_context.verify(old_password, credential.password_hash):
            raise Exception("Current password is incorrect")
        
        # Hash and store new password
        new_hash = self._hash_password(new_password)
        credential.password_hash = new_hash
        credential.is_temporary_password = False
        credential.password_change_required = False
        credential.last_password_change = datetime.utcnow()
        
        await credential.save()
        
        logger.info(f"Password changed for credential {credential_id}")
        
        return True
    
    async def get_by_username(self, username: str) -> Optional[PermanentCredential]:
        """Find credentials by username"""
        return await PermanentCredential.find_one({
            "username": username.lower(),
            "is_active": True,
        })
    
    async def get_by_applicant_id(self, applicant_id: str) -> Optional[PermanentCredential]:
        """Find credentials by applicant ID"""
        return await PermanentCredential.find_one({
            "applicant_id": applicant_id,
            "is_active": True,
        })
    
    async def deactivate_credentials(self, credential_id: str, reason: str = "manual") -> bool:
        """Deactivate credentials"""
        credential = await PermanentCredential.get(credential_id)
        if not credential:
            return False
        
        credential.is_active = False
        credential.status = CredentialStatusEnum.DEACTIVATED
        credential.notes = f"Deactivated: {reason}"
        await credential.save()
        
        return True
