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
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssignmentTypeEnum(str, Enum):
    """Type of staff assignment to resource."""
    DEPARTMENT = "department"  # HOD assigned to department
    FACULTY = "faculty"  # Dean assigned to faculty
    PROGRAMME = "programme"  # Programme coordinator assigned
    COURSE = "course"  # Lecturer assigned to course
    HOSTEL = "hostel"  # Hostel admin assigned to hostel
    LIBRARY = "library"  # Librarian assigned to library section
    EXAMINATION = "examination"  # Exam officer assigned to exam period
    FINANCE = "finance"  # Finance officer assigned to cost center


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
            [("tenant_id", 1), ("staff_id", 1)],  # Find all assignments for a staff
            [("tenant_id", 1), ("resource_id", 1)],  # Find all staff for a resource
            [("tenant_id", 1), ("assignment_type", 1), ("is_active", 1)],  # Active assignments by type
            [("tenant_id", 1), ("staff_id", 1), ("is_active", 1)],  # Active assignments for staff
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
