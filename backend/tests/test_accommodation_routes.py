import pytest
import asyncio
from fastapi import HTTPException

from app.presentation.api.v1.accommodation.routes import (
    create_hall, create_room, allocate_room, report_maintenance, list_pending_maintenance
)
from app.presentation.api.v1.accommodation.schemas import (
    CreateHallRequest, CreateRoomRequest, AllocateRoomRequest, MaintenanceRequestCreate
)

class MockUser:
    def __init__(self, tenant_id, id_="u1"):
        self.tenant_id = tenant_id
        self.id = id_


class MockHallRepo:
    def __init__(self):
        self.created = []
    async def create(self, data):
        class H: pass
        h = H(); h.id = 'H1'; h.name = data.get('name'); h.capacity = data.get('capacity')
        self.created.append(data)
        return h


class MockRoomRepo:
    def __init__(self, room=None):
        self.room = room
        self.updated = []
    async def create(self, data):
        class R: pass
        r = R(); r.id = 'R1'; r.room_number = data.get('room_number'); r.room_type = data.get('room_type'); r.capacity = data.get('capacity'); r.occupied = 0; r.students = []
        self.room = r
        return r
    async def get_by_hall(self, hall_id):
        return [self.room] if self.room else []
    async def get_by_id(self, room_id):
        return self.room if self.room and getattr(self.room, 'id', None) == room_id else None
    async def update(self, room_id, data):
        self.updated.append((room_id, data))
    async def allocate_if_space(self, room_id, student_id):
        if not self.room or getattr(self.room, 'id', None) != room_id:
            return None
        if getattr(self.room, 'occupied', 0) >= getattr(self.room, 'capacity', 1):
            return None
        self.room.occupied = getattr(self.room, 'occupied', 0) + 1
        return self.room


class MockAccommodationRepo:
    def __init__(self):
        self.created = []
        self.accommodation = None
    async def create(self, data):
        class A: pass
        a = A(); a.id = 'AC1'
        for k, v in data.items(): setattr(a, k, v)
        self.created.append(data)
        self.accommodation = a
        return a
    async def get_by_student(self, tenant_id, student_id):
        return self.accommodation
    async def update(self, accommodation_id, data):
        if self.accommodation:
            for k, v in data.items(): setattr(self.accommodation, k, v)
        return self.accommodation


class MockMaintenanceRepo:
    def __init__(self):
        self.created = []
    async def create(self, data):
        class M: pass
        m = M(); m.id = 'M1'; m.issue_description = data.get('issue_description'); m.status = 'pending'; self.created.append(data); return m
    async def get_pending_requests(self, tenant_id):
        class M: pass
        m = M(); m.id = 'M1'; m.issue_description = 'Leaky roof'; m.status = 'pending'
        return [m]


@pytest.mark.asyncio
async def test_create_hall_and_room_and_allocate():
    user = MockUser('t1')
    hall_repo = MockHallRepo()
    room_repo = MockRoomRepo()
    accommodation_repo = MockAccommodationRepo()

    hall_req = CreateHallRequest(name='Alpha Hall', capacity=50)
    hall_resp = await create_hall(hall_req, current_user=user, hall_repo=hall_repo)
    assert hall_resp.name == 'Alpha Hall'

    room_req = CreateRoomRequest(hall_id='H1', room_number='101', room_type='single', capacity=1)
    room_resp = await create_room(room_req, current_user=user, room_repo=room_repo)
    assert room_resp.room_number == '101'

    # allocate
    room_repo.room.occupied = 0
    room_repo.room.capacity = 1
    alloc_req = AllocateRoomRequest(student_id='STU1', hall_id='H1', room_id='R1')
    res = await allocate_room(alloc_req, current_user=user, accommodation_repo=accommodation_repo, room_repo=room_repo)
    assert res['status'] == 'allocated'


@pytest.mark.asyncio
async def test_allocate_full_room_raises():
    user = MockUser('t1')
    room = type('R', (), {'id':'R2','occupied':1,'capacity':1,'students':[]})()
    room_repo = MockRoomRepo(room=room)
    accommodation_repo = MockAccommodationRepo()

    alloc_req = AllocateRoomRequest(student_id='STU2', hall_id='H1', room_id='R2')
    with pytest.raises(HTTPException):
        await allocate_room(alloc_req, current_user=user, accommodation_repo=accommodation_repo, room_repo=room_repo)


