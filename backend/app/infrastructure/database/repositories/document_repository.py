from app.infrastructure.models.document import Document, DigitalSignature
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List, Optional

class DocumentRepository(BaseRepository[Document]):
    def __init__(self):
        super().__init__(Document)

    async def get_by_uploader(self, uploaded_by: str) -> List[Document]:
        return await self.model.find({"uploaded_by": uploaded_by}).to_list(None)

    async def get_by_type(self, tenant_id: str, document_type: str) -> List[Document]:
        return await self.model.find({"tenant_id": tenant_id, "document_type": document_type}).to_list(None)

    async def search(
        self,
        tenant_id: str,
        document_type: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        signed: Optional[bool] = None,
    ) -> List[Document]:
        filters = {"tenant_id": tenant_id}
        if document_type is not None:
            filters["document_type"] = document_type
        if uploaded_by is not None:
            filters["uploaded_by"] = uploaded_by
        if signed is not None:
            filters["is_signed"] = signed
        return await self.model.find(filters).sort([("uploaded_at", -1)]).to_list(None)

class DigitalSignatureRepository(BaseRepository[DigitalSignature]):
    def __init__(self):
        super().__init__(DigitalSignature)

    async def get_by_document(self, document_id: str) -> Optional[DigitalSignature]:
        return await self.model.find_one({"document_id": document_id})
