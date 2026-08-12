from typing import Optional, Tuple, Dict
from datetime import datetime
import httpx
from app.config import get_settings

settings = get_settings()

class WAECService:
    """
    WAEC result verification service

    For now: STUB implementation with manual entry approval workflow
    When WAEC API available: Replace with actual API calls
    """

    def __init__(self):
        self.api_enabled = settings.WAEC_API_ENABLED
        self.api_base_url = settings.WAEC_API_BASE_URL or "https://waec.api.example.com"
        self.api_key = settings.WAEC_API_KEY

    async def verify_results(
        self,
        index_number: str,
        exam_year: int,
        exam_type: str,
        pin: Optional[str] = None
    ) -> Tuple[bool, Optional[dict], str]:
        if self.api_enabled:
            return await self._verify_via_api(index_number, exam_year, exam_type, pin)
        else:
            return await self._verify_manual_stub(index_number, exam_year, exam_type)

    async def _verify_via_api(
        self,
        index_number: str,
        exam_year: int,
        exam_type: str,
        pin: str
    ) -> Tuple[bool, Optional[dict], str]:
        """
        Call WAEC API for result verification
        """
        if not self.api_key:
            return False, None, "WAEC API key is not configured"

        payload = {
            "index_number": index_number,
            "exam_year": exam_year,
            "exam_type": exam_type,
            "pin": pin,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(f"{self.api_base_url}/verify", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

            verified = data.get("verified", False)
            details = data.get("details", {})
            message = data.get("message", "Verification completed")
            return verified, details, message
        except httpx.HTTPStatusError as exc:
            return False, None, f"WAEC API returned {exc.response.status_code}: {exc.response.text}"
        except Exception as exc:
            return False, None, f"WAEC API error: {str(exc)}"

    async def _verify_manual_stub(
        self,
        index_number: str,
        exam_year: int,
        exam_type: str
    ) -> Tuple[bool, Optional[dict], str]:
        """
        Stub: Manual verification required
        Applicant provides results -> Admin approves via UI
        """
        return False, None, "Manual verification required. Applicant must upload results for admin approval."

    async def validate_exam_credentials(
        self,
        index_number: str,
        exam_year: int,
        exam_type: str
    ) -> Tuple[bool, str]:
        if not index_number or len(index_number) < 10:
            return False, "Invalid index number format"

        current_year = datetime.utcnow().year
        if exam_year < 2015 or exam_year > current_year:
            return False, "Exam year out of valid range"

        valid_types = ["WASSCE", "NECO", "IB", "A-LEVELS"]
        if exam_type not in valid_types:
            return False, f"Exam type must be one of: {', '.join(valid_types)}"

        return True, "Credentials valid"

class ManualResultsEntryService:
    """
    Handle manual results entry for testing (before WAEC API)
    Applicant enters results -> Admin approves -> Updates applicant record
    """

    def __init__(self):
        pass

    async def create_result_entry(
        self,
        applicant_id: str,
        subject: str,
        grade: str,
        uploaded_by: str
    ) -> Dict:
        valid_grades = ["A1", "A", "B2", "B3", "C4", "C5", "C6", "D7", "D8", "E", "F"]
        if grade not in valid_grades:
            raise ValueError(f"Invalid grade. Must be one of: {', '.join(valid_grades)}")

        return {
            "applicant_id": applicant_id,
            "subject": subject,
            "grade": grade,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.utcnow(),
            "status": "pending_approval"
        }

    async def submit_for_approval(
        self,
        applicant_id: str,
        results: Dict[str, str]
    ) -> Dict:
        return {
            "applicant_id": applicant_id,
            "results": results,
            "status": "awaiting_approval",
            "submitted_at": datetime.utcnow()
        }

    async def approve_results(
        self,
        applicant_id: str,
        approved_by: str,
        results: Dict[str, str]
    ) -> Dict:
        return {
            "applicant_id": applicant_id,
            "results": results,
            "status": "approved",
            "approved_by": approved_by,
            "approved_at": datetime.utcnow()
        }

    async def reject_results(
        self,
        applicant_id: str,
        rejection_reason: str,
        reviewed_by: str
    ) -> Dict:
        return {
            "applicant_id": applicant_id,
            "status": "rejected",
            "rejection_reason": rejection_reason,
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow()
        }
