from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Document(Document):
    tenant_id: str
    uploaded_by: str

    document_name: str
    document_type: str
    file_url: str

    is_signed: bool = False
    signed_by: Optional[str] = None
    qr_code: Optional[str] = None

    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"

class DigitalSignature(Document):
    tenant_id: str
    signer_id: str
    document_id: str

    signature_data: str
    signed_date: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "digital_signatures"
