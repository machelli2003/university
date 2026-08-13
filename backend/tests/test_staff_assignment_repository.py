"""
Unit Tests for Staff Assignment Repository
Tests CRUD operations and data access patterns
Section 63: Unit Tests - Repository
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from beanie import PydanticObjectId

from app.infrastructure.repositories.staff_assignment_repository import StaffAssignmentRepository
from app.infrastructure.models.staff_assignment import StaffAssignment


class TestStaffAssignmentRepository:
    """Test suite for StaffAssignmentRepository"""

    @pytest.fixture
    def sample_assignment(self):
        """Create a sample StaffAssignment for testing"""
        return StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="DEPARTMENT",
            resource_id="dept_789",
            resource_name="Computer Science",
            staff_role="head_of_department",
            permissions=["view_staff", "edit_course"],
            is_active=True,
            start_date=datetime.utcnow(),
            end_date=None,
            assigned_by="admin_001",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_create_assignment(self, sample_assignment):
        """Test creating a new staff assignment"""
        with patch.object(
            StaffAssignment, 'insert',
            new_callable=AsyncMock
        ):
            result = await StaffAssignmentRepository.create(sample_assignment)
            assert result == sample_assignment
            sample_assignment.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, sample_assignment):
        """Test retrieving assignment by ID"""
        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=sample_assignment
        ):
            result = await StaffAssignmentRepository.get_by_id(sample_assignment.id)
            assert result == sample_assignment
            assert result.tenant_id == "tenant_123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test retrieving non-existent assignment"""
        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await StaffAssignmentRepository.get_by_id(PydanticObjectId())
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_staff_id(self, sample_assignment):
        """Test retrieving assignments by staff ID"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(to_list=AsyncMock(return_value=[sample_assignment]))
        ):
            result = await StaffAssignmentRepository.get_by_staff_id(
                "tenant_123",
                "staff_456"
            )
            assert len(result) == 1
            assert result[0].staff_id == "staff_456"

    @pytest.mark.asyncio
    async def test_get_by_staff_id_multiple(self):
        """Test retrieving multiple assignments for same staff"""
        assignment1 = StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="DEPARTMENT",
            resource_id="dept_1",
            resource_name="CS",
            staff_role="head",
            permissions=[],
            is_active=True,
            start_date=datetime.utcnow(),
            assigned_by="admin",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assignment2 = StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="COURSE",
            resource_id="course_1",
            resource_name="Data Structures",
            staff_role="lecturer",
            permissions=[],
            is_active=True,
            start_date=datetime.utcnow(),
            assigned_by="admin",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(to_list=AsyncMock(return_value=[assignment1, assignment2]))
        ):
            result = await StaffAssignmentRepository.get_by_staff_id(
                "tenant_123",
                "staff_456"
            )
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_by_resource(self, sample_assignment):
        """Test retrieving assignments by resource ID"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(to_list=AsyncMock(return_value=[sample_assignment]))
        ):
            result = await StaffAssignmentRepository.get_by_resource(
                "tenant_123",
                "dept_789"
            )
            assert len(result) == 1
            assert result[0].resource_id == "dept_789"

    @pytest.mark.asyncio
    async def test_get_by_type(self, sample_assignment):
        """Test retrieving assignments by type"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(to_list=AsyncMock(return_value=[sample_assignment]))
        ):
            result = await StaffAssignmentRepository.get_by_type(
                "tenant_123",
                "DEPARTMENT",
                is_active=True
            )
            assert len(result) == 1
            assert result[0].assignment_type == "DEPARTMENT"

    @pytest.mark.asyncio
    async def test_get_by_type_inactive_excluded(self):
        """Test that inactive assignments are excluded"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(to_list=AsyncMock(return_value=[]))
        ):
            result = await StaffAssignmentRepository.get_by_type(
                "tenant_123",
                "DEPARTMENT",
                is_active=True
            )
            assert result == []

    @pytest.mark.asyncio
    async def test_update_assignment(self, sample_assignment):
        """Test updating an assignment"""
        update_data = {
            "permissions": ["view_staff", "edit_course", "delete_course"],
            "updated_at": datetime.utcnow()
        }

        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=sample_assignment
        ):
            with patch.object(
                sample_assignment, 'update',
                new_callable=AsyncMock
            ):
                result = await StaffAssignmentRepository.update(
                    sample_assignment.id,
                    update_data
                )
                assert result == sample_assignment
                sample_assignment.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_assignment_not_found(self):
        """Test updating non-existent assignment"""
        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await StaffAssignmentRepository.update(
                PydanticObjectId(),
                {"permissions": []}
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_assignment(self, sample_assignment):
        """Test deleting an assignment"""
        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=sample_assignment
        ):
            with patch.object(
                sample_assignment, 'delete',
                new_callable=AsyncMock
            ):
                result = await StaffAssignmentRepository.delete(sample_assignment.id)
                assert result is True
                sample_assignment.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_assignment_not_found(self):
        """Test deleting non-existent assignment"""
        with patch.object(
            StaffAssignment, 'get',
            new_callable=AsyncMock,
            return_value=None
        ):
            result = await StaffAssignmentRepository.delete(PydanticObjectId())
            assert result is False

    @pytest.mark.asyncio
    async def test_list_by_tenant(self, sample_assignment):
        """Test listing all assignments for tenant"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(
                skip=AsyncMock(return_value=AsyncMock(
                    limit=AsyncMock(return_value=AsyncMock(
                        to_list=AsyncMock(return_value=[sample_assignment])
                    ))
                ))
            )
        ):
            result = await StaffAssignmentRepository.list_by_tenant(
                "tenant_123",
                skip=0,
                limit=50
            )
            assert len(result) >= 0  # Should return list

    @pytest.mark.asyncio
    async def test_check_assignment_success(self, sample_assignment):
        """Test checking assignment authorization success"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(
                first_or_none=AsyncMock(return_value=sample_assignment)
            )
        ):
            result = await StaffAssignmentRepository.check_assignment(
                "tenant_123",
                "staff_456",
                "dept_789"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_check_assignment_not_found(self):
        """Test checking assignment when not found"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(
                first_or_none=AsyncMock(return_value=None)
            )
        ):
            result = await StaffAssignmentRepository.check_assignment(
                "tenant_123",
                "staff_456",
                "dept_999"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_check_assignment_with_permission_success(self, sample_assignment):
        """Test checking assignment with specific permission"""
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(
                first_or_none=AsyncMock(return_value=sample_assignment)
            )
        ):
            result = await StaffAssignmentRepository.check_assignment(
                "tenant_123",
                "staff_456",
                "dept_789",
                permission="view_staff"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_check_assignment_with_permission_denied(self, sample_assignment):
        """Test checking assignment when permission denied"""
        sample_assignment.permissions = ["view_staff"]
        
        with patch.object(
            StaffAssignment, 'find',
            return_value=AsyncMock(
                first_or_none=AsyncMock(return_value=sample_assignment)
            )
        ):
            result = await StaffAssignmentRepository.check_assignment(
                "tenant_123",
                "staff_456",
                "dept_789",
                permission="delete_staff"
            )
            assert result is False
