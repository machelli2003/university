from pydantic import BaseModel

class CreateDocumentRequest(BaseModel):
    document_name: str
    document_type: str
    file_url: str
