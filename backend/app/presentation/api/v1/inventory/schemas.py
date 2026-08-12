from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateAssetRequest(BaseModel):
    asset_type: str
    name: str
    description: Optional[str] = None
    purchase_date: datetime
    purchase_price: float
    location: Optional[str] = None

class CreateInventoryItemRequest(BaseModel):
    item_name: str
    quantity: int
    unit: str
    reorder_level: int
