from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Asset(Document):
    tenant_id: str
    asset_type: str
    name: str
    description: Optional[str] = None

    purchase_date: datetime
    purchase_price: float
    current_value: float

    depreciation_rate: float = 0.1

    assigned_to: Optional[str] = None
    location: Optional[str] = None

    class Settings:
        name = "assets"

class Inventory(Document):
    tenant_id: str
    item_name: str
    quantity: int
    unit: str

    reorder_level: int

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "inventory"

class MaintenanceSchedule(Document):
    tenant_id: str
    asset_id: str

    maintenance_date: datetime
    maintenance_type: str

    performed_by: Optional[str] = None
    status: str = "scheduled"

    class Settings:
        name = "maintenance_schedules"
