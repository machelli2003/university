"""
Setup Completeness Service

Validates and tracks the completion status of university setup wizard sections.
Determines if a university can be submitted for review or activated.
"""

from typing import Dict, Tuple, List
from enum import Enum


class SetupCompleteness(str, Enum):
    """Completion status of a setup section."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class SetupSectionRequirement(str, Enum):
    """Whether a section is mandatory or optional."""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"


# Define which sections are mandatory vs optional
SETUP_SECTION_REQUIREMENTS: Dict[str, SetupSectionRequirement] = {
    # Mandatory sections (must be complete before submission)
    "university_information": SetupSectionRequirement.MANDATORY,
    "id_configuration": SetupSectionRequirement.MANDATORY,
    "academic_years": SetupSectionRequirement.MANDATORY,
    "faculties": SetupSectionRequirement.MANDATORY,
    "departments": SetupSectionRequirement.MANDATORY,
    "programmes": SetupSectionRequirement.MANDATORY,
    "courses": SetupSectionRequirement.MANDATORY,
    "admission_cycle": SetupSectionRequirement.MANDATORY,
    "admission_categories": SetupSectionRequirement.MANDATORY,
    "admission_requirements": SetupSectionRequirement.MANDATORY,
    "application_form": SetupSectionRequirement.MANDATORY,
    "application_fee": SetupSectionRequirement.MANDATORY,
    "staff": SetupSectionRequirement.MANDATORY,
    "role_permission": SetupSectionRequirement.MANDATORY,
    "student_id_configuration": SetupSectionRequirement.MANDATORY,
    "staff_id_configuration": SetupSectionRequirement.MANDATORY,
    "applicant_id_configuration": SetupSectionRequirement.MANDATORY,
    "grading": SetupSectionRequirement.MANDATORY,
    "graduation": SetupSectionRequirement.MANDATORY,
    
    # Optional sections (can be configured later)
    "hostel": SetupSectionRequirement.OPTIONAL,
    "finance": SetupSectionRequirement.OPTIONAL,
    "library": SetupSectionRequirement.OPTIONAL,
    "module_enablement": SetupSectionRequirement.OPTIONAL,
}


class SetupCompletenessService:
    """
    Service to validate and track university setup completeness.
    """

    @staticmethod
    def get_all_sections() -> Dict[str, SetupSectionRequirement]:
        """Get all setup sections and their requirements."""
        return SETUP_SECTION_REQUIREMENTS

    @staticmethod
    def get_mandatory_sections() -> List[str]:
        """Get list of mandatory setup sections."""
        return [
            section for section, requirement in SETUP_SECTION_REQUIREMENTS.items()
            if requirement == SetupSectionRequirement.MANDATORY
        ]

    @staticmethod
    def get_optional_sections() -> List[str]:
        """Get list of optional setup sections."""
        return [
            section for section, requirement in SETUP_SECTION_REQUIREMENTS.items()
            if requirement == SetupSectionRequirement.OPTIONAL
        ]

    @staticmethod
    def is_section_mandatory(section: str) -> bool:
        """Check if a section is mandatory."""
        return SETUP_SECTION_REQUIREMENTS.get(section) == SetupSectionRequirement.MANDATORY

    @staticmethod
    def is_section_optional(section: str) -> bool:
        """Check if a section is optional."""
        return SETUP_SECTION_REQUIREMENTS.get(section) == SetupSectionRequirement.OPTIONAL

    @staticmethod
    def calculate_completeness(setup_sections: Dict[str, bool]) -> Tuple[int, int, float]:
        """
        Calculate setup completeness percentage.
        
        Args:
            setup_sections: Dictionary of section names to completion status
            
        Returns:
            Tuple of (completed_count, total_sections, completion_percentage)
        """
        completed = sum(1 for v in setup_sections.values() if v)
        total = len(setup_sections)
        percentage = (completed / total * 100) if total > 0 else 0
        return completed, total, percentage

    @staticmethod
    def get_mandatory_completeness(setup_sections: Dict[str, bool]) -> Tuple[int, int, float]:
        """
        Calculate mandatory sections completeness percentage.
        
        Args:
            setup_sections: Dictionary of section names to completion status
            
        Returns:
            Tuple of (completed_mandatory_count, total_mandatory_sections, completion_percentage)
        """
        mandatory_sections = SetupCompletenessService.get_mandatory_sections()
        completed = sum(
            1 for section in mandatory_sections 
            if setup_sections.get(section, False)
        )
        total = len(mandatory_sections)
        percentage = (completed / total * 100) if total > 0 else 0
        return completed, total, percentage

    @staticmethod
    @staticmethod
    def normalize_sections(setup_sections: Dict[str, bool]) -> Dict[str, bool]:
        """Ensure every known section is present so validation is deterministic."""
        normalized = {section: False for section in SetupCompletenessService.get_all_sections()}
        if setup_sections:
            normalized.update(setup_sections)
        return normalized

    @staticmethod
    def can_submit_for_review(setup_sections: Dict[str, bool]) -> Tuple[bool, List[str]]:
        """
        Check if all mandatory sections are complete.
        
        Args:
            setup_sections: Dictionary of section names to completion status
            
        Returns:
            Tuple of (can_submit: bool, incomplete_mandatory_sections: List[str])
        """
        normalized_sections = SetupCompletenessService.normalize_sections(setup_sections)
        mandatory_sections = SetupCompletenessService.get_mandatory_sections()
        incomplete = [
            section for section in mandatory_sections
            if not normalized_sections.get(section, False)
        ]
        return len(incomplete) == 0, incomplete

    @staticmethod
    def get_setup_summary(setup_sections: Dict[str, bool]) -> Dict:
        """
        Get a detailed summary of setup completeness.
        
        Args:
            setup_sections: Dictionary of section names to completion status
            
        Returns:
            Dictionary with completion details
        """
        completed_count, total_count, overall_percentage = SetupCompletenessService.calculate_completeness(setup_sections)
        mandatory_completed, mandatory_total, mandatory_percentage = SetupCompletenessService.get_mandatory_completeness(setup_sections)
        can_submit, incomplete_mandatory = SetupCompletenessService.can_submit_for_review(setup_sections)
        
        # Group sections by requirement and status
        mandatory_sections = SetupCompletenessService.get_mandatory_sections()
        optional_sections = SetupCompletenessService.get_optional_sections()
        
        mandatory_complete = [s for s in mandatory_sections if setup_sections.get(s, False)]
        mandatory_incomplete = [s for s in mandatory_sections if not setup_sections.get(s, False)]
        optional_complete = [s for s in optional_sections if setup_sections.get(s, False)]
        optional_incomplete = [s for s in optional_sections if not setup_sections.get(s, False)]
        
        return {
            "overall_completion": {
                "completed": completed_count,
                "total": total_count,
                "percentage": round(overall_percentage, 2),
            },
            "mandatory_completion": {
                "completed": mandatory_completed,
                "total": mandatory_total,
                "percentage": round(mandatory_percentage, 2),
            },
            "can_submit_for_review": can_submit,
            "incomplete_mandatory_sections": incomplete_mandatory,
            "sections": {
                "mandatory": {
                    "complete": mandatory_complete,
                    "incomplete": mandatory_incomplete,
                },
                "optional": {
                    "complete": optional_complete,
                    "incomplete": optional_incomplete,
                },
            },
        }
