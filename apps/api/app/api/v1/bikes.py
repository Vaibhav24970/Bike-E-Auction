from typing import List
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin, get_current_user
from app.models import User
from app.schemas import BikeCreate, BikeUpdate, BikeResponse
from app.services.bike_service import BikeService
from app.core.rate_limit import limiter

router = APIRouter()

def get_bike_service(db: AsyncSession = Depends(get_db)) -> BikeService:
    return BikeService(db)

@router.get("/", response_model=List[BikeResponse])
async def list_bikes(bike_service: BikeService = Depends(get_bike_service)):
    """List all bikes. Open to public or authenticated users."""
    return await bike_service.list_bikes()

@router.get("/{bike_id}", response_model=BikeResponse)
async def get_bike(bike_id: str, bike_service: BikeService = Depends(get_bike_service)):
    """Get bike details."""
    return await bike_service.get_bike(bike_id)

@router.post("/", response_model=BikeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_bike(
    request: Request,
    payload: BikeCreate,
    admin_user: User = Depends(require_admin),
    bike_service: BikeService = Depends(get_bike_service)
):
    """Create a new bike. Admin only."""
    return await bike_service.create_bike(payload)

@router.patch("/{bike_id}", response_model=BikeResponse)
@limiter.limit("20/minute")
async def update_bike(
    request: Request,
    bike_id: str,
    payload: BikeUpdate,
    admin_user: User = Depends(require_admin),
    bike_service: BikeService = Depends(get_bike_service)
):
    """Update bike details. Admin only."""
    return await bike_service.update_bike(bike_id, payload)

@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_bike(
    request: Request,
    bike_id: str,
    admin_user: User = Depends(require_admin),
    bike_service: BikeService = Depends(get_bike_service)
):
    """Delete a bike. Admin only."""
    await bike_service.delete_bike(bike_id)
    return None
