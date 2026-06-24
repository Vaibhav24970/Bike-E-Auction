import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import timedelta
from fastapi import HTTPException

from app.services.bid_service import BidService
from app.models import Auction, User, AuctionStatus, now_utc
from app.schemas import BidPlaceRequest

@pytest.fixture(autouse=True)
def mock_ws_manager():
    with patch("app.services.bid_service.manager") as mock_mgr:
        mock_mgr.broadcast_to_auction = AsyncMock()
        yield mock_mgr

@pytest.mark.asyncio
async def test_bid_auto_extends_under_30_seconds():
    db = AsyncMock()
    service = BidService(db)
    
    # Mock user
    user = User(id="user_1")
    
    # Mock auction ending in 10 seconds (under 30s)
    end_time = now_utc() + timedelta(seconds=10)
    auction = Auction(
        id="auction_1",
        status=AuctionStatus.LIVE,
        starting_price=1000,
        current_bid=2000,
        bid_increment=100,
        scheduled_end=end_time,
        extension_count=0
    )
    
    # Mock DB select for update
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auction
    db.execute.return_value = mock_result
    
    # Place valid bid
    bid_request = BidPlaceRequest(amount=2500)
    await service.place_bid("auction_1", bid_request, user)
    
    # Assert extension was applied
    assert auction.extension_count == 1
    assert auction.scheduled_end == end_time + timedelta(minutes=2)
    assert auction.current_bid == 2500

@pytest.mark.asyncio
async def test_bid_max_3_extensions_respected():
    db = AsyncMock()
    service = BidService(db)
    
    user = User(id="user_1")
    
    # Mock auction ending in 10 seconds, but already extended 3 times
    end_time = now_utc() + timedelta(seconds=10)
    auction = Auction(
        id="auction_1",
        status=AuctionStatus.LIVE,
        starting_price=1000,
        current_bid=2000,
        bid_increment=100,
        scheduled_end=end_time,
        extension_count=3
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auction
    db.execute.return_value = mock_result
    
    bid_request = BidPlaceRequest(amount=2500)
    await service.place_bid("auction_1", bid_request, user)
    
    # Assert extension was NOT applied because max reached
    assert auction.extension_count == 3
    assert auction.scheduled_end == end_time
    assert auction.current_bid == 2500

@pytest.mark.asyncio
async def test_bid_invalid_amount_fails():
    db = AsyncMock()
    service = BidService(db)
    user = User(id="user_1")
    
    auction = Auction(
        id="auction_1",
        status=AuctionStatus.LIVE,
        starting_price=1000,
        current_bid=2000,
        bid_increment=500,
        scheduled_end=now_utc() + timedelta(minutes=5),
        extension_count=0
    )
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = auction
    db.execute.return_value = mock_result
    
    # current_bid (2000) + increment (500) = 2500 required
    bid_request = BidPlaceRequest(amount=2200)
    
    with pytest.raises(HTTPException) as exc:
        await service.place_bid("auction_1", bid_request, user)
        
    assert exc.value.status_code == 400
    assert "Bid must be at least 2500 paise" in exc.value.detail
