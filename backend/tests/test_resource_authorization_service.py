"""
Unit Tests for Resource Authorization Service
Tests resource-level authorization checks and validations
Section 63: Unit Tests - Authorization
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from beanie import PydanticObjectId

from app.domain.authorization.resource_authorization_service import ResourceAuthorizationService
from app.infrastructure.models.staff_assignment import StaffAssignment


class TestResourceAuthorizationService:
    """Test suite for ResourceAuthorizationService"""

    @pytest.fixture
    def mock_assignment(self):
        """Create a mock StaffAssignment"""
        return StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="DEPARTMENT",
            resource_id="dept_789",
            resource_name="Computer Science",
            staff_role="head_of_department",
            permissions=["view_staff", "edit_course", "submit_grades"],
            is_active=True,
            start_date=datetime.utcnow(),
            end_date=None,
            assigned_by="admin_001",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.mark.asyncio
    async def test_can_access_resource_success(self, mock_assignment):
        """Test successful resource access check"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.check_assignment',
            new_callable=AsyncMock,
            return_value=True
        ):
            result = await ResourceAuthorizationService.can_access_resource(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_can_access_resource_denied(self):
        """Test denied resource access"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.check_assignment',
            new_callable=AsyncMock,
            return_value=False
        ):
            result = await ResourceAuthorizationService.can_access_resource(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_999"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_can_access_resource_with_permission(self):
        """Test resource access with specific permission check"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.check_assignment',
            new_callable=AsyncMock,
            return_value=True
        ) as mock_check:
            result = await ResourceAuthorizationService.can_access_resource(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789",
                required_permission="edit_course"
            )
            assert result is True
            mock_check.assert_called_once_with(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789",
                permission="edit_course"
            )

    @pytest.mark.asyncio
    async def test_can_access_resource_type_success(self, mock_assignment):
        """Test resource type access check success"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_type',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.can_access_resource_type(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_type="DEPARTMENT"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_can_access_resource_type_denied(self):
        """Test resource type access check denied"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_type',
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await ResourceAuthorizationService.can_access_resource_type(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_type="FACULTY"
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_can_access_resource_type_with_permission(self, mock_assignment):
        """Test resource type access with specific permission"""
        mock_assignment.permissions = ["view_staff"]
        
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_type',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.can_access_resource_type(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_type="DEPARTMENT",
                required_permission="view_staff"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_get_accessible_resources(self, mock_assignment):
        """Test retrieving accessible resources"""
        assignment2 = StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="COURSE",
            resource_id="course_001",
            resource_name="Data Structures",
            staff_role="lecturer",
            permissions=["submit_grades"],
            is_active=True,
            start_date=datetime.utcnow(),
            assigned_by="admin_001",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment, assignment2]
        ):
            result = await ResourceAuthorizationService.get_accessible_resources(
                tenant_id="tenant_123",
                staff_id="staff_456"
            )
            
            assert len(result) == 2
            assert "dept_789" in result
            assert "course_001" in result

    @pytest.mark.asyncio
    async def test_get_accessible_resources_filtered_by_type(self, mock_assignment):
        """Test retrieving accessible resources filtered by type"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.get_accessible_resources(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_type="DEPARTMENT"
            )
            
            assert len(result) == 1
            assert result[0] == "dept_789"

    @pytest.mark.asyncio
    async def test_get_accessible_resources_empty(self):
        """Test retrieving accessible resources when none exist"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await ResourceAuthorizationService.get_accessible_resources(
                tenant_id="tenant_123",
                staff_id="staff_999"
            )
            
            assert result == []

    @pytest.mark.asyncio
    async def test_get_accessible_resources_excludes_inactive(self):
        """Test that inactive assignments are excluded"""
        inactive_assignment = StaffAssignment(
            id=PydanticObjectId(),
            tenant_id="tenant_123",
            staff_id="staff_456",
            assignment_type="DEPARTMENT",
            resource_id="dept_inactive",
            resource_name="Inactive Dept",
            staff_role="head_of_department",
            permissions=[],
            is_active=False,
            start_date=datetime.utcnow(),
            assigned_by="admin_001",
            assigned_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[inactive_assignment]
        ):
            result = await ResourceAuthorizationService.get_accessible_resources(
                tenant_id="tenant_123",
                staff_id="staff_456"
            )
            
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_validate_resource_access_authorized(self, mock_assignment):
        """Test resource access validation when authorized"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.validate_resource_access(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789"
            )
            
            assert result["authorized"] is True
            assert result["staff_role"] == "head_of_department"
            assert result["resource_id"] == "dept_789"

    @pytest.mark.asyncio
    async def test_validate_resource_access_unauthorized(self):
        """Test resource access validation when not authorized"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await ResourceAuthorizationService.validate_resource_access(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_unauthorized"
            )
            
            assert result["authorized"] is False
            assert "No assignment" in result["reason"]

    @pytest.mark.asyncio
    async def test_validate_resource_access_missing_permission(self, mock_assignment):
        """Test resource access validation with missing required permission"""
        mock_assignment.permissions = ["view_staff"]
        
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.validate_resource_access(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789",
                required_permission="delete_staff"
            )
            
            assert result["authorized"] is False
            assert "Missing permission" in result["reason"]

    @pytest.mark.asyncio
    async def test_get_staff_permissions(self, mock_assignment):
        """Test retrieving staff permissions"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.get_staff_permissions(
                tenant_id="tenant_123",
                staff_id="staff_456"
            )
            
            assert "dept_789" in result
            assert result["dept_789"]["role"] == "head_of_department"
            assert "view_staff" in result["dept_789"]["permissions"]
            assert result["dept_789"]["resource_type"] == "DEPARTMENT"

    @pytest.mark.asyncio
    async def test_get_staff_permissions_by_resource(self, mock_assignment):
        """Test retrieving staff permissions for specific resource"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[mock_assignment]
        ):
            result = await ResourceAuthorizationService.get_staff_permissions(
                tenant_id="tenant_123",
                staff_id="staff_456",
                resource_id="dept_789"
            )
            
            assert "dept_789" in result
            assert "other_resource" not in result

    @pytest.mark.asyncio
    async def test_get_staff_permissions_no_assignments(self):
        """Test retrieving staff permissions when no assignments exist"""
        with patch(
            'app.infrastructure.repositories.staff_assignment_repository.StaffAssignmentRepository.get_by_staff_id',
            new_callable=AsyncMock,
            return_value=[]
        ):
            result = await ResourceAuthorizationService.get_staff_permissions(
                tenant_id="tenant_123",
                staff_id="staff_999"
            )
            
            assert result == {}
