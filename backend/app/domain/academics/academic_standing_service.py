"""
Academic Standing Service

Calculates and manages student academic standing based on GPA/CGPA.
Implements multi-tier standing rules for probation and suspension.
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class AcademicStandingEnum(str, Enum):
    """Academic standing classifications based on GPA thresholds."""
    
    EXCELLENT = "excellent"      # GPA >= 3.5
    GOOD = "good"                # 3.0 <= GPA < 3.5
    SATISFACTORY = "satisfactory"  # 2.5 <= GPA < 3.0
    WARNING = "warning"           # 2.0 <= GPA < 2.5
    PROBATION = "probation"       # 1.5 <= GPA < 2.0
    AT_RISK = "at_risk"           # 1.0 <= GPA < 1.5
    SUSPENDED = "suspended"       # GPA < 1.0


class AcademicStandingConfig:
    """Configuration for academic standing thresholds."""
    
    # Default thresholds (universities can override via grading configuration)
    EXCELLENT_THRESHOLD = 3.5
    GOOD_THRESHOLD = 3.0
    SATISFACTORY_THRESHOLD = 2.5
    WARNING_THRESHOLD = 2.0
    PROBATION_THRESHOLD = 1.5
    AT_RISK_THRESHOLD = 1.0
    SUSPENDED_THRESHOLD = 0.0
    
    # Probation rules
    PROBATION_GPAPOINT_THRESHOLD = 1.5
    SUSPENSION_GPA_THRESHOLD = 1.0
    CONSECUTIVE_PROBATION_LIMIT = 2  # Consecutive semesters before suspension


class AcademicStandingService:
    """
    Service for calculating and managing academic standing.
    
    Academic Standing Classification:
    - EXCELLENT: GPA >= 3.5 (Dean's List candidate)
    - GOOD: 3.0 <= GPA < 3.5 (Meets standard expectations)
    - SATISFACTORY: 2.5 <= GPA < 3.0 (Acceptable performance)
    - WARNING: 2.0 <= GPA < 2.5 (Below satisfactory; needs improvement)
    - PROBATION: 1.5 <= GPA < 2.0 (At risk; on probation)
    - AT_RISK: 1.0 <= GPA < 1.5 (Severe academic difficulty)
    - SUSPENDED: GPA < 1.0 (Academic suspension)
    """
    
    def __init__(self, custom_config: Optional[Dict] = None):
        """
        Initialize Academic Standing Service.
        
        Args:
            custom_config: Optional dictionary with custom thresholds.
                          Keys: excellent_threshold, good_threshold, etc.
        """
        self.config = AcademicStandingConfig()
        
        # Override defaults with custom configuration if provided
        if custom_config:
            if "excellent_threshold" in custom_config:
                self.config.EXCELLENT_THRESHOLD = custom_config["excellent_threshold"]
            if "good_threshold" in custom_config:
                self.config.GOOD_THRESHOLD = custom_config["good_threshold"]
            if "satisfactory_threshold" in custom_config:
                self.config.SATISFACTORY_THRESHOLD = custom_config["satisfactory_threshold"]
            if "warning_threshold" in custom_config:
                self.config.WARNING_THRESHOLD = custom_config["warning_threshold"]
            if "probation_threshold" in custom_config:
                self.config.PROBATION_THRESHOLD = custom_config["probation_threshold"]
            if "at_risk_threshold" in custom_config:
                self.config.AT_RISK_THRESHOLD = custom_config["at_risk_threshold"]
            if "suspended_threshold" in custom_config:
                self.config.SUSPENDED_THRESHOLD = custom_config["suspended_threshold"]
    
    def calculate_standing(self, gpa: float) -> AcademicStandingEnum:
        """
        Calculate academic standing based on GPA.
        
        Args:
            gpa: Current GPA value (typically 0.0 - 4.0)
            
        Returns:
            AcademicStandingEnum representing the student's standing
        """
        gpa = float(gpa) if gpa is not None else 0.0
        
        if gpa >= self.config.EXCELLENT_THRESHOLD:
            return AcademicStandingEnum.EXCELLENT
        elif gpa >= self.config.GOOD_THRESHOLD:
            return AcademicStandingEnum.GOOD
        elif gpa >= self.config.SATISFACTORY_THRESHOLD:
            return AcademicStandingEnum.SATISFACTORY
        elif gpa >= self.config.WARNING_THRESHOLD:
            return AcademicStandingEnum.WARNING
        elif gpa >= self.config.PROBATION_THRESHOLD:
            return AcademicStandingEnum.PROBATION
        elif gpa >= self.config.AT_RISK_THRESHOLD:
            return AcademicStandingEnum.AT_RISK
        else:
            return AcademicStandingEnum.SUSPENDED
    
    def is_on_probation(self, gpa: float) -> bool:
        """
        Check if student should be on academic probation.
        
        Probation triggered when GPA falls below the probation threshold.
        
        Args:
            gpa: Current GPA value
            
        Returns:
            True if student is on probation, False otherwise
        """
        gpa = float(gpa) if gpa is not None else 0.0
        standing = self.calculate_standing(gpa)
        return standing in [
            AcademicStandingEnum.PROBATION,
            AcademicStandingEnum.AT_RISK,
            AcademicStandingEnum.SUSPENDED
        ]
    
    def is_suspended(self, gpa: float) -> bool:
        """
        Check if student should be academically suspended.
        
        Suspension triggered when GPA falls below suspension threshold.
        
        Args:
            gpa: Current GPA value
            
        Returns:
            True if student should be suspended, False otherwise
        """
        gpa = float(gpa) if gpa is not None else 0.0
        return gpa < self.config.SUSPENDED_THRESHOLD
    
    def is_dean_list_eligible(self, gpa: float) -> bool:
        """
        Check if student qualifies for Dean's List.
        
        Dean's List typically requires excellent standing (GPA >= 3.5).
        
        Args:
            gpa: Current GPA value
            
        Returns:
            True if student qualifies for Dean's List, False otherwise
        """
        gpa = float(gpa) if gpa is not None else 0.0
        return self.calculate_standing(gpa) == AcademicStandingEnum.EXCELLENT
    
    def get_standing_description(self, gpa: float) -> str:
        """
        Get human-readable description of academic standing.
        
        Args:
            gpa: Current GPA value
            
        Returns:
            String description of the standing
        """
        standing = self.calculate_standing(gpa)
        
        descriptions = {
            AcademicStandingEnum.EXCELLENT: "Excellent - Dean's List candidate",
            AcademicStandingEnum.GOOD: "Good - Meets expectations",
            AcademicStandingEnum.SATISFACTORY: "Satisfactory - Acceptable performance",
            AcademicStandingEnum.WARNING: "Warning - Below satisfactory",
            AcademicStandingEnum.PROBATION: "Probation - At risk",
            AcademicStandingEnum.AT_RISK: "At Risk - Severe difficulty",
            AcademicStandingEnum.SUSPENDED: "Suspended - Not meeting minimum standards",
        }
        
        return descriptions.get(standing, "Unknown")
    
    def get_standing_color(self, gpa: float) -> str:
        """
        Get color code for UI representation.
        
        Args:
            gpa: Current GPA value
            
        Returns:
            Color code (green, yellow, red, etc.)
        """
        standing = self.calculate_standing(gpa)
        
        colors = {
            AcademicStandingEnum.EXCELLENT: "green",
            AcademicStandingEnum.GOOD: "lightgreen",
            AcademicStandingEnum.SATISFACTORY: "yellow",
            AcademicStandingEnum.WARNING: "orange",
            AcademicStandingEnum.PROBATION: "red",
            AcademicStandingEnum.AT_RISK: "darkred",
            AcademicStandingEnum.SUSPENDED: "black",
        }
        
        return colors.get(standing, "gray")
    
    def get_recommended_actions(self, gpa: float) -> List[str]:
        """
        Get recommended actions based on academic standing.
        
        Args:
            gpa: Current GPA value
            
        Returns:
            List of recommended actions
        """
        standing = self.calculate_standing(gpa)
        
        actions = {
            AcademicStandingEnum.EXCELLENT: [
                "Maintain excellent performance",
                "Consider honors/distinction track",
                "Eligible for academic scholarships"
            ],
            AcademicStandingEnum.GOOD: [
                "Continue with current study habits",
                "Maintain discipline and focus"
            ],
            AcademicStandingEnum.SATISFACTORY: [
                "Consider course review with academic advisor",
                "Increase study hours",
                "Attend tutoring sessions if available"
            ],
            AcademicStandingEnum.WARNING: [
                "Meet with academic advisor urgently",
                "Review study methods",
                "Identify and address struggling courses",
                "Consider course withdrawal/deferral"
            ],
            AcademicStandingEnum.PROBATION: [
                "Academic probation in effect",
                "Mandatory meeting with HOD",
                "Significant improvement required to avoid suspension",
                "Course load may be restricted"
            ],
            AcademicStandingEnum.AT_RISK: [
                "Immediate academic intervention required",
                "Consider deferral or part-time study",
                "Suspension risk very high"
            ],
            AcademicStandingEnum.SUSPENDED: [
                "Academic suspension in effect",
                "Meet with registrar for reinstatement procedures",
                "Appeal process may be available"
            ],
        }
        
        return actions.get(standing, [])
