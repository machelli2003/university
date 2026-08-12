from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class RankingCriteria:
    aggregate_weight: float = 0.4
    english_math_weight: float = 0.25
    relevant_subjects_weight: float = 0.2
    bonus_points_weight: float = 0.15

    regional_quota: bool = False
    disability_quota: bool = False
    sports_achievement: bool = False
    stem_bonus: bool = False

class MeritRankingEngine:
    """Calculate merit scores for eligible applicants"""

    AGGREGATE_SCORES = {
        1: 100, 2: 95, 3: 90, 4: 85, 5: 80, 6: 75, 7: 70, 8: 65, 9: 60
    }

    GRADE_SCORES = {
        "A1": 100, "A": 100, "B2": 90, "B3": 80, "C4": 70,
        "C5": 60, "C6": 50, "D7": 40, "D8": 30, "E": 20, "F": 0
    }

    def __init__(self):
        pass

    async def calculate_merit_score(
        self,
        applicant: dict,
        programme_requirements: dict,
        criteria: RankingCriteria = None
    ) -> float:
        if not criteria:
            criteria = RankingCriteria()

        score = 0.0

        aggregate = applicant.get("aggregate", 9)
        aggregate_score = self.AGGREGATE_SCORES.get(aggregate, 60)
        score += (aggregate_score / 100) * criteria.aggregate_weight * 100

        results = applicant.get("results", {})
        english_grade = results.get("english", "F")
        math_grade = results.get("mathematics", "F")

        english_score = self.GRADE_SCORES.get(english_grade, 0)
        math_score = self.GRADE_SCORES.get(math_grade, 0)
        lang_math_score = (english_score + math_score) / 2

        score += (lang_math_score / 100) * criteria.english_math_weight * 100

        relevant_subjects = programme_requirements.get("required_subjects", [])
        relevant_scores = []

        for subject in relevant_subjects:
            if subject in results and subject not in ["english", "mathematics"]:
                grade = results[subject]
                relevant_scores.append(self.GRADE_SCORES.get(grade, 0))

        if relevant_scores:
            avg_relevant = sum(relevant_scores) / len(relevant_scores)
            score += (avg_relevant / 100) * criteria.relevant_subjects_weight * 100

        bonus = 0
        metadata = applicant.get("metadata", {})

        if criteria.regional_quota and metadata.get("is_regional_quota"):
            bonus += 10

        if criteria.disability_quota and metadata.get("is_disability"):
            bonus += 15

        if criteria.sports_achievement and metadata.get("sports_achievement"):
            bonus += 8

        if criteria.stem_bonus and self._is_stem_focused(relevant_subjects, results):
            bonus += 12

        score += (bonus / 100) * criteria.bonus_points_weight * 100

        return round(score, 2)

    def _is_stem_focused(self, subjects: List[str], results: dict) -> bool:
        stem_subjects = ["mathematics", "physics", "chemistry", "biology", "computer_science"]
        taken_stem = [s for s in subjects if s.lower() in stem_subjects]
        return len(taken_stem) >= 3

    async def rank_applicants(
        self,
        eligible_applicants: List[dict],
        programme_requirements: dict,
        criteria: RankingCriteria = None,
        tiebreaker: str = "aggregate"
    ) -> List[Dict[str, Any]]:
        scored_applicants = []
        for applicant in eligible_applicants:
            merit_score = await self.calculate_merit_score(
                applicant, programme_requirements, criteria
            )
            scored_applicants.append({
                "applicant_id": applicant.get("id"),
                "merit_score": merit_score,
                "aggregate": applicant.get("aggregate"),
                "results": applicant.get("results"),
                "application_date": applicant.get("application_date"),
            })

        def sort_key(app):
            primary = -app["merit_score"]

            if tiebreaker == "aggregate":
                secondary = app["aggregate"]
            elif tiebreaker == "english_math":
                english = self.GRADE_SCORES.get(
                    app["results"].get("english", "F"), 0
                )
                math = self.GRADE_SCORES.get(
                    app["results"].get("mathematics", "F"), 0
                )
                secondary = -(english + math)
            else:
                secondary = app["application_date"]

            return (primary, secondary)

        ranked = sorted(scored_applicants, key=sort_key)

        for rank, applicant in enumerate(ranked, 1):
            applicant["merit_rank"] = rank

        return ranked
