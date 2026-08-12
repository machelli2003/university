from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.presentation.api.v1.inventory.schemas import (
    CreateAssetRequest, CreateInventoryItemRequest
)
from app.infrastructure.database.repositories.inventory_repository import (
    AssetRepository, InventoryRepository
)
from app.dependencies import get_current_user, require_roles
from app.infrastructure.models.user import User

router = APIRouter()

def get_asset_repo() -> AssetRepository:
    return AssetRepository()

def get_inventory_repo() -> InventoryRepository:
    return InventoryRepository()

@router.post("/assets")
async def create_asset(
    request: CreateAssetRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    asset_repo=Depends(get_asset_repo),
):
    asset = await asset_repo.create({
        "tenant_id": current_user.tenant_id or "default",
        "current_value": request.purchase_price,
        **request.dict()
    })
    return {"id": str(asset.id)}

@router.get("/assets/type/{asset_type}")
async def list_assets_by_type(
    asset_type: str,
    current_user: User = Depends(get_current_user),
    asset_repo=Depends(get_asset_repo),
):
    assets = await asset_repo.get_by_type(current_user.tenant_id or "default", asset_type)
    return [{"id": str(a.id), "name": a.name, "current_value": a.current_value} for a in assets]

@router.post("/items")
async def create_inventory_item(
    request: CreateInventoryItemRequest,
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    inventory_repo=Depends(get_inventory_repo),
):
    item = await inventory_repo.create({"tenant_id": current_user.tenant_id or "default", **request.dict()})
    return {"id": str(item.id)}

@router.get("/items/low-stock")
async def list_low_stock(
    current_user: User = Depends(require_roles("university_admin", "super_admin")),
    inventory_repo=Depends(get_inventory_repo),
):
    items = await inventory_repo.get_low_stock(current_user.tenant_id or "default")
    return [{"id": str(i.id), "item_name": i.item_name, "quantity": i.quantity} for i in items]
