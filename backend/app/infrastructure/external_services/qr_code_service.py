import qrcode
import base64
from io import BytesIO
from typing import Optional

class QRCodeService:
    """Generate QR codes for verification (documents, attendance, student ID)"""

    def __init__(self):
        pass

    def generate_qr_code(self, data: str, box_size: int = 10) -> str:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_base64}"

    def generate_verification_qr(self, entity_type: str, entity_id: str, base_url: str) -> str:
        verification_url = f"{base_url}/verify/{entity_type}/{entity_id}"
        return self.generate_qr_code(verification_url)

    def generate_attendance_qr(self, course_id: str, session_id: str, base_url: str) -> str:
        attendance_url = f"{base_url}/attendance/mark/{course_id}/{session_id}"
        return self.generate_qr_code(attendance_url)
