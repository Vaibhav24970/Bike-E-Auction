import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import timedelta

from app.tasks.scheduler import process_auctions
from app.models import Auction, AuctionStatus, now_utc

@pytest.mark.asyncio
async def test_scheduler_starts_auctions():
    # Mock auction that should start
    now = now_utc()
    auction = Auction(
        id="a1",
        status=AuctionStatus.SCHEDULED,
        scheduled_start=now - timedelta(minutes=1),
        scheduled_end=now + timedelta(days=1)
    )

    db_session_mock = AsyncMock()
    # Setup mock to return our auction for the first query (scheduled)
    # and empty for the second query (live)
    scheduled_result = MagicMock()
    scheduled_result.scalars().all.return_value = [auction]
    
    live_result = MagicMock()
    live_result.scalars().all.return_value = []
    
    db_session_mock.execute.side_effect = [scheduled_result, live_result]

    with patch("app.tasks.scheduler.AsyncSessionLocal") as session_maker:
        session_maker.return_value.__aenter__.return_value = db_session_mock
        # We need to stop the while loop. Let's patch asyncio.sleep to raise an exception
        # so it breaks out of the loop after one iteration.
        with patch("asyncio.sleep", side_effect=Exception("Stop Loop")):
            try:
                await process_auctions()
            except Exception as e:
                if str(e) != "Stop Loop":
                    raise

    assert auction.status == AuctionStatus.LIVE
    assert auction.actual_start is not None
    db_session_mock.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_scheduler_ends_auctions_with_winner():
    now = now_utc()
    auction = Auction(
        id="a2",
        status=AuctionStatus.LIVE,
        scheduled_start=now - timedelta(days=1),
        scheduled_end=now - timedelta(minutes=1),
        current_bid=5000,
        reserve_price=4000,
        current_winner_id="user1"
    )

    db_session_mock = AsyncMock()
    scheduled_result = MagicMock()
    scheduled_result.scalars().all.return_value = []
    
    live_result = MagicMock()
    live_result.scalars().all.return_value = [auction]
    
    db_session_mock.execute.side_effect = [scheduled_result, live_result]

    with patch("app.tasks.scheduler.AsyncSessionLocal") as session_maker:
        session_maker.return_value.__aenter__.return_value = db_session_mock
        with patch("asyncio.sleep", side_effect=Exception("Stop Loop")):
            try:
                await process_auctions()
            except Exception as e:
                if str(e) != "Stop Loop":
                    raise

    assert auction.status == AuctionStatus.ENDED
    assert auction.actual_end is not None
    assert auction.current_winner_id == "user1"

@pytest.mark.asyncio
async def test_scheduler_ends_auctions_reserve_not_met():
    now = now_utc()
    auction = Auction(
        id="a3",
        status=AuctionStatus.LIVE,
        scheduled_start=now - timedelta(days=1),
        scheduled_end=now - timedelta(minutes=1),
        current_bid=3000,
        reserve_price=4000, # Reserve higher than current bid
        current_winner_id="user1"
    )

    db_session_mock = AsyncMock()
    scheduled_result = MagicMock()
    scheduled_result.scalars().all.return_value = []
    
    live_result = MagicMock()
    live_result.scalars().all.return_value = [auction]
    
    db_session_mock.execute.side_effect = [scheduled_result, live_result]

    with patch("app.tasks.scheduler.AsyncSessionLocal") as session_maker:
        session_maker.return_value.__aenter__.return_value = db_session_mock
        with patch("asyncio.sleep", side_effect=Exception("Stop Loop")):
            try:
                await process_auctions()
            except Exception as e:
                if str(e) != "Stop Loop":
                    raise

    assert auction.status == AuctionStatus.ENDED
    assert auction.current_winner_id is None # Reserve not met, winner cleared
