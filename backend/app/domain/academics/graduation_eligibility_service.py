"""
Graduation Eligibility Service

Determines student eligibility for graduation based on:
- Minimum CGPA
- Minimum credits earned
- Clearance status (financial, library, health)
- Academic standing
"""

from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class GraduationRequirements:
    """Data class for graduation requirements."""
    
    minimum_cgpa: float
    minimum_credits: int
    requires_financial_clearance: bool = True
    requires_library_clearance: bool = True
    requires_health_clearance: bool = True
    requires_hostel_clearance: bool = False
    minimum_passing_gpa: float = 1.0


@dataclass
class GraduationEligibilityResult:
    """Result of graduation eligibility check."""
    
    is_eligible: bool
    total_score: float  # Percentage of requirements met
    cgpa_met: bool
    credits_met: bool
    financial_clearance_met: bool
    library_clearance_met: bool
    health_clearance_met: bool
    hostel_clearance_met: bool
    all_requirements_details: Dict[str, bool]
    issues: List[str]  # List of reasons preventing graduation
    recommendations: List[str]  # Recommendations to achieve eligibility


class GraduationEligibilityService:
    """
    Service for determining student graduation eligibility.
    
    A student is eligible for graduation when they meet ALL of:
    1. Minimum CGPA requirement
    2. Minimum credit hours requirement
    3. All clearance requirements (financial, library, health, etc.)
    4. Passing grades in all required courses
    5. Good academic standing (not suspended)
    """
    
    def __init__(self, requirements: Optional[GraduationRequirements] = None):
        """
        Initialize Graduation Eligibility Service.
        
        Args:
            requirements: GraduationRequirements instance with thresholds.
                         If None, uses default requirements.
        """
        self.requirements = requirements or GraduationRequirements(
            minimum_cgpa=2.0,
            minimum_credits=120,
            requires_financial_clearance=True,
            requires_library_clearance=True,
            requires_health_clearance=True,
            requires_hostel_clearance=False,
            minimum_passing_gpa=1.0
        )
    
    async def check_eligibility(
        self,
        student_data: Dict
    ) -> GraduationEligibilityResult:
        """
        Check if student is eligible for graduation.
        
        Args:
            student_data: Dictionary containing student information:
                - cgpa: float - Cumulative GPA
                - total_credits: int - Total credits earned
                - academic_standing: str - Current academic standing
                - financial_clearance: bool - Has financial clearance
                - library_clearance: bool - Has library clearance
                - health_clearance: bool - Has health clearance
                - hostel_clearance: bool - Has hostel clearance (optional)
                - failed_courses: int - Number of failed courses
                
        Returns:
            GraduationEligibilityResult with detailed eligibility assessment
        """
        
        issues = []
        recommendations = []
        all_requirements = {}
        
        # 1. Check CGPA
        cgpa = float(student_data.get("cgpa", 0.0))
        cgpa_met = cgpa >= self.requirements.minimum_cgpa
        all_requirements["cgpa"] = cgpa_met
        
        if not cgpa_met:
            shortfall = self.requirements.minimum_cgpa - cgpa
            issues.append(
                f"CGPA {cgpa:.2f} is below minimum {self.requirements.minimum_cgpa:.2f} "
                f"(shortfall: {shortfall:.2f})"
            )
            recommendations.append(
                f"Improve CGPA by at least {shortfall:.2f} points through better performance"
            )
        
        # 2. Check Credits
        total_credits = int(student_data.get("total_credits", 0))
        credits_met = total_credits >= self.requirements.minimum_credits
        all_requirements["credits"] = credits_met
        
        if not credits_met:
            shortfall = self.requirements.minimum_credits - total_credits
            issues.append(
                f"Total credits {total_credits} below minimum {self.requirements.minimum_credits} "
                f"(need {shortfall} more)"
            )
            recommendations.append(
                f"Earn {shortfall} more credit hours by completing outstanding courses"
            )
        
        # 3. Check Academic Standing
        academic_standing = student_data.get("academic_standing", "").lower()
        is_suspended = academic_standing == "suspended"
        standing_ok = not is_suspended
        all_requirements["academic_standing"] = standing_ok
        
        if not standing_ok:
            issues.append("Student is currently under academic suspension")
            recommendations.append("Appeal suspension or wait for eligibility review")
        
        # 4. Check Financial Clearance
        financial_clearance = student_data.get("financial_clearance", False)
        financial_ok = (not self.requirements.requires_financial_clearance) or financial_clearance
        all_requirements["financial_clearance"] = financial_ok
        
        if self.requirements.requires_financial_clearance and not financial_ok:
            issues.append("Outstanding financial obligations")
            recommendations.append("Clear all outstanding fees and fines with the Finance Office")
        
        # 5. Check Library Clearance
        library_clearance = student_data.get("library_clearance", False)
        library_ok = (not self.requirements.requires_library_clearance) or library_clearance
        all_requirements["library_clearance"] = library_ok
        
        if self.requirements.requires_library_clearance and not library_ok:
            issues.append("Outstanding library obligations")
            recommendations.append("Return all books and clear any fines with the Library")
        
        # 6. Check Health Clearance
        health_clearance = student_data.get("health_clearance", False)
        health_ok = (not self.requirements.requires_health_clearance) or health_clearance
        all_requirements["health_clearance"] = health_ok
        
        if self.requirements.requires_health_clearance and not health_ok:
            issues.append("Health clearance not obtained")
            recommendations.append("Complete medical examination at Health Center")
        
        # 7. Check Hostel Clearance (if applicable)
        hostel_clearance = student_data.get("hostel_clearance", True)  # Default True if not applicable
        hostel_ok = (not self.requirements.requires_hostel_clearance) or hostel_clearance
        all_requirements["hostel_clearance"] = hostel_ok
        
        if self.requirements.requires_hostel_clearance and not hostel_ok:
            issues.append("Outstanding hostel obligations")
            recommendations.append("Clear all hostel charges and return accommodation keys")
        
        # 8. Check for Failed Courses
        failed_courses = int(student_data.get("failed_courses", 0))
        no_failed_courses = failed_courses == 0
        all_requirements["no_failed_courses"] = no_failed_courses
        
        if not no_failed_courses:
            issues.append(f"Student has {failed_courses} failed course(s)")
            recommendations.append("Retake failed courses or apply for exemption")
        
        # Calculate overall eligibility
        is_eligible = (
            cgpa_met and
            credits_met and
            standing_ok and
            financial_ok and
            library_ok and
            health_ok and
            hostel_ok and
            no_failed_courses
        )
        
        # Calculate score (percentage of requirements met)
        total_requirements = len(all_requirements)
        met_requirements = sum(1 for v in all_requirements.values() if v)
        total_score = (met_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        # Add positive message if eligible
        if is_eligible:
            recommendations.append("✓ Student meets all graduation requirements")
        
        return GraduationEligibilityResult(
            is_eligible=is_eligible,
            total_score=total_score,
            cgpa_met=cgpa_met,
            credits_met=credits_met,
            financial_clearance_met=financial_ok,
            library_clearance_met=library_ok,
            health_clearance_met=health_ok,
            hostel_clearance_met=hostel_ok,
            all_requirements_details=all_requirements,
            issues=issues,
            recommendations=recommendations
        )
    
    async def get_graduation_checklist(
        self,
        student_data: Dict
    ) -> Dict:
        """
        Get graduation checklist for student display.
        
        Args:
            student_data: Student information dictionary
            
        Returns:
            Dictionary with checklist items and status
        """
        result = await self.check_eligibility(student_data)
        
        checklist = {
            "overall_eligible": result.is_eligible,
            "completion_percentage": result.total_score,
            "items": [
                {
                    "name": "Minimum CGPA",
                    "required": f"{self.requirements.minimum_cgpa:.2f}",
                    "current": f"{student_data.get('cgpa', 0.0):.2f}",
                    "completed": result.cgpa_met,
                    "priority": "critical"
                },
                {
                    "name": "Minimum Credit Hours",
                    "required": f"{self.requirements.minimum_credits}",
                    "current": f"{student_data.get('total_credits', 0)}",
                    "completed": result.credits_met,
                    "priority": "critical"
                },
                {
                    "name": "Good Academic Standing",
                    "required": "Not Suspended",
                    "current": student_data.get("academic_standing", "Unknown"),
                    "completed": student_data.get("academic_standing", "").lower() != "suspended",
                    "priority": "critical"
                },
                {
                    "name": "Financial Clearance",
                    "required": "Yes",
                    "current": "Yes" if result.financial_clearance_met else "No",
                    "completed": result.financial_clearance_met,
                    "priority": "high"
                },
                {
                    "name": "Library Clearance",
                    "required": "Yes",
                    "current": "Yes" if result.library_clearance_met else "No",
                    "completed": result.library_clearance_met,
                    "priority": "high"
                },
                {
                    "name": "Health Clearance",
                    "required": "Yes",
                    "current": "Yes" if result.health_clearance_met else "No",
                    "completed": result.health_clearance_met,
                    "priority": "high"
                },
            ],
            "blocking_issues": result.issues,
            "next_steps": result.recommendations
        }
        
        # Add hostel if required
        if self.requirements.requires_hostel_clearance:
            checklist["items"].append({
                "name": "Hostel Clearance",
                "required": "Yes",
                "current": "Yes" if result.hostel_clearance_met else "No",
                "completed": result.hostel_clearance_met,
                "priority": "high"
            })
        
        return checklist
    
    @staticmethod
    def create_from_university_config(grading_config: Dict) -> "GraduationEligibilityService":
        """
        Create service instance from university grading configuration.
        
        Args:
            grading_config: Dictionary from university's graduation configuration
                           with keys: minimum_cgpa, minimum_credits, clearance_requirements
                           
        Returns:
            Configured GraduationEligibilityService instance
        """
        requirements = GraduationRequirements(
            minimum_cgpa=float(grading_config.get("minimum_cgpa", 2.0)),
            minimum_credits=int(grading_config.get("minimum_credits", 120)),
            requires_financial_clearance=grading_config.get("requires_financial_clearance", True),
            requires_library_clearance=grading_config.get("requires_library_clearance", True),
            requires_health_clearance=grading_config.get("requires_health_clearance", True),
            requires_hostel_clearance=grading_config.get("requires_hostel_clearance", False),
        )
        
        return GraduationEligibilityService(requirements)
