export interface CreateProposalRequest {
  title: string
  description: string
}

export interface ProposalItem {
  id: string
  title: string
  researcher_id: string
}

export interface CreateGrantRequest {
  title: string
  amount: number
}

export interface CreatePublicationRequest {
  title: string
  journal: string
  publication_date: string
  doi?: string
}

export interface PublicationItem {
  id: string
  title: string
  journal: string
}
