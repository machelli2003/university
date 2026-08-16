"""Seed script: create tenant, lecturer, student, course, fee structure, scholarship, payment for manual testing"""
import os
import sys

# Ensure backend directory is on Python path regardless of execution location
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from app.infrastructure.database.connection import init_db, close_db
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.student_repository import StudentRepository
from app.infrastructure.database.repositories.course_repository import CourseRepository
from app.infrastructure.database.repositories.payment_repository import FeeStructureRepository, PaymentRepository, ScholarshipRepository
from app.application.auth.login import AuthService

async def seed():
    await init_db()
    user_repo = UserRepository()
    student_repo = StudentRepository()
    course_repo = CourseRepository()
    fee_repo = FeeStructureRepository()
    payment_repo = PaymentRepository()
    sch_repo = ScholarshipRepository()

    auth = AuthService(user_repo)

    # create lecturer
    lec = await user_repo.create({
        'email':'lecturer@example.com','first_name':'Lee','last_name':'C','password_hash':auth.hash_password('password'), 'role':'lecturer'
    })
    print('created lecturer', lec.email)

    # create student user + student
    stu_user = await user_repo.create({
        'email':'student@example.com','first_name':'Stu','last_name':'Dent','password_hash':auth.hash_password('password'), 'role':'student'
    })
    student = await student_repo.create({
        'tenant_id': 'default', 'user_id': str(stu_user.id), 'first_name':'Stu','last_name':'Dent','student_id':'STU100','phone':'','email':'student@example.com','programme_id':'prog1','faculty_id':'fac1','department_id':'dep1','entry_level':'100','entry_semester':'1','entry_year':2024
    })
    print('created student', student.student_id)

    # create course
    course = await course_repo.create({'tenant_id':'default','code':'CSC101','name':'Intro to CS','credit_hours':3,'lecturer_id':str(lec.id)})
    print('created course', course.code)

    # fee structure
    fs = await fee_repo.create({'tenant_id':'default','programme_id':'prog1','academic_year':'2026','fees':{'tuition':1000,'lab':200}})
    print('created fee structure')

    # scholarship
    sch = await sch_repo.create({'tenant_id':'default','student_id':student.student_id,'name':'Merit','scholarship_type':'merit','amount':0,'percentage':25,'approved_by':str(lec.id),'approved_date': '2026-01-01','start_date':'2026-01-01','is_active':True})
    print('created scholarship')

    await close_db()

if __name__ == '__main__':
    asyncio.run(seed())
