from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Auction, Bike, User
from app.schemas import AuctionCreate

class AuctionService:
    """Business logic for Auction management."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_auctions(self) -> List[Auction]:
        result = await self.db.execute(select(Auction))
        return result.scalars().all()

    async def get_auction(self, auction_id: str) -> Auction:
        result = await self.db.execute(select(Auction).where(Auction.id == auction_id))
        auction = result.scalar_one_or_none()
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")
        return auction

    async def create_auction(self, payload: AuctionCreate, admin_user: User) -> Auction:
        # Verify bike exists
        bike = await self.db.execute(select(Bike).where(Bike.id == payload.bike_id))
        if not bike.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Bike not found")

        auction = Auction(
            bike_id=payload.bike_id,
            created_by_id=admin_user.id,
            title=payload.title,
            description=payload.description,
            starting_price=payload.starting_price,
            reserve_price=payload.reserve_price,
            bid_increment=payload.bid_increment,
            scheduled_start=payload.scheduled_start,
            scheduled_end=payload.scheduled_end
        )
        self.db.add(auction)
        await self.db.flush()
        return auction
