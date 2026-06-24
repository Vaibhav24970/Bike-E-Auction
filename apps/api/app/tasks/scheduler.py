import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import AsyncSessionLocal
from app.models import Auction, AuctionStatus, now_utc
from app.core.logging import get_logger
from app.websocket.manager import manager

logger = get_logger(__name__)

async def process_auctions():
    """Background task to manage auction states."""
    while True:
        try:
            async with AsyncSessionLocal() as db:
                now = now_utc()
                
                # 1. Start scheduled auctions
                scheduled_query = select(Auction).where(
                    Auction.status == AuctionStatus.SCHEDULED,
                    Auction.scheduled_start <= now
                )
                scheduled_result = await db.execute(scheduled_query)
                for auction in scheduled_result.scalars().all():
                    auction.status = AuctionStatus.LIVE
                    auction.actual_start = now
                    logger.info("auction_started", auction_id=auction.id)
                    await manager.broadcast_to_auction(auction.id, {
                        "type": "AUCTION_STARTED",
                        "data": {"auction_id": auction.id, "started_at": now.isoformat()}
                    })
                
                # 2. End live auctions
                live_query = select(Auction).where(
                    Auction.status == AuctionStatus.LIVE,
                    Auction.scheduled_end <= now
                )
                live_result = await db.execute(live_query)
                for auction in live_result.scalars().all():
                    auction.status = AuctionStatus.ENDED
                    auction.actual_end = now
                    
                    # Winner determination logic
                    # If reserve price exists, ensure current bid meets it
                    if auction.current_bid and auction.current_winner_id:
                        if auction.reserve_price and auction.current_bid < auction.reserve_price:
                            # Reserve not met
                            logger.info("auction_ended_reserve_not_met", auction_id=auction.id)
                            auction.current_winner_id = None # Clear winner since reserve not met
                        else:
                            logger.info("auction_ended_with_winner", auction_id=auction.id, winner_id=auction.current_winner_id)
                    else:
                        logger.info("auction_ended_no_bids", auction_id=auction.id)
                    
                    await manager.broadcast_to_auction(auction.id, {
                        "type": "AUCTION_ENDED",
                        "data": {
                            "auction_id": auction.id, 
                            "winner_id": auction.current_winner_id,
                            "final_price": auction.current_bid
                        }
                    })
                        
                await db.commit()
                
        except Exception as e:
            logger.error("auction_scheduler_error", error=str(e))
            
        # Sleep for 10 seconds before checking again
        await asyncio.sleep(10)

def start_scheduler():
    loop = asyncio.get_event_loop()
    loop.create_task(process_auctions())