@pytest.mark.asyncio
async def test_report_and_list_pending_maintenance():
    user = MockUser('t1', id_='u2')
    maintenance_repo = MockMaintenanceRepo()

    maint_req = MaintenanceRequestCreate(hall_id='H1', room_id='R1', issue_description='Broken window')
    res = await report_maintenance(maint_req, current_user=user, maintenance_repo=maintenance_repo)
    assert res['status'] == 'pending'

    # list pending
    pending = await list_pending_maintenance(current_user=user, maintenance_repo=maintenance_repo)
    assert pending[0]['status'] == 'pending'


# Mock repos for student fee & housing selection tests
class MockStudentRepo:
    def __init__(self, student=None):
        self.student = student
        self.updated = []
    async def get_by_user_id(self, tenant_id, user_id):
        return self.student
    async def update(self, student_id, data):
        self.updated.append((student_id, data))
        if self.student:
            for k, v in data.items():
                setattr(self.student, k, v)
        return self.student

class MockPaymentRepo:
    def __init__(self, payments=None):
        self.payments = payments or []
    async def get_by_student(self, tenant_id, student_id):
        return self.payments

from app.presentation.api.v1.accommodation.routes import select_student_housing, get_my_housing_status
from app.presentation.api.v1.accommodation.schemas import HousingSelectionRequest

@pytest.mark.asyncio
async def test_select_housing_unpaid_school_fees_raises():
    user = MockUser('t1', id_='u_student')
    student = type('S', (), {'id': 's1', 'student_id': 'STD100', 'school_fee_paid': False, 'hostel_fee_paid': False, 'fee_balance': 5000.0, 'housing_status': 'unassigned', 'gender': 'male', 'hall_id': None, 'room_id': None})()
    student_repo = MockStudentRepo(student=student)
    payment_repo = MockPaymentRepo([])

    req = HousingSelectionRequest(housing_type='outside_hostel', outside_hostel_name='Unity Hostel', outside_hostel_contact='0200000000')

    with pytest.raises(HTTPException) as exc_info:
        await select_student_housing(
            req, current_user=user, student_repo=student_repo, payment_repo=payment_repo,
            accommodation_repo=MockAccommodationRepo(), hall_repo=MockHallRepo(), room_repo=MockRoomRepo(), audit_repo=None
        )
    assert exc_info.value.status_code == 400
    assert "School fees must be paid" in exc_info.value.detail

@pytest.mark.asyncio
async def test_select_outside_hostel_success_when_school_fees_paid():
    user = MockUser('t1', id_='u_student')
    student = type('S', (), {'id': 's1', 'student_id': 'STD100', 'school_fee_paid': True, 'hostel_fee_paid': False, 'fee_balance': 0.0, 'housing_status': 'unassigned', 'gender': 'male', 'hall_id': None, 'room_id': None})()
    student_repo = MockStudentRepo(student=student)
    payment_repo = MockPaymentRepo([])

    req = HousingSelectionRequest(
        housing_type='outside_hostel',
        outside_hostel_name='Royal Plaza Hostel',
        outside_hostel_address='12 University Way',
        outside_hostel_contact='0244123456'
    )

    res = await select_student_housing(
        req, current_user=user, student_repo=student_repo, payment_repo=payment_repo,
        accommodation_repo=MockAccommodationRepo(), hall_repo=MockHallRepo(), room_repo=MockRoomRepo(), audit_repo=None
    )

    assert res['status'] == 'success'
    assert res['housing_type'] == 'outside_hostel'
    assert student.housing_status == 'outside_hostel'

@pytest.mark.asyncio
async def test_select_private_renting_success_when_school_fees_paid():
    user = MockUser('t1', id_='u_student')
    student = type('S', (), {'id': 's1', 'student_id': 'STD100', 'school_fee_paid': True, 'hostel_fee_paid': False, 'fee_balance': 0.0, 'housing_status': 'unassigned', 'gender': 'female', 'hall_id': None, 'room_id': None})()
    student_repo = MockStudentRepo(student=student)
    payment_repo = MockPaymentRepo([])

    req = HousingSelectionRequest(
        housing_type='private_renting',
        private_address='Block B, Flat 4, Legon Hills',
        private_city='Accra',
        private_contact='0501112233'
    )

    res = await select_student_housing(
        req, current_user=user, student_repo=student_repo, payment_repo=payment_repo,
        accommodation_repo=MockAccommodationRepo(), hall_repo=MockHallRepo(), room_repo=MockRoomRepo(), audit_repo=None
    )

    assert res['status'] == 'success'
    assert res['housing_type'] == 'private_renting'
    assert student.housing_status == 'private_renting'

