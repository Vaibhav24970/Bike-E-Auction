from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Bike, BikeCondition
from app.schemas import BikeCreate, BikeUpdate

class BikeService:
    """Business logic for Bike management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_bikes(self) -> List[Bike]:
        result = await self.db.execute(select(Bike))
        return result.scalars().all()

    async def get_bike(self, bike_id: str) -> Bike:
        result = await self.db.execute(select(Bike).where(Bike.id == bike_id))
        bike = result.scalar_one_or_none()
        if not bike:
            raise HTTPException(status_code=404, detail="Bike not found")
        return bike

    async def create_bike(self, payload: BikeCreate) -> Bike:
        # Validate Enum
        try:
            condition = BikeCondition(payload.condition.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid bike condition")

        bike = Bike(
            make=payload.make,
            model=payload.model,
            year=payload.year,
            mileage_km=payload.mileage_km,
            condition=condition,
            description=payload.description,
            images=payload.images,
            vin=payload.vin,
            engine_cc=payload.engine_cc,
            color=payload.color
        )
        self.db.add(bike)
        await self.db.flush()
        return bike

    async def update_bike(self, bike_id: str, payload: BikeUpdate) -> Bike:
        bike = await self.get_bike(bike_id)
        
        update_data = payload.model_dump(exclude_unset=True)
        if "condition" in update_data and update_data["condition"]:
            try:
                update_data["condition"] = BikeCondition(update_data["condition"].upper())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid bike condition")

        for key, value in update_data.items():
            setattr(bike, key, value)
            
        await self.db.flush()
        return bike

    async def delete_bike(self, bike_id: str) -> None:
        bike = await self.get_bike(bike_id)
        # Check if auctions exist for this bike (left for integrity check by DB)
        # SQLAlchemy will throw an IntegrityError if a foreign key is violated.
        await self.db.delete(bike)
        await self.db.flush()
