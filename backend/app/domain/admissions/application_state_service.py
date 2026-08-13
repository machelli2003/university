"""
Section 39: Application State Transition Service

Manages valid state transitions in the 20-state application lifecycle.
Prevents invalid state changes and logs all transitions for audit trail.
"""

from typing import List, Dict, Tuple
from app.infrastructure.models.applicant import ApplicationStatusEnum


class ApplicationStateTransitionService:
    """
    Enforces valid state transitions in application workflow.
    Prevents moving applicants to invalid states based on current state.
    """

    # Valid state transitions: current_state -> [list of allowed next states]
    VALID_TRANSITIONS: Dict[ApplicationStatusEnum, List[ApplicationStatusEnum]] = {
        # Initial Phase
        ApplicationStatusEnum.DRAFT: [
            ApplicationStatusEnum.SUBMITTED,
        ],
        ApplicationStatusEnum.SUBMITTED: [
            ApplicationStatusEnum.PAYMENT_PENDING,
        ],
        # Payment & Document Phase
        ApplicationStatusEnum.PAYMENT_PENDING: [
            ApplicationStatusEnum.PAYMENT_VERIFIED,
        ],
        ApplicationStatusEnum.PAYMENT_VERIFIED: [
            ApplicationStatusEnum.DOCUMENT_REVIEW,
        ],
        ApplicationStatusEnum.DOCUMENT_REVIEW: [
            ApplicationStatusEnum.ELIGIBILITY_CHECK,
        ],
        # Eligibility & Review Phase
        ApplicationStatusEnum.ELIGIBILITY_CHECK: [
            ApplicationStatusEnum.ELIGIBLE,
            ApplicationStatusEnum.INELIGIBLE,
        ],
        ApplicationStatusEnum.ELIGIBLE: [
            ApplicationStatusEnum.UNDER_REVIEW,
        ],
        ApplicationStatusEnum.INELIGIBLE: [
            ApplicationStatusEnum.REJECTED,
        ],
        ApplicationStatusEnum.UNDER_REVIEW: [
            ApplicationStatusEnum.DEPARTMENT_REVIEW,
        ],
        ApplicationStatusEnum.DEPARTMENT_REVIEW: [
            ApplicationStatusEnum.FACULTY_REVIEW,
        ],
        ApplicationStatusEnum.FACULTY_REVIEW: [
            ApplicationStatusEnum.COMMITTEE_REVIEW,
        ],
        ApplicationStatusEnum.COMMITTEE_REVIEW: [
            ApplicationStatusEnum.OFFERED,
            ApplicationStatusEnum.CONDITIONALLY_ADMITTED,
            ApplicationStatusEnum.RANKED,
            ApplicationStatusEnum.REJECTED,
            ApplicationStatusEnum.MANUAL_REVIEW,
        ],
        ApplicationStatusEnum.MANUAL_REVIEW: [
            ApplicationStatusEnum.COMMITTEE_REVIEW,
            ApplicationStatusEnum.OFFERED,
            ApplicationStatusEnum.REJECTED,
        ],
        # Decision Phase (After Ranking)
        ApplicationStatusEnum.RANKED: [
            ApplicationStatusEnum.ALLOCATED,
            ApplicationStatusEnum.WAITLISTED,
        ],
        ApplicationStatusEnum.ALLOCATED: [
            ApplicationStatusEnum.ENROLLMENT_PENDING,
        ],
        # Offer Acceptance
        ApplicationStatusEnum.OFFERED: [
            ApplicationStatusEnum.ENROLLMENT_PENDING,
        ],
        ApplicationStatusEnum.CONDITIONALLY_ADMITTED: [
            ApplicationStatusEnum.ENROLLMENT_PENDING,
        ],
        # Terminal States (No Further Transitions)
        ApplicationStatusEnum.REJECTED: [],
        ApplicationStatusEnum.WAITLISTED: [],
        ApplicationStatusEnum.ENROLLMENT_PENDING: [
            ApplicationStatusEnum.ENROLLED,
        ],
        ApplicationStatusEnum.ENROLLED: [],
    }

    @staticmethod
    def is_valid_transition(
        current_state: ApplicationStatusEnum,
        next_state: ApplicationStatusEnum,
    ) -> bool:
        """
        Check if transition from current_state to next_state is allowed.
        
        Args:
            current_state: Current application status
            next_state: Desired next status
            
        Returns:
            True if transition is valid, False otherwise
        """
        return next_state in ApplicationStateTransitionService.VALID_TRANSITIONS.get(
            current_state, []
        )

    @staticmethod
    def get_allowed_transitions(
        current_state: ApplicationStatusEnum,
    ) -> List[ApplicationStatusEnum]:
        """
        Get list of all valid next states from current state.
        
        Args:
            current_state: Current application status
            
        Returns:
            List of allowed next states
        """
        return ApplicationStateTransitionService.VALID_TRANSITIONS.get(current_state, [])

    @staticmethod
    def validate_transition(
        current_state: ApplicationStatusEnum,
        next_state: ApplicationStatusEnum,
    ) -> Tuple[bool, str]:
        """
        Validate transition and return result with explanation.
        
        Args:
            current_state: Current application status
            next_state: Desired next status
            
        Returns:
            Tuple of (is_valid, message)
        """
        if current_state == next_state:
            return False, f"Application is already in {current_state} state"

        if not ApplicationStateTransitionService.is_valid_transition(current_state, next_state):
            allowed = ApplicationStateTransitionService.get_allowed_transitions(current_state)
            if not allowed:
                return (
                    False,
                    f"Application in {current_state} state has reached a terminal state",
                )
            allowed_str = ", ".join([s.value for s in allowed])
            return (
                False,
                f"Cannot transition from {current_state} to {next_state}. "
                f"Allowed transitions: {allowed_str}",
            )

        return True, f"Valid transition from {current_state} to {next_state}"

    @staticmethod
    def get_state_display_name(state: ApplicationStatusEnum) -> str:
        """
        Get human-readable name for application state.
        
        Args:
            state: Application status
            
        Returns:
            Formatted state name (e.g., "payment_pending" -> "Payment Pending")
        """
        display_map = {
            ApplicationStatusEnum.DRAFT: "Draft",
            ApplicationStatusEnum.SUBMITTED: "Submitted",
            ApplicationStatusEnum.PAYMENT_PENDING: "Payment Pending",
            ApplicationStatusEnum.PAYMENT_VERIFIED: "Payment Verified",
            ApplicationStatusEnum.DOCUMENT_REVIEW: "Document Review",
            ApplicationStatusEnum.ELIGIBILITY_CHECK: "Eligibility Check",
            ApplicationStatusEnum.ELIGIBLE: "Eligible",
            ApplicationStatusEnum.INELIGIBLE: "Ineligible",
            ApplicationStatusEnum.UNDER_REVIEW: "Under Review",
            ApplicationStatusEnum.DEPARTMENT_REVIEW: "Department Review",
            ApplicationStatusEnum.FACULTY_REVIEW: "Faculty Review",
            ApplicationStatusEnum.COMMITTEE_REVIEW: "Committee Review",
            ApplicationStatusEnum.MANUAL_REVIEW: "Manual Review",
            ApplicationStatusEnum.RANKED: "Ranked",
            ApplicationStatusEnum.ALLOCATED: "Allocated",
            ApplicationStatusEnum.OFFERED: "Offered",
            ApplicationStatusEnum.CONDITIONALLY_ADMITTED: "Conditionally Admitted",
            ApplicationStatusEnum.WAITLISTED: "Waitlisted",
            ApplicationStatusEnum.REJECTED: "Rejected",
            ApplicationStatusEnum.ENROLLMENT_PENDING: "Enrollment Pending",
            ApplicationStatusEnum.ENROLLED: "Enrolled",
        }
        return display_map.get(state, state.value)

    @staticmethod
    def get_state_description(state: ApplicationStatusEnum) -> str:
        """
        Get description of what each state means.
        
        Args:
            state: Application status
            
        Returns:
            Description of state
        """
        descriptions = {
            ApplicationStatusEnum.DRAFT: "Application started but not yet submitted",
            ApplicationStatusEnum.SUBMITTED: "Application submitted by applicant",
            ApplicationStatusEnum.PAYMENT_PENDING: "Awaiting application fee payment",
            ApplicationStatusEnum.PAYMENT_VERIFIED: "Payment confirmed, processing application",
            ApplicationStatusEnum.DOCUMENT_REVIEW: "Supporting documents under review",
            ApplicationStatusEnum.ELIGIBILITY_CHECK: "Verifying eligibility requirements",
            ApplicationStatusEnum.ELIGIBLE: "Meets all eligibility requirements",
            ApplicationStatusEnum.INELIGIBLE: "Does not meet eligibility requirements",
            ApplicationStatusEnum.UNDER_REVIEW: "Application in review queue",
            ApplicationStatusEnum.DEPARTMENT_REVIEW: "Department evaluating application",
            ApplicationStatusEnum.FACULTY_REVIEW: "Faculty head reviewing application",
            ApplicationStatusEnum.COMMITTEE_REVIEW: "Admissions committee reviewing",
            ApplicationStatusEnum.MANUAL_REVIEW: "Special cases requiring manual review",
            ApplicationStatusEnum.RANKED: "Placed in merit ranking pool",
            ApplicationStatusEnum.ALLOCATED: "Offered position from ranking",
            ApplicationStatusEnum.OFFERED: "Admission offer extended",
            ApplicationStatusEnum.CONDITIONALLY_ADMITTED: "Admitted with conditions to fulfill",
            ApplicationStatusEnum.WAITLISTED: "Placed on waitlist for future consideration",
            ApplicationStatusEnum.REJECTED: "Application rejected",
            ApplicationStatusEnum.ENROLLMENT_PENDING: "Offer accepted, awaiting enrollment",
            ApplicationStatusEnum.ENROLLED: "Successfully enrolled and registered",
        }
        return descriptions.get(state, "Unknown state")
