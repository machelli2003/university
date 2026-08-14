"""
Eligibility Engine
Items 19-31: Check if applicant meets admission requirements

Evaluates:
- WASSCE grades
- Age requirements
- Education history
- Programme prerequisites
- Admission category eligibility
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EligibilityStatus(str, Enum):
    """Eligibility check outcome."""
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class EligibilityCheck:
    """Result of eligibility evaluation."""
    status: EligibilityStatus
    eligible: bool
    score: float  # 0-100 (for ranking)
    reasons: List[str]  # Why eligible/ineligible
    warnings: List[str]  # Things to note
    requires_manual_review: bool = False


class AdmissionRequirement(Enum):
    """Types of admission requirements."""
    WASSCE_GRADE = "wassce_grade"
    MINIMUM_AGE = "minimum_age"
    MAXIMUM_AGE = "maximum_age"
    PREVIOUS_QUALIFICATION = "previous_qualification"
    PROGRAMME_PREREQUISITE = "programme_prerequisite"
    CATEGORY_REQUIREMENT = "category_requirement"
    GPA_REQUIREMENT = "gpa_requirement"
    INTERVIEW = "interview"
    ESSAY = "essay"


class EligibilityEngine:
    """
    Check if applicant meets programme requirements.
    
    Evaluates against:
    - Admission requirements (per programme)
    - Academic qualifications
    - Entry requirements
    - Category/quota eligibility
    """
    
    async def check_eligibility(
        self,
        applicant_data: Dict[str, Any],
        programme_requirements: Dict[str, Any],
        admission_category: Optional[str] = None,
    ) -> EligibilityCheck:
        """
        Comprehensive eligibility evaluation.
        
        Args:
            applicant_data: Applicant's submitted data (WASSCE, personal info, etc.)
            programme_requirements: Requirements for the programme
            admission_category: e.g., "domestic", "international", "mature_student"
        
        Returns:
            EligibilityCheck with status and reasons
        """
        reasons = []
        warnings = []
        score = 100.0
        
        # 1. Check WASSCE grades
        wassce_check, wassce_score = self._check_wassce_requirements(
            applicant_data,
            programme_requirements.get("wassce_requirements", {}),
        )
        reasons.extend(wassce_check)
        score = min(score, wassce_score)
        
        # 2. Check age
        age_check, age_ok = self._check_age_requirements(
            applicant_data,
            programme_requirements.get("age_requirements", {}),
        )
        reasons.extend(age_check)
        if not age_ok:
            score -= 20
        
        # 3. Check entry qualifications
        qual_check, qual_ok = self._check_qualifications(
            applicant_data,
            programme_requirements.get("qualifications_required", []),
        )
        reasons.extend(qual_check)
        if not qual_ok:
            score -= 30
        
        # 4. Check programme prerequisites
        prereq_check, prereq_ok = self._check_prerequisites(
            applicant_data,
            programme_requirements.get("prerequisites", []),
        )
        reasons.extend(prereq_check)
        if not prereq_ok:
            score -= 25
        
        # 5. Check category eligibility
        category_check, category_ok = self._check_category(
            applicant_data,
            admission_category,
            programme_requirements.get("category_requirements", {}),
        )
        reasons.extend(category_check)
        if not category_ok:
            warnings.append("Category eligibility requires manual review")
        
        # Determine final status
        if score >= 85:
            status = EligibilityStatus.ELIGIBLE
        elif score >= 60:
            status = EligibilityStatus.CONDITIONALLY_ELIGIBLE
            warnings.append("Applicant meets minimum requirements but should be reviewed")
        else:
            status = EligibilityStatus.INELIGIBLE
        
        # Flag for manual review if needed
        requires_manual_review = (
            not wassce_check[-1] or  # WASSCE unverified
            not category_ok or  # Category needs review
            programme_requirements.get("requires_interview", False)
        )
        
        return EligibilityCheck(
            status=status,
            eligible=status in [EligibilityStatus.ELIGIBLE, EligibilityStatus.CONDITIONALLY_ELIGIBLE],
            score=max(0, score),
            reasons=reasons,
            warnings=warnings,
            requires_manual_review=requires_manual_review,
        )
    
    def _check_wassce_requirements(
        self,
        applicant_data: Dict[str, Any],
        wassce_requirements: Dict[str, Any],
    ) -> Tuple[List[str], float]:
        """
        Check WASSCE results against requirements.
        
        Returns: (reasons, score_0_to_100)
        """
        reasons = []
        score = 100.0
        
        wassce_data = applicant_data.get("wassce_data", {})
        if not wassce_data:
            return ["❌ No WASSCE data submitted"], 0.0
        
        # Check verification status
        verification = wassce_data.get("verification_status", "pending")
        if verification != "verified":
            reasons.append(f"⚠️ WASSCE status: {verification} (requires verification)")
            score -= 20
        else:
            reasons.append("✓ WASSCE verified")
        
        # Check required subjects
        subjects = wassce_data.get("subjects", {})
        required_subjects = wassce_requirements.get("required_subjects", {})
        
        for subject, required_grade in required_subjects.items():
            if subject not in subjects:
                reasons.append(f"❌ Required subject '{subject}' not taken")
                score -= 15
            else:
                actual_grade = subjects[subject]
                if self._grade_meets_requirement(actual_grade, required_grade):
                    reasons.append(f"✓ {subject}: {actual_grade} (requires {required_grade})")
                else:
                    reasons.append(f"❌ {subject}: {actual_grade} (requires minimum {required_grade})")
                    score -= 20
        
        # Bonus: aggregate score
        if all(self._grade_is_strong(g) for g in subjects.values()):
            reasons.append("✓ Strong overall grades")
            score = min(100, score + 10)
        
        return reasons, score
    
    def _check_age_requirements(
        self,
        applicant_data: Dict[str, Any],
        age_requirements: Dict[str, Any],
    ) -> Tuple[List[str], bool]:
        """Check if applicant age meets requirements."""
        reasons = []
        
        from datetime import datetime
        dob = applicant_data.get("date_of_birth")
        if not dob:
            return ["⚠️ Date of birth not provided"], True  # Assume OK for now
        
        # Calculate age
        try:
            birth_date = datetime.fromisoformat(dob)
            age = (datetime.now() - birth_date).days // 365
        except:
            return ["⚠️ Invalid date of birth"], True
        
        min_age = age_requirements.get("minimum", 16)
        max_age = age_requirements.get("maximum", 999)
        
        if age < min_age:
            reasons.append(f"❌ Age {age} below minimum {min_age}")
            return reasons, False
        
        if age > max_age:
            reasons.append(f"⚠️ Age {age} above preferred maximum {max_age} (mature student)")
            return reasons, True  # May require special category
        
        reasons.append(f"✓ Age {age} meets requirements")
        return reasons, True
    
    def _check_qualifications(
        self,
        applicant_data: Dict[str, Any],
        qualifications_required: List[str],
    ) -> Tuple[List[str], bool]:
        """Check if applicant has required prior qualifications."""
        reasons = []
        applicant_quals = applicant_data.get("qualifications", [])
        
        for qual in qualifications_required:
            if qual in applicant_quals:
                reasons.append(f"✓ Has {qual}")
            else:
                reasons.append(f"❌ Missing {qual}")
                return reasons, False
        
        return reasons, True
    
    def _check_prerequisites(
        self,
        applicant_data: Dict[str, Any],
        prerequisites: List[Dict[str, str]],
    ) -> Tuple[List[str], bool]:
        """Check WASSCE subject prerequisites."""
        reasons = []
        subjects = applicant_data.get("wassce_data", {}).get("subjects", {})
        
        for prereq in prerequisites:
            subject = prereq.get("subject")
            min_grade = prereq.get("minimum_grade")
            
            if subject not in subjects:
                reasons.append(f"❌ Prerequisite {subject} not taken")
                return reasons, False
            
            if not self._grade_meets_requirement(subjects[subject], min_grade):
                reasons.append(f"❌ {subject} grade below prerequisite {min_grade}")
                return reasons, False
            
            reasons.append(f"✓ Prerequisite {subject} ({min_grade}) met")
        
        return reasons, True
    
    def _check_category(
        self,
        applicant_data: Dict[str, Any],
        admission_category: Optional[str],
        category_requirements: Dict[str, Any],
    ) -> Tuple[List[str], bool]:
        """Check category-specific requirements."""
        reasons = []
        
        if not admission_category:
            reasons.append("⚠️ No admission category specified")
            return reasons, True  # Category optional
        
        if admission_category == "international":
            # International students may have different requirements
            reasons.append("ℹ️ International student category")
        
        elif admission_category == "mature_student":
            # Mature students (older applicants)
            reasons.append("ℹ️ Mature student category")
        
        elif admission_category == "special_entry":
            # Special entry (e.g., sports, arts talent)
            reasons.append("ℹ️ Special entry category (requires manual review)")
            return reasons, False  # Requires review
        
        else:
            reasons.append(f"✓ {admission_category} category")
        
        return reasons, True
    
    @staticmethod
    def _grade_meets_requirement(actual_grade: str, required_grade: str) -> bool:
        """
        Check if actual grade meets requirement.
        
        Grade hierarchy: A1 > A2 > B2 > B3 > C4 > C5 > D7 > E8 > F9
        """
        grade_order = {
            "A1": 9, "A2": 8,
            "B2": 7, "B3": 6,
            "C4": 5, "C5": 4,
            "D7": 3, "E8": 2, "F9": 1,
        }
        
        actual_score = grade_order.get(actual_grade, 0)
        required_score = grade_order.get(required_grade, 0)
        
        return actual_score >= required_score
    
    @staticmethod
    def _grade_is_strong(grade: str) -> bool:
        """Check if grade is strong (A1, A2, B2)."""
        return grade in ["A1", "A2", "B2"]


class EligibilityRepository:
    """Store and retrieve eligibility checks."""
    
    async def save_check(
        self,
        applicant_id: str,
        programme_id: str,
        check: EligibilityCheck,
    ) -> Dict[str, Any]:
        """Save eligibility check result."""
        from datetime import datetime
        
        record = {
            "applicant_id": applicant_id,
            "programme_id": programme_id,
            "status": check.status.value,
            "eligible": check.eligible,
            "score": check.score,
            "reasons": check.reasons,
            "warnings": check.warnings,
            "requires_manual_review": check.requires_manual_review,
            "checked_at": datetime.utcnow(),
        }
        
        # TODO: Save to MongoDB EligibilityCheck collection
        logger.info(f"✅ Eligibility check saved for {applicant_id} → {programme_id}")
        return record
