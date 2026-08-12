from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Venue(Document):
    tenant_id: str
    name: str
    capacity: int
    venue_type: str

    equipment: list = []

    class Settings:
        name = "venues"

class TimeSlot(Document):
    tenant_id: str
    start_time: str
    end_time: str

    class Settings:
        name = "time_slots"

class Timetable(Document):
    tenant_id: str
    course_id: str
    lecturer_id: str
    venue_id: str

    day_of_week: str
    time_slot_id: str

    semester: str
    academic_year: str

    class Settings:
        name = "timetables"
