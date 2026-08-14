from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
from datetime import datetime


def generate_receipt_pdf(payment: dict, tenant: dict | None = None) -> bytes:
    """Generate a simple PDF receipt and return bytes.

    Args:
        payment: dict-like object with keys `receipt_number`, `amount`, `payment_reference`, `payment_date`, `student_id`.
        tenant: optional tenant info for header/title
    Returns:
        PDF file bytes
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    title = "Payment Receipt"
    if tenant and tenant.get("name"):
        title = f"{tenant.get('name')} - {title}"

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 72, title)

    c.setFont("Helvetica", 12)
    y = height - 110
    c.drawString(72, y, f"Receipt Number: {payment.get('receipt_number')}")
    y -= 20
    paid_at = payment.get("payment_date")
    if isinstance(paid_at, datetime):
        paid_at = paid_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    c.drawString(72, y, f"Date: {paid_at}")
    y -= 20
    c.drawString(72, y, f"Amount: GHS {payment.get('amount'):.2f}")
    y -= 20
    c.drawString(72, y, f"Payment Reference: {payment.get('payment_reference')}")
    y -= 20
    if payment.get('student_id'):
        c.drawString(72, y, f"Student ID: {payment.get('student_id')}")
        y -= 20

    y -= 10
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(72, y, "This is an auto-generated receipt. For enquiries contact support.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
