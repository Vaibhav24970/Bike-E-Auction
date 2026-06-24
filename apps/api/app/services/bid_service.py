from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import timedelta

from app.models import Auction, Bid, User, AuctionStatus, now_utc
from app.schemas import BidPlaceRequest, PaginatedBidHistory, BidHistoryItem
from app.websocket.manager import manager

class BidService:
    """Business logic for Bidding and auto-extensions."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def place_bid(self, auction_id: str, payload: BidPlaceRequest, user: User) -> Bid:
        # Lock the auction row to prevent concurrent bidding issues
        result = await self.db.execute(
            select(Auction).where(Auction.id == auction_id).with_for_update()
        )
        auction = result.scalar_one_or_none()
        
        if not auction:
            raise HTTPException(status_code=404, detail="Auction not found")
            
        if auction.status != AuctionStatus.LIVE:
            raise HTTPException(status_code=400, detail=f"Cannot bid on auction with status {auction.status}")

        # Validate amount
        current_highest = auction.current_bid or auction.starting_price
        min_required = current_highest + auction.bid_increment if auction.current_bid else auction.starting_price
        
        if payload.amount < min_required:
            raise HTTPException(status_code=400, detail=f"Bid must be at least {min_required} paise")

        # Place bid
        new_bid = Bid(
            auction_id=auction.id,
            user_id=user.id,
            amount=payload.amount,
            is_winning=True
        )
        self.db.add(new_bid)
        
        # Mark old winning bid as false
        if auction.current_bid:
            old_bids_result = await self.db.execute(
                select(Bid).where(Bid.auction_id == auction.id, Bid.is_winning == True)
            )
            old_winning = old_bids_result.scalars().all()
            for b in old_winning:
                b.is_winning = False

        # Update auction
        auction.current_bid = payload.amount
        auction.current_winner_id = user.id
        
        # Auto-extension logic
        extended = False
        time_remaining = (auction.scheduled_end - now_utc()).total_seconds()
        if time_remaining < 30 and getattr(auction, "extension_count", 0) < 3:
            auction.scheduled_end += timedelta(minutes=2)
            auction.extension_count += 1
            extended = True

        await self.db.commit()
        await self.db.refresh(new_bid)
        
        # Broadcast BID_PLACED
        timestamp = new_bid.created_at.isoformat() if new_bid.created_at else now_utc().isoformat()
        await manager.broadcast_to_auction(auction_id, {
            "type": "BID_PLACED",
            "data": {
                "amount": payload.amount,
                "bidder_name": f"{user.first_name} {user.last_name}".strip(),
                "timestamp": timestamp
            }
        })
        
        if extended:
            await manager.broadcast_to_auction(auction_id, {
                "type": "AUCTION_EXTENDED",
                "data": {
                    "new_end_time": auction.scheduled_end.isoformat(),
                    "extension_count": auction.extension_count
                }
            })
            
        return new_bid

    async def get_bid_history(self, auction_id: str, page: int = 1, size: int = 20) -> PaginatedBidHistory:
        # Check auction
        result = await self.db.execute(select(Auction).where(Auction.id == auction_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Auction not found")

        # Get total count
        count_query = select(func.count()).select_from(Bid).where(Bid.auction_id == auction_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated items
        offset = (page - 1) * size
        query = (
            select(Bid, User)
            .join(User, Bid.user_id == User.id)
            .where(Bid.auction_id == auction_id)
            .order_by(Bid.created_at.desc()) # Chronological descending
            .offset(offset)
            .limit(size)
        )
        items_result = await self.db.execute(query)
        rows = items_result.all()

        history_items = []
        for bid, user in rows:
            history_items.append(
                BidHistoryItem(
                    id=bid.id,
                    amount=bid.amount,
                    is_winning=bid.is_winning,
                    created_at=bid.created_at,
                    bidder_name=f"{user.first_name} {user.last_name}".strip()
                )
            )

        return PaginatedBidHistory(
            items=history_items,
            total=total,
            page=page,
            size=size
        )
