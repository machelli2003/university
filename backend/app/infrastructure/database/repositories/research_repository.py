from app.infrastructure.models.research import ResearchProposal, Grant, Publication
from app.infrastructure.database.repositories.base_repository import BaseRepository
from typing import List

class ResearchProposalRepository(BaseRepository[ResearchProposal]):
    def __init__(self):
        super().__init__(ResearchProposal)

    async def get_by_researcher(self, researcher_id: str) -> List[ResearchProposal]:
        return await self.model.find({"researcher_id": researcher_id}).to_list(None)

    async def get_pending(self, tenant_id: str) -> List[ResearchProposal]:
        return await self.model.find({"tenant_id": tenant_id, "status": "submitted"}).to_list(None)

class GrantRepository(BaseRepository[Grant]):
    def __init__(self):
        super().__init__(Grant)

    async def get_by_researcher(self, researcher_id: str) -> List[Grant]:
        return await self.model.find({"researcher_id": researcher_id}).to_list(None)

class PublicationRepository(BaseRepository[Publication]):
    def __init__(self):
        super().__init__(Publication)

    async def get_by_researcher(self, researcher_id: str) -> List[Publication]:
        return await self.model.find({"researcher_id": researcher_id}).to_list(None)
