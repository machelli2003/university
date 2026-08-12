from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from datetime import datetime
from app.dependencies import get_current_user, get_course_repo, get_s3_service
from app.infrastructure.models.user import User
from app.infrastructure.database.repositories.course_material_repository import CourseMaterialRepository
from app.infrastructure.external_services.s3_service import S3Service

router = APIRouter()

def get_course_material_repo() -> CourseMaterialRepository:
    return CourseMaterialRepository()

@router.post("/courses/{course_id}/materials")
async def upload_course_material(
    course_id: str,
    title: str,
    material_type: str,
    description: str | None = None,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    course_repo=Depends(get_course_repo),
    s3_service: S3Service = Depends(get_s3_service),
    material_repo=Depends(get_course_material_repo),
):
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.value != "lecturer" and current_user.role.value not in ("university_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Requires lecturer role")
    if course.lecturer_id != str(current_user.id) and current_user.role.value not in ("university_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    content = await file.read()
    upload_result = await s3_service.upload_file(content, file.filename)
    file_url = upload_result.get("url") if isinstance(upload_result, dict) else None
    if not file_url:
        raise HTTPException(status_code=500, detail="File upload failed")

    material = await material_repo.create({
        "tenant_id": current_user.tenant_id,
        "course_id": course_id,
        "uploaded_by": str(current_user.id),
        "title": title,
        "description": description,
        "file_url": file_url,
        "material_type": material_type,
        "uploaded_at": datetime.utcnow(),
    })

    return {"id": str(material.id), "file_url": file_url}

@router.get("/courses/{course_id}/materials")
async def list_course_materials(
    course_id: str,
    current_user: User = Depends(get_current_user),
    course_repo=Depends(get_course_repo),
    material_repo=Depends(get_course_material_repo),
):
    course = await course_repo.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if current_user.role.value != "lecturer" and current_user.role.value not in ("university_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Requires lecturer role")
    if course.lecturer_id != str(current_user.id) and current_user.role.value not in ("university_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Not authorized for this course")

    materials = await material_repo.get_by_course(current_user.tenant_id or "default", course_id)
    return [
        {
            "id": str(m.id),
            "title": m.title,
            "description": m.description,
            "file_url": m.file_url,
            "material_type": m.material_type,
            "uploaded_at": m.uploaded_at.isoformat(),
        }
        for m in materials
    ]
