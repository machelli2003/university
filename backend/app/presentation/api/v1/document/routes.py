from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional
from app.infrastructure.external_services.s3_service import S3Service
from app.infrastructure.database.repositories.document_repository import DocumentRepository, DigitalSignatureRepository
from app.infrastructure.external_services.qr_code_service import QRCodeService
from app.dependencies import get_current_user, require_roles, get_digital_signature_repo
from app.infrastructure.models.user import User

router = APIRouter()

def get_document_repo() -> DocumentRepository:
    return DocumentRepository()

def get_qr_service() -> QRCodeService:
    return QRCodeService()

def get_s3_service() -> S3Service:
    return S3Service()


def get_digital_signature_repo() -> DigitalSignatureRepository:
    return DigitalSignatureRepository()

@router.post("/upload")
async def create_document(
    document_name: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_repo=Depends(get_document_repo),
    qr_service: QRCodeService = Depends(get_qr_service),
    s3_service: S3Service = Depends(get_s3_service),
):
    file_bytes = await file.read()
    upload_result = await s3_service.upload_file(
        file_content=file_bytes,
        file_name=f"{current_user.tenant_id or 'default'}/{document_type}/{file.filename}",
        content_type=file.content_type or "application/octet-stream",
    )

    if not upload_result.get("uploaded") and not upload_result.get("stub"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=upload_result.get("message", "File upload failed"))

    document = await document_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "uploaded_by": str(current_user.id),
        "document_name": document_name,
        "document_type": document_type,
        "file_url": upload_result["url"],
    })

    qr_code = qr_service.generate_verification_qr(
        document_type, str(document.id), "https://eump-frontend.onrender.com"
    )

    await document_repo.update(str(document.id), {"qr_code": qr_code})

    return {"id": str(document.id), "qr_code": qr_code, "file_url": upload_result["url"]}

@router.get("/verify/{document_id}")
async def verify_document(
    document_id: str,
    document_repo=Depends(get_document_repo),
):
    """Public endpoint - no auth required for verification"""
    document = await document_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {
        "document_name": document.document_name,
        "document_type": document.document_type,
        "is_signed": document.is_signed,
        "uploaded_at": document.uploaded_at,
        "verified": True,
    }

@router.get("/my-documents")
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    document_repo=Depends(get_document_repo),
):
    documents = await document_repo.get_by_uploader(str(current_user.id))
    return [{"id": str(d.id), "document_name": d.document_name, "document_type": d.document_type} for d in documents]


@router.get("/search")
async def search_documents(
    document_type: Optional[str] = None,
    uploaded_by: Optional[str] = None,
    signed: Optional[bool] = None,
    current_user: User = Depends(require_roles("registrar", "university_admin", "super_admin")),
    document_repo=Depends(get_document_repo),
):
    documents = await document_repo.search(
        current_user.tenant_id or "default",
        document_type=document_type,
        uploaded_by=uploaded_by,
        signed=signed,
    )
    return [
        {
            "id": str(d.id),
            "document_name": d.document_name,
            "document_type": d.document_type,
            "is_signed": d.is_signed,
            "signed_by": d.signed_by,
            "uploaded_by": d.uploaded_by,
            "uploaded_at": d.uploaded_at,
            "file_url": d.file_url,
        }
        for d in documents
    ]


@router.post("/{document_id}/sign")
async def sign_document(
    document_id: str,
    current_user: User = Depends(require_roles("registrar", "university_admin", "super_admin")),
    document_repo=Depends(get_document_repo),
    signature_repo=Depends(get_digital_signature_repo),
):
    document = await document_repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if document.tenant_id != (current_user.tenant_id or "default"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied for this document")

    if document.is_signed:
        return {"document_id": document_id, "signed": True, "message": "Document already signed"}

    signature = await signature_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "signer_id": str(current_user.id),
        "document_id": document_id,
        "signature_data": f"Signed by {current_user.first_name} {current_user.last_name}",
    })

    await document_repo.update(document_id, {"is_signed": True, "signed_by": str(current_user.id)})

    return {"document_id": document_id, "signed": True, "signature_id": str(signature.id)}
