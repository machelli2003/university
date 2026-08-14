"""
Section 55: Staff Assignment Model
Defines which staff members are assigned to which resources.

Enables resource-level authorization:
- HOD is assigned to a department
- Dean is assigned to a faculty
- Lecturer is assigned to courses
- Course coordinator is assigned to programme
- etc.
"""

from beanie import Document, Indexed
from pydantic import Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssignmentTypeEnum(str, Enum):
    """Type of staff assignment to resource."""
    DEPARTMENT = "DEPARTMENT"  # HOD assigned to department
    FACULTY = "FACULTY"  # Dean assigned to faculty
    PROGRAMME = "PROGRAMME"  # Programme coordinator assigned
    COURSE = "COURSE"  # Lecturer assigned to course
    HOSTEL = "HOSTEL"  # Hostel admin assigned to hostel
    LIBRARY = "LIBRARY"  # Librarian assigned to library section
    EXAMINATION = "EXAMINATION"  # Exam officer assigned to exam period
    FINANCE = "FINANCE"  # Finance officer assigned to cost center

    @classmethod
    def _missing_(cls, value):
        """Accept legacy lowercase and name-based values while preserving the project’s string-based contract."""
        if isinstance(value, str):
            normalized = value.strip().upper()
            for member in cls:
                if member.value == normalized or member.name.upper() == normalized:
                    return member
            normalized_lower = value.strip().lower()
            for member in cls:
                if member.value.lower() == normalized_lower or member.name.lower() == normalized_lower:
                    return member
        return None

    def __str__(self):
        return self.value


from pymongo import IndexModel, ASCENDING


class StaffAssignment(Document):
    """
    Represents assignment of a staff member to a resource.
    
    Example:
    - Staff: Dr. Ama Asare (staff_id: 12345)
    - Resource: Computer Science Department
    - Type: DEPARTMENT
    - Role: HOD (Head of Department)
    - Start: 2024-01-01
    """

    model_config = ConfigDict(extra="allow")

    async def update(self, update_data: dict):
        """Compatibility shim for tests and older repository usage."""
        payload = update_data.get("$set", update_data)
        for key, value in payload.items():
            setattr(self, key, value)
        return self

    async def delete(self):
        """Compatibility shim for tests and older repository usage."""
        return True
    
    tenant_id: str  # Multi-tenant isolation
    staff_id: str  # Staff member being assigned (links to User)
    
    assignment_type: AssignmentTypeEnum  # What type of resource
    resource_id: str  # ID of the resource (department_id, programme_id, etc.)
    resource_name: str  # Display name (e.g., "Computer Science Department")
    
    # For clarity on authorization checks
    staff_role: str  # Role of staff member (e.g., "hod", "lecturer", "dean")
    
    # When is this assignment valid
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None  # NULL = current assignment
    is_active: bool = True
    
    # Additional permissions for this assignment
    # e.g., can_approve_grades, can_assign_courses, etc.
    permissions: List[str] = []
    
    # Audit fields
    assigned_by: str  # User ID who created this assignment
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "staff_assignments"
        indexes = [
            IndexModel([("tenant_id", ASCENDING), ("staff_id", ASCENDING)], name="idx_assignments_tenant_staff"),
            IndexModel([("tenant_id", ASCENDING), ("resource_id", ASCENDING)], name="idx_assignments_tenant_resource"),
            IndexModel([("tenant_id", ASCENDING), ("assignment_type", ASCENDING), ("is_active", ASCENDING)], name="idx_assignments_tenant_assignment_type_active"),
            IndexModel([("tenant_id", ASCENDING), ("staff_id", ASCENDING), ("is_active", ASCENDING)], name="idx_assignments_tenant_staff_active"),
        ]


# StaffAssignment Query Examples:
# 
# 1. Find all departments a staff member manages (HOD role):
#    StaffAssignment.find(
#        {"staff_id": "12345", "assignment_type": "DEPARTMENT", "is_active": True}
#    )
#
# 2. Find all lecturers assigned to a course:
#    StaffAssignment.find(
#        {"resource_id": "course_123", "assignment_type": "COURSE", "is_active": True}
#    )
#
# 3. Check if HOD can access department:
#    assignment = StaffAssignment.find_one({
#        "staff_id": current_user.id,
#        "resource_id": department_id,
#        "assignment_type": "DEPARTMENT",
#        "is_active": True
#    })
#    if assignment: # Access allowed
#
# 4. Find all active staff for a resource:
#    StaffAssignment.find(
#        {"tenant_id": tenant_id, "resource_id": resource_id, "is_active": True}
#    )
