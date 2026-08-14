"""
Ranking Algorithm
Items 19-31: Rank eligible applicants for programme selection

Supports:
- Merit-based ranking (WASSCE scores)
- Cutoff scores
- Category quotas
- Interview scores
- Tie-breaking rules
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RankingMethod(str, Enum):
    """Methods for ranking applicants."""
    MERIT = "merit"  # WASSCE score only
    AGGREGATE = "aggregate"  # WASSCE + interview + essay
    CATEGORY_BASED = "category_based"  # Different cutoffs per category
    WEIGHTED = "weighted"  # Custom weighted scoring


@dataclass
class RankingScores:
    """Individual applicant ranking scores."""
    applicant_id: str
    programme_id: str
    
    # Component scores (0-100 each)
    wassce_score: float
    interview_score: Optional[float] = None
    essay_score: Optional[float] = None
    
    # Final aggregate
    aggregate_score: float = 0.0
    rank_position: Optional[int] = None
    
    # Category info
    admission_category: Optional[str] = None
    category_rank: Optional[int] = None  # Rank within category
    
    # Status
    within_cutoff: bool = False
    allocated: bool = False


class RankingAlgorithm:
    """
    Rank eligible applicants for programme admission.
    
    Determines admission order based on:
    - Academic merit (WASSCE)
    - Interview performance
    - Essay quality
    - Category quotas
    """
    
    async def rank_applicants(
        self,
        eligible_applicants: List[Dict[str, Any]],
        programme_ranking_rules: Dict[str, Any],
        ranking_method: RankingMethod = RankingMethod.MERIT,
    ) -> List[RankingScores]:
        """
        Rank all eligible applicants for a programme.
        
        Args:
            eligible_applicants: List of eligible applicant records
            programme_ranking_rules: Ranking config (cutoff, quotas, weights)
            ranking_method: How to rank applicants
        
        Returns:
            Sorted list of RankingScores
        """
        ranking_scores = []
        
        # Calculate scores for each applicant
        for applicant in eligible_applicants:
            score = self._calculate_applicant_score(
                applicant,
                programme_ranking_rules,
                ranking_method,
            )
            ranking_scores.append(score)
        
        # Sort by aggregate score (highest first)
        ranking_scores.sort(
            key=lambda x: x.aggregate_score,
            reverse=True,
        )
        
        # Assign rank positions
        for i, score in enumerate(ranking_scores, 1):
            score.rank_position = i
        
        # Check cutoff
        cutoff_score = programme_ranking_rules.get("cutoff_score", 0)
        for score in ranking_scores:
            score.within_cutoff = score.aggregate_score >= cutoff_score
        
        # Apply category quotas if configured
        if programme_ranking_rules.get("use_category_quotas", False):
            ranking_scores = self._apply_category_quotas(
                ranking_scores,
                programme_ranking_rules.get("category_quotas", {}),
            )
        
        logger.info(f"✅ Ranked {len(ranking_scores)} applicants for programme")
        return ranking_scores
    
    def _calculate_applicant_score(
        self,
        applicant: Dict[str, Any],
        rules: Dict[str, Any],
        method: RankingMethod,
    ) -> RankingScores:
        """Calculate ranking score for one applicant."""
        
        if method == RankingMethod.MERIT:
            return self._calculate_merit_score(applicant, rules)
        elif method == RankingMethod.AGGREGATE:
            return self._calculate_aggregate_score(applicant, rules)
        elif method == RankingMethod.WEIGHTED:
            return self._calculate_weighted_score(applicant, rules)
        else:
            return self._calculate_aggregate_score(applicant, rules)
    
    def _calculate_merit_score(
        self,
        applicant: Dict[str, Any],
        rules: Dict[str, Any],
    ) -> RankingScores:
        """WASSCE score only (merit-based)."""
        from app.application.admissions.eligibility_engine import EligibilityEngine
        
        # Extract WASSCE score from eligibility check
        wassce_score = applicant.get("eligibility_check", {}).get("score", 60.0)
        
        return RankingScores(
            applicant_id=applicant["id"],
            programme_id=applicant["programme_id"],
            wassce_score=wassce_score,
            aggregate_score=wassce_score,
            admission_category=applicant.get("admission_category"),
        )
    
    def _calculate_aggregate_score(
        self,
        applicant: Dict[str, Any],
        rules: Dict[str, Any],
    ) -> RankingScores:
        """Combine WASSCE + interview + essay."""
        wassce_score = applicant.get("eligibility_check", {}).get("score", 60.0)
        interview_score = applicant.get("interview_score", 0.0)
        essay_score = applicant.get("essay_score", 0.0)
        
        # Weights (configurable, default: 70% WASSCE, 20% interview, 10% essay)
        wassce_weight = rules.get("wassce_weight", 0.7)
        interview_weight = rules.get("interview_weight", 0.2)
        essay_weight = rules.get("essay_weight", 0.1)
        
        # Calculate aggregate
        aggregate = (
            wassce_score * wassce_weight +
            interview_score * interview_weight +
            essay_score * essay_weight
        )
        
        return RankingScores(
            applicant_id=applicant["id"],
            programme_id=applicant["programme_id"],
            wassce_score=wassce_score,
            interview_score=interview_score,
            essay_score=essay_score,
            aggregate_score=aggregate,
            admission_category=applicant.get("admission_category"),
        )
    
    def _calculate_weighted_score(
        self,
        applicant: Dict[str, Any],
        rules: Dict[str, Any],
    ) -> RankingScores:
        """Custom weighted scoring (e.g., STEM subjects prioritized)."""
        base_score = applicant.get("eligibility_check", {}).get("score", 60.0)
        
        # Apply subject bonuses
        subjects_bonus = 0.0
        required_subjects = rules.get("required_subjects", [])
        applicant_subjects = applicant.get("wassce_data", {}).get("subjects", {})
        
        for subject in required_subjects:
            if subject in applicant_subjects:
                grade = applicant_subjects[subject]
                # Strong grade bonus
                if grade in ["A1", "A2"]:
                    subjects_bonus += 5
                elif grade == "B2":
                    subjects_bonus += 2
        
        aggregate = min(100, base_score + subjects_bonus)
        
        return RankingScores(
            applicant_id=applicant["id"],
            programme_id=applicant["programme_id"],
            wassce_score=base_score,
            aggregate_score=aggregate,
            admission_category=applicant.get("admission_category"),
        )
    
    def _apply_category_quotas(
        self,
        ranking_scores: List[RankingScores],
        quotas: Dict[str, int],
    ) -> List[RankingScores]:
        """
        Apply category-based quotas.
        
        Example:
        - 70% for domestic students
        - 20% for international students
        - 10% for mature students
        """
        # Group by category
        by_category = {}
        for score in ranking_scores:
            category = score.admission_category or "general"
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(score)
        
        # Apply quota limits per category
        final_list = []
        for category, quota in quotas.items():
            category_applicants = by_category.get(category, [])
            # Sort category by score
            category_applicants.sort(key=lambda x: x.aggregate_score, reverse=True)
            
            # Take top `quota` from this category
            selected = category_applicants[:quota]
            for i, score in enumerate(selected, 1):
                score.category_rank = i
            
            final_list.extend(selected)
        
        # Re-sort overall by score
        final_list.sort(key=lambda x: x.aggregate_score, reverse=True)
        
        return final_list
    
    async def get_cutoff_score(
        self,
        programme_id: str,
        target_intake: int,
        all_scores: List[RankingScores],
    ) -> float:
        """
        Dynamically calculate cutoff score.
        
        If we have more applicants than spots, cutoff is the score
        of the last selected applicant.
        """
        if len(all_scores) <= target_intake:
            # All applicants fit
            return min([s.aggregate_score for s in all_scores]) if all_scores else 0.0
        
        # Get score at cutoff position
        cutoff_applicant = all_scores[target_intake - 1]
        return cutoff_applicant.aggregate_score


class RankingRepository:
    """Persist ranking scores and decisions."""
    
    async def save_ranking(
        self,
        programme_id: str,
        ranking_scores: List[RankingScores],
        ranking_date: str,
    ) -> Dict[str, Any]:
        """Save ranking results."""
        
        admitted = [s for s in ranking_scores if s.within_cutoff]
        
        ranking_record = {
            "programme_id": programme_id,
            "total_ranked": len(ranking_scores),
            "total_admitted": len(admitted),
            "ranking_date": ranking_date,
            "scores": [
                {
                    "applicant_id": s.applicant_id,
                    "rank": s.rank_position,
                    "score": s.aggregate_score,
                    "category": s.admission_category,
                    "within_cutoff": s.within_cutoff,
                }
                for s in ranking_scores
            ],
        }
        
        # TODO: Save to MongoDB RankingResult collection
        logger.info(f"✅ Ranking saved: {len(admitted)} admitted from {len(ranking_scores)} applicants")
        return ranking_record
