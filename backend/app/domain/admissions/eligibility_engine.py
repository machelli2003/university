from typing import Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class EligibilityResult:
    is_eligible: bool
    reason: str
    missing_subjects: List[str] = None
    failed_subjects: List[str] = None
    aggregate_status: Optional[str] = None

class EligibilityEngine:
    """Business logic for checking applicant eligibility"""

    GRADE_SCORES = {
        "A1": 1, "A": 1, "B2": 2, "B3": 3, "C4": 4,
        "C5": 5, "C6": 6, "D7": 7, "D8": 8, "E": 9, "F": 9,
    }

    def __init__(self):
        pass

    async def check_eligibility(
        self,
        applicant_results: dict,
        programme_requirements: dict
    ) -> EligibilityResult:
        required = programme_requirements.get("required_subjects", [])
        missing_subjects = [s for s in required if s not in applicant_results]

        if missing_subjects:
            return EligibilityResult(
                is_eligible=False,
                reason=f"Missing required subjects: {', '.join(missing_subjects)}",
                missing_subjects=missing_subjects
            )

        minimum_grades = programme_requirements.get("minimum_grades", {})
        failed_subjects = []

        for subject, min_grade in minimum_grades.items():
            if subject in applicant_results:
                student_grade = applicant_results[subject]
                if self._compare_grades(student_grade, min_grade) > 0:
                    failed_subjects.append(f"{subject} ({student_grade} < {min_grade})")

        if failed_subjects:
            return EligibilityResult(
                is_eligible=False,
                reason=f"Below minimum grades in: {', '.join(failed_subjects)}",
                failed_subjects=failed_subjects
            )

        aggregate = self._calculate_aggregate(applicant_results, required)
        aggregate_threshold = programme_requirements.get("aggregate_threshold")

        if aggregate_threshold and aggregate > aggregate_threshold:
            return EligibilityResult(
                is_eligible=False,
                reason=f"Aggregate score {aggregate} exceeds threshold {aggregate_threshold}",
                aggregate_status="exceeds_threshold"
            )

        return EligibilityResult(
            is_eligible=True,
            reason="Meets all requirements",
            aggregate_status=f"aggregate_{aggregate}"
        )

    def _compare_grades(self, student_grade: str, minimum_grade: str) -> int:
        student_score = self.GRADE_SCORES.get(student_grade, 9)
        min_score = self.GRADE_SCORES.get(minimum_grade, 9)

        if student_score < min_score:
            return -1
        elif student_score == min_score:
            return 0
        else:
            return 1

    def _calculate_aggregate(self, results: dict, core_subjects: List[str]) -> int:
        aggregate = 0
        for subject, grade in results.items():
            if subject in core_subjects:
                aggregate += self.GRADE_SCORES.get(grade, 9)
        return aggregate

class AlternativeQualificationValidator:
    """Handle non-standard qualifications (diploma, international)"""

    EQUIVALENCE_MAP = {
        "diploma": {"min_grade": "B", "aggregate_adjustment": -2},
        "mature_entry": {"min_age": 23, "work_experience_years": 2},
        "international": {
            "ib": {"min_score": 30},
            "a_levels": {"required_subjects": 3},
            "neco": {"aggregate_threshold": 12},
        }
    }

    async def validate_alternative(
        self,
        qualification_type: str,
        qualification_data: dict
    ) -> Tuple[bool, str]:
        if qualification_type not in self.EQUIVALENCE_MAP:
            return False, "Qualification type not recognized"

        if qualification_type == "mature_entry":
            return self._validate_mature_entry(qualification_data)
        elif qualification_type == "international":
            return self._validate_international(qualification_data)

        return True, "Qualification accepted"

    def _validate_mature_entry(self, data: dict) -> Tuple[bool, str]:
        age = data.get("age")
        work_exp = data.get("work_experience_years", 0)

        if age and age < self.EQUIVALENCE_MAP["mature_entry"]["min_age"]:
            return False, "Must be at least 23 years old"

        if work_exp < self.EQUIVALENCE_MAP["mature_entry"]["work_experience_years"]:
            return False, "Must have at least 2 years work experience"

        return True, "Mature entry validated"

    def _validate_international(self, data: dict) -> Tuple[bool, str]:
        qual_type = data.get("type")

        if qual_type == "ib":
            score = data.get("score")
            min_score = self.EQUIVALENCE_MAP["international"]["ib"]["min_score"]
            if score and score < min_score:
                return False, f"IB score must be at least {min_score}"

        elif qual_type == "a_levels":
            subjects = data.get("subjects", [])
            required = self.EQUIVALENCE_MAP["international"]["a_levels"]["required_subjects"]
            if len(subjects) < required:
                return False, f"Must have at least {required} A-Level subjects"

        return True, f"International qualification ({qual_type}) validated"
