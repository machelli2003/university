from typing import Optional, Dict, List
from email.message import EmailMessage
import smtplib
import asyncio
import logging
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

class EmailService:
    """
    Email service that supports stub or SMTP providers.
    """

    def __init__(self):
        self.provider = settings.EMAIL_PROVIDER.lower() if settings.EMAIL_PROVIDER else "stub"
        self.enabled = self.provider == "smtp"

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> dict:
        if self.provider == "smtp":
            return await self._send_smtp(to, subject, body, html_body)

        logger.info(f"[EMAIL STUB] To: {to} | Subject: {subject}")
        logger.info(f"[EMAIL STUB] Body: {body[:200]}...")
        return {
            "sent": False,
            "stub": True,
            "message": "Email service not configured. Logged instead.",
            "to": to,
            "subject": subject,
        }

    async def _send_smtp(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> dict:
        if not settings.SMTP_HOST or not settings.SMTP_PORT or not settings.EMAIL_FROM_ADDRESS:
            logger.error("SMTP provider selected but SMTP_HOST/SMTP_PORT/EMAIL_FROM_ADDRESS is not configured")
            return {
                "sent": False,
                "message": "SMTP provider not fully configured.",
                "to": to,
            }

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM_ADDRESS
        msg["To"] = to
        msg.set_content(body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")

        try:
            await asyncio.to_thread(self._send_smtp_sync, msg)
            return {"sent": True, "to": to}
        except Exception as exc:
            logger.error(f"SMTP send failed: {exc}")
            return {"sent": False, "message": str(exc), "to": to}

    def _send_smtp_sync(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

    async def send_admission_offer(self, to: str, applicant_name: str, programme_name: str) -> dict:
        subject = f"Admission Offer - {programme_name}"
        body = f"Dear {applicant_name},\n\nCongratulations! You have been offered admission to {programme_name}."
        return await self.send_email(to, subject, body)

    async def send_results_approved(self, to: str, applicant_name: str) -> dict:
        subject = "Your Results Have Been Approved"
        body = f"Dear {applicant_name},\n\nYour submitted results have been reviewed and approved."
        return await self.send_email(to, subject, body)

    async def send_payment_receipt(self, to: str, amount: float, receipt_number: str) -> dict:
        subject = f"Payment Receipt - {receipt_number}"
        body = f"Your payment of GHS {amount:.2f} has been received. Receipt: {receipt_number}"
        return await self.send_email(to, subject, body)


class SMSService:
    """
    SMS service that supports stub or Twilio providers.
    """

    def __init__(self):
        self.provider = settings.SMS_PROVIDER.lower() if settings.SMS_PROVIDER else "stub"
        self.enabled = self.provider == "twilio"

    async def send_sms(self, to: str, message: str) -> dict:
        if self.provider == "twilio":
            return await self._send_twilio(to, message)

        logger.info(f"[SMS STUB] To: {to} | Message: {message[:100]}")
        return {
            "sent": False,
            "stub": True,
            "message": "SMS service not configured. Logged instead.",
            "to": to,
        }

    async def _send_twilio(self, to: str, message: str) -> dict:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN or not settings.TWILIO_FROM_NUMBER:
            logger.error("Twilio provider selected but credentials are not configured")
            return {"sent": False, "message": "Twilio not configured.", "to": to}

        url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        data = {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": to,
            "Body": message,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
                response.raise_for_status()
                return {"sent": True, "to": to, "provider": "twilio", "response": response.json()}
        except Exception as exc:
            logger.error(f"Twilio send failed: {exc}")
            return {"sent": False, "message": str(exc), "to": to}
