"""
Paystack payment service for application form purchases.

This service handles:
1. Payment initialization - get payment link from Paystack
2. Payment verification - confirm payment after callback
3. PIN/Serial generation - create unique credentials
4. Application form creation - store purchased forms
"""

import secrets
import string
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.infrastructure.models import ApplicationForm, ApplicationFormStatusEnum

logger = logging.getLogger(__name__)


class PaystackInitializeRequest(BaseModel):
    """Request to initialize a Paystack payment"""
    email: str
    amount: float  # Amount in Naira/Pesewa (multiply by 100 for Paystack)
    first_name: str
    last_name: str
    phone_number: str
    admission_cycle_id: str
    academic_year: str
    callback_url: str


class PaystackInitializeResponse(BaseModel):
    """Response from Paystack payment initialization"""
    status: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class PaystackVerifyResponse(BaseModel):
    """Response from Paystack payment verification"""
    status: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ApplicationFormPurchaseService:
    """
    Service to handle application form purchases via Paystack.
    
    Workflow:
    1. Applicant requests to purchase application form
    2. System calls initialize_payment() to get Paystack link
    3. Applicant pays via Paystack
    4. Paystack redirects back and we call verify_payment()
    5. If payment verified, generate PIN/serial and create ApplicationForm
    6. Return PIN/serial to applicant
    """
    
    def __init__(self, paystack_secret_key: str):
        self.paystack_secret_key = paystack_secret_key
        self.paystack_base_url = "https://api.paystack.co"
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {paystack_secret_key}",
                "Content-Type": "application/json",
            }
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
    
    def _generate_pin(self, length: int = 6) -> str:
        """Generate a random PIN (numeric only)"""
        digits = string.digits
        return "".join(secrets.choice(digits) for _ in range(length))
    
    def _generate_serial_number(self, length: int = 8) -> str:
        """
        Generate a serial number (alphanumeric, uppercase).
        Format example: AB12CD34
        """
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))
    
    async def initialize_payment(
        self,
        email: str,
        amount: float,  # Amount in Cedis
        first_name: str,
        last_name: str,
        phone_number: str,
        admission_cycle_id: str,
        academic_year: str,
        callback_url: str,
    ) -> Dict[str, Any]:
        """
        Initialize a Paystack payment for application form purchase.
        
        Args:
            email: Applicant email
            amount: Amount in Cedis (will be converted to pesewa for Paystack)
            first_name: Applicant first name
            last_name: Applicant last name
            phone_number: Applicant phone
            admission_cycle_id: The admission cycle ID
            academic_year: Academic year
            callback_url: URL to redirect to after payment
        
        Returns:
            Dict with payment_url and reference from Paystack
        """
        try:
            # Paystack expects amount in pesewa (1 GHS = 100 pesewa)
            amount_pesewa = int(amount * 100)
            
            payload = {
                "email": email,
                "amount": amount_pesewa,
                "metadata": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_number": phone_number,
                    "admission_cycle_id": admission_cycle_id,
                    "academic_year": academic_year,
                },
                "callback_url": callback_url,
            }
            
            response = await self.http_client.post(
                f"{self.paystack_base_url}/transaction/initialize",
                json=payload,
            )
            
            if response.status_code not in [200, 201]:
                logger.error(f"Paystack initialization failed: {response.text}")
                raise Exception(f"Paystack error: {response.text}")
            
            data = response.json()
            
            if not data.get("status"):
                logger.error(f"Paystack returned status=false: {data}")
                raise Exception(f"Payment initialization failed: {data.get('message')}")
            
            return {
                "payment_url": data["data"]["authorization_url"],
                "access_code": data["data"]["access_code"],
                "reference": data["data"]["reference"],
                "amount": amount,
            }
            
        except httpx.RequestError as e:
            logger.error(f"HTTP error during Paystack initialization: {e}")
            raise Exception(f"Payment service unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Error initializing payment: {e}")
            raise
    
    async def verify_payment(self, reference: str) -> Dict[str, Any]:
        """
        Verify a Paystack payment using the payment reference.
        
        Args:
            reference: Paystack payment reference
        
        Returns:
            Dict with payment details if verified, raises exception otherwise
        """
        try:
            response = await self.http_client.get(
                f"{self.paystack_base_url}/transaction/verify/{reference}"
            )
            
            if response.status_code != 200:
                logger.error(f"Paystack verification failed: {response.text}")
                raise Exception(f"Payment verification failed: {response.text}")
            
            data = response.json()
            
            if not data.get("status"):
                raise Exception(f"Payment not successful: {data.get('message')}")
            
            payment_data = data["data"]
            
            # Verify payment was successful
            if payment_data.get("status") != "success":
                raise Exception(f"Payment status is {payment_data.get('status')}")
            
            return {
                "reference": payment_data.get("reference"),
                "amount": payment_data.get("amount") / 100,  # Convert from pesewa to Cedis
                "status": payment_data.get("status"),
                "paid_at": payment_data.get("paid_at"),
                "customer": payment_data.get("customer", {}),
                "metadata": payment_data.get("metadata", {}),
            }
            
        except httpx.RequestError as e:
            logger.error(f"HTTP error during payment verification: {e}")
            raise Exception(f"Payment service unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Error verifying payment: {e}")
            raise
    
    async def create_application_form(
        self,
        applicant_email: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        admission_cycle_id: str,
        academic_year: str,
        amount: float,
        paystack_reference: str,
    ) -> ApplicationForm:
        """
        Generate PIN/serial and create an ApplicationForm record.
        
        Args:
            applicant_email: Email of the applicant
            first_name: First name
            last_name: Last name
            phone_number: Phone number
            admission_cycle_id: Admission cycle
            academic_year: Academic year
            amount: Amount paid
            paystack_reference: Paystack payment reference
        
        Returns:
            Created ApplicationForm document
        """
        # Generate unique PIN and serial
        pin = self._generate_pin()
        serial_number = self._generate_serial_number()
        
        # Ensure uniqueness by checking database
        while await ApplicationForm.find_one({"pin": pin}):
            pin = self._generate_pin()
        
        while await ApplicationForm.find_one({"serial_number": serial_number}):
            serial_number = self._generate_serial_number()
        
        # Create application form record
        form = ApplicationForm(
            pin=pin,
            serial_number=serial_number,
            admission_cycle_id=admission_cycle_id,
            academic_year=academic_year,
            applicant_email=applicant_email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            amount=amount,
            currency="GHS",
            payment_method="paystack",
            payment_reference=f"APPFORM-{pin}",  # Internal reference
            paystack_reference=paystack_reference,
            payment_status="completed",
            status=ApplicationFormStatusEnum.PURCHASED,
        )
        
        await form.save()
        logger.info(f"Created application form with PIN {pin} for {applicant_email}")
        
        return form
    
    async def get_form_by_pin_and_serial(
        self,
        pin: str,
        serial_number: str,
    ) -> Optional[ApplicationForm]:
        """
        Retrieve an application form by PIN and serial number.
        
        Args:
            pin: The PIN
            serial_number: The serial number
        
        Returns:
            ApplicationForm if found and valid, None otherwise
        """
        form = await ApplicationForm.find_one({
            "pin": pin,
            "serial_number": serial_number,
            "status": ApplicationFormStatusEnum.PURCHASED,
        })
        
        return form
    
    async def mark_form_as_used(
        self,
        form: ApplicationForm,
        applicant_id: str,
    ) -> ApplicationForm:
        """
        Mark an application form as used after successful login.
        
        Args:
            form: The ApplicationForm document
            applicant_id: ID of the applicant who used it
        
        Returns:
            Updated ApplicationForm
        """
        form.status = ApplicationFormStatusEnum.USED
        form.used_at = datetime.utcnow()
        form.first_login_at = datetime.utcnow()
        form.last_login_at = datetime.utcnow()
        form.login_count = 1
        form.applicant_id = applicant_id
        
        await form.save()
        logger.info(f"Marked application form {form.serial_number} as used by applicant {applicant_id}")
        
        return form
    
    async def track_login(self, form: ApplicationForm) -> ApplicationForm:
        """
        Track a login attempt with this form.
        
        Args:
            form: The ApplicationForm document
        
        Returns:
            Updated ApplicationForm
        """
        form.last_login_at = datetime.utcnow()
        form.login_count += 1
        
        await form.save()
        
        return form
