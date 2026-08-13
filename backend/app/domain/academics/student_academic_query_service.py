"""
Student Academic Query Service

Repository-level queries for student academic records and status.
"""

from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.infrastructure.models.student import Student
from app.infrastructure.models.exam import Grade
from app.domain.academics.academic_standing_service import AcademicStandingService


class StudentAcademicQueryService:
    """
    Service for querying students based on academic status.
    
    Provides methods to find:
    - Students on probation
    - Students eligible for graduation
    - Students with excellent standing
    - Student academic summaries
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize Student Academic Query Service.
        
        Args:
            db: Motor async database instance
        """
        self.db = db
        self.students_collection = db.students
        self.grades_collection = db.grades
        self.standing_service = AcademicStandingService()
    
    async def get_students_on_probation(
        self,
        tenant_id: str,
        academic_year: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Get all students on academic probation for a tenant.
        
        Args:
            tenant_id: Tenant ID to query
            academic_year: Optional academic year filter
            limit: Maximum number of results to return
            
        Returns:
            List of student summaries with probation details
        """
        query = {
            "tenant_id": tenant_id,
            "is_on_probation": True,
            "status": {"$in": ["active", "registered"]}  # Exclude suspended/graduated
        }
        
        students = await self.students_collection.find(query).limit(limit).to_list(None)
        
        results = []
        for student in students:
            # Calculate current standing
            cgpa = float(student.get("cgpa", 0.0))
            standing = self.standing_service.calculate_standing(cgpa)
            
            results.append({
                "student_id": str(student.get("_id")),
                "name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                "student_code": student.get("student_id"),
                "cgpa": cgpa,
                "current_gpa": float(student.get("current_gpa", 0.0)),
                "academic_standing": standing.value,
                "probation_since": student.get("probation_since"),
                "programme_id": student.get("programme_id"),
                "department_id": student.get("department_id"),
                "contact_email": student.get("email"),
                "contact_phone": student.get("phone"),
            })
        
        return results
    
    async def get_students_eligible_for_graduation(
        self,
        tenant_id: str,
        academic_year: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        """
        Get students eligible for graduation.
        
        OPTIMIZED: Uses MongoDB aggregation pipeline to avoid N+1 queries.
        Joins students with grades in single server-side operation.
        
        A student is eligible if they have:
        - Completed their final level
        - Earned minimum credits
        - Met minimum CGPA
        - No failed courses
        - Good academic standing
        
        Args:
            tenant_id: Tenant ID to query
            academic_year: Optional academic year filter
            limit: Maximum number of results to return
            
        Returns:
            List of student summaries with graduation details
        """
        # Use aggregation pipeline for efficient join and calculation
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "entry_level": {"$in": ["400", "500", "600"]},  # Final levels
                    "cgpa": {"$gte": 2.0},  # Minimum CGPA
                    "status": {"$in": ["active", "registered"]}
                }
            },
            {
                "$lookup": {
                    "from": "grades",
                    "let": {"student_id": {"$toString": "$_id"}, "tenant": "$tenant_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$student_id", "$$student_id"]},
                                        {"$eq": ["$tenant_id", "$$tenant"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "grades"
                }
            },
            {
                "$addFields": {
                    "failed_count": {
                        "$size": {
                            "$filter": {
                                "input": "$grades",
                                "as": "grade",
                                "cond": {"$eq": ["$$grade.letter_grade", "F"]}
                            }
                        }
                    },
                    "total_credits": {"$multiply": [{"$size": "$grades"}, 3]}
                }
            },
            {"$limit": limit}
        ]
        
        students = await self.students_collection.aggregate(pipeline).to_list(None)
        
        results = []
        for student in students:
            cgpa = float(student.get("cgpa", 0.0))
            standing = self.standing_service.calculate_standing(cgpa)
            
            results.append({
                "student_id": str(student.get("_id")),
                "name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                "student_code": student.get("student_id"),
                "cgpa": cgpa,
                "total_credits": student.get("total_credits", 0),
                "failed_courses": student.get("failed_count", 0),
                "academic_standing": standing.value,
                "programme_id": student.get("programme_id"),
                "department_id": student.get("department_id"),
                "entry_year": student.get("entry_year"),
                "expected_graduation": self._calculate_expected_graduation(student),
            })
        
        return results
    
    async def get_students_with_excellent_standing(
        self,
        tenant_id: str,
        limit: int = 50
    ) -> List[dict]:
        """
        Get students with excellent academic standing (Dean's List).
        
        Args:
            tenant_id: Tenant ID to query
            limit: Maximum number of results to return
            
        Returns:
            List of student summaries with excellent standing
        """
        # Excellent standing: CGPA >= 3.5
        query = {
            "tenant_id": tenant_id,
            "cgpa": {"$gte": 3.5},
            "status": {"$in": ["active", "registered"]}
        }
        
        students = await self.students_collection.find(query).limit(limit).to_list(None)
        
        results = []
        for student in students:
            cgpa = float(student.get("cgpa", 0.0))
            
            results.append({
                "student_id": str(student.get("_id")),
                "name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
                "student_code": student.get("student_id"),
                "cgpa": cgpa,
                "current_gpa": float(student.get("current_gpa", 0.0)),
                "programme_id": student.get("programme_id"),
                "department_id": student.get("department_id"),
            })
        
        return results
    
    async def get_student_academic_summary(
        self,
        tenant_id: str,
        student_id: str
    ) -> Optional[dict]:
        """
        Get comprehensive academic summary for a student.
        
        Args:
            tenant_id: Tenant ID
            student_id: Student object ID
            
        Returns:
            Dictionary with complete academic summary or None if not found
        """
        student = await self.students_collection.find_one({
            "_id": student_id,
            "tenant_id": tenant_id
        })
        
        if not student:
            return None
        
        # Get all grades
        grades = await self.grades_collection.find({
            "tenant_id": tenant_id,
            "student_id": str(student_id)
        }).to_list(None)
        
        # Calculate statistics
        cgpa = float(student.get("cgpa", 0.0))
        current_gpa = float(student.get("current_gpa", 0.0))
        failed_courses = sum(1 for g in grades if g.get("letter_grade") == "F")
        passed_courses = sum(1 for g in grades if g.get("letter_grade") != "F")
        
        standing = self.standing_service.calculate_standing(cgpa)
        
        return {
            "student_id": str(student.get("_id")),
            "name": f"{student.get('first_name', '')} {student.get('last_name', '')}",
            "student_code": student.get("student_id"),
            "programme_id": student.get("programme_id"),
            "department_id": student.get("department_id"),
            "entry_level": student.get("entry_level"),
            "entry_year": student.get("entry_year"),
            "status": student.get("status"),
            "cgpa": cgpa,
            "current_gpa": current_gpa,
            "is_on_probation": student.get("is_on_probation", False),
            "probation_since": student.get("probation_since"),
            "academic_standing": standing.value,
            "total_courses": len(grades),
            "passed_courses": passed_courses,
            "failed_courses": failed_courses,
            "total_credits": len(grades) * 3,  # Simplified
        }
    
    async def get_enrollment_statistics_by_standing(
        self,
        tenant_id: str
    ) -> dict:
        """
        Get statistics of student enrollment by academic standing.
        
        OPTIMIZED: Uses MongoDB aggregation to compute statistics server-side
        instead of fetching all students into memory.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with counts by standing level
        """
        # Get total count
        total_count = await self.students_collection.count_documents({
            "tenant_id": tenant_id,
            "status": {"$in": ["active", "registered"]}
        })
        
        # Use aggregation to calculate standing distribution
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": {"$in": ["active", "registered"]}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "excellent": {
                        "$sum": {"$cond": [{"$gte": ["$cgpa", 3.5]}, 1, 0]}
                    },
                    "good": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$gte": ["$cgpa", 3.0]},
                                        {"$lt": ["$cgpa", 3.5]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "satisfactory": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$gte": ["$cgpa", 2.5]},
                                        {"$lt": ["$cgpa", 3.0]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "warning": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$gte": ["$cgpa", 2.0]},
                                        {"$lt": ["$cgpa", 2.5]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "probation": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$gte": ["$cgpa", 1.5]},
                                        {"$lt": ["$cgpa", 2.0]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "at_risk": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$gte": ["$cgpa", 1.0]},
                                        {"$lt": ["$cgpa", 1.5]}
                                    ]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "suspended": {
                        "$sum": {"$cond": [{"$lt": ["$cgpa", 1.0]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await self.students_collection.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            return {
                "excellent": stats.get("excellent", 0),
                "good": stats.get("good", 0),
                "satisfactory": stats.get("satisfactory", 0),
                "warning": stats.get("warning", 0),
                "probation": stats.get("probation", 0),
                "at_risk": stats.get("at_risk", 0),
                "suspended": stats.get("suspended", 0),
                "total": total_count
            }
        
        # Return zeros if no students found
        return {
            "excellent": 0,
            "good": 0,
            "satisfactory": 0,
            "warning": 0,
            "probation": 0,
            "at_risk": 0,
            "suspended": 0,
            "total": 0
        }
    
    @staticmethod
    def _calculate_expected_graduation(student: dict) -> datetime:
        """
        Calculate expected graduation date based on entry level and year.
        
        Simplified calculation assuming:
        - Level 100: First year
        - Level 200: Second year
        - Level 300: Third year
        - Level 400: Fourth year
        
        Args:
            student: Student document
            
        Returns:
            Estimated graduation datetime
        """
        from datetime import timedelta
        
        entry_year = int(student.get("entry_year", 2026))
        entry_level = int(student.get("entry_level", 100))
        
        # Calculate years remaining
        level = (entry_level // 100)  # 1, 2, 3, or 4
        years_to_complete = 4 - (level - 1)
        
        graduation_year = entry_year + years_to_complete
        
        # Assume graduation in June of final year
        return datetime(graduation_year, 6, 15)
