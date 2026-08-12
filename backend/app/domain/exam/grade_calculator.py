from typing import Optional

class GradeCalculator:
    """Calculate grades, GPA, and CGPA"""

    GRADE_POINTS = {
        "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0,
    }

    def __init__(self):
        pass

    async def calculate_letter_grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D+"
        elif score >= 45:
            return "D"
        else:
            return "F"

    async def calculate_gpa(self, grades: list, credits: list) -> float:
        total_points = 0
        total_credits = 0

        for grade, credit in zip(grades, credits):
            gpa_points = self.GRADE_POINTS.get(grade, 0.0)
            total_points += gpa_points * credit
            total_credits += credit

        if total_credits == 0:
            return 0.0

        return round(total_points / total_credits, 2)

    async def calculate_cgpa(self, semester_gpas: list, semester_credits: list) -> float:
        total_points = 0
        total_credits = 0

        for gpa, credits in zip(semester_gpas, semester_credits):
            total_points += gpa * credits
            total_credits += credits

        if total_credits == 0:
            return 0.0

        return round(total_points / total_credits, 2)

    async def determine_academic_standing(self, cgpa: float) -> tuple:
        if cgpa >= 3.5:
            return "Excellent", False
        elif cgpa >= 3.0:
            return "Good Standing", False
        elif cgpa >= 2.0:
            return "Satisfactory", False
        elif cgpa >= 1.5:
            return "Academic Probation", True
        else:
            return "Dismissal", True
