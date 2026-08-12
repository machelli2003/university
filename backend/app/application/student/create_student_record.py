from datetime import datetime
from app.infrastructure.database.repositories.applicant_repository import ApplicantRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.models.student import StudentStatusEnum

class CreateStudentRecordUseCase:
    """Auto-create student record when applicant accepts offer"""

    def __init__(
        self,
        applicant_repo: ApplicantRepository,
        student_repo: StudentRepository
    ):
        self.applicant_repo = applicant_repo
        self.student_repo = student_repo

    async def execute(self, applicant_id: str, tenant_id: str) -> dict:
        applicant = await self.applicant_repo.get_by_id(applicant_id)

        if not applicant:
            raise ValueError("Applicant not found")

        if applicant.status != "accepted":
            raise ValueError("Applicant must accept offer before student record creation")

        if applicant.student_id:
            raise ValueError("Student record already exists")

        year = datetime.utcnow().year
        count = await self.student_repo.count(tenant_id=tenant_id)
        student_id = f"UNIV/{year}/{count + 1:05d}"

        student_data = {
            "tenant_id": tenant_id,
            "user_id": applicant.user_id,
            "applicant_id": applicant_id,
            "first_name": applicant.first_name,
            "last_name": applicant.last_name,
            "student_id": student_id,
            "date_of_birth": applicant.date_of_birth,
            "gender": applicant.gender,
            "phone": applicant.phone,
            "email": "",
            "programme_id": applicant.allocated_programme_id,
            "faculty_id": "",
            "department_id": "",
            "entry_level": "100",
            "entry_semester": "1",
            "entry_year": year,
            "status": StudentStatusEnum.REGISTERED,
        }

        student = await self.student_repo.create(student_data)

        await self.applicant_repo.update(applicant_id, {
            "student_id": str(student.id)
        })

        return {"student_id": str(student.id), "student_code": student_id}
