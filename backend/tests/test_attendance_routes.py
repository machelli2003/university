import pytest
import asyncio
from datetime import datetime
from app.presentation.api.v1.attendance.routes import mark_attendance_via_qr, mark_attendance_public

class MockUser:
    def __init__(self, role, tenant_id, id_):
        self.role = type("R", (), {"value": role})
        self.tenant_id = tenant_id
        self.id = id_

class MockStudentRepo:
    def __init__(self, student):
        self.student = student
    async def get_by_user_id(self, tenant_id, user_id):
        return self.student
    async def get_by_student_id(self, tenant_id, student_id):
        return self.student if getattr(self.student, 'student_id', None) == student_id else None

class MockAttendanceRepo:
    def __init__(self):
        self.created = []
    async def create(self, data):
        self.created.append(data)
        class R: pass
        r = R(); r.id = 'rec1'; return r

@pytest.mark.asyncio
async def test_mark_attendance_via_qr_student():
    student = type('S', (), {'student_id':'STU001','tenant_id':'t1'})()
    user = MockUser('student','t1','u1')
    student_repo = MockStudentRepo(student)
    attendance_repo = MockAttendanceRepo()

    res = await mark_attendance_via_qr('C1','sess1', current_user=user, student_repo=student_repo, attendance_repo=attendance_repo)
    assert res['status'] == 'recorded'
    assert attendance_repo.created[0]['student_id'] == 'STU001'

@pytest.mark.asyncio
async def test_mark_attendance_public():
    student = type('S', (), {'student_id':'STU002','tenant_id':'t1'})()
    student_repo = MockStudentRepo(student)
    attendance_repo = MockAttendanceRepo()

    res = await mark_attendance_public('C1','sess2', {'student_id':'STU002'}, student_repo=student_repo, attendance_repo=attendance_repo)
    assert res['status'] == 'recorded'
    assert attendance_repo.created[0]['method'] == 'public'
