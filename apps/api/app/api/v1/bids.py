from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas import BidPlaceRequest, BidResponse, PaginatedBidHistory
from app.services.bid_service import BidService
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter()

def get_bid_service(db: AsyncSession = Depends(get_db)) -> BidService:
    return BidService(db)



@router.post("/auction/{auction_id}", response_model=BidResponse)
@limiter.limit("20/minute")
async def place_bid(
    request: Request,
    auction_id: str,
    payload: BidPlaceRequest,
    user: User = Depends(get_current_user),
    bid_service: BidService = Depends(get_bid_service)
):
    return await bid_service.place_bid(auction_id, payload, user)

@router.get("/auction/{auction_id}", response_model=PaginatedBidHistory)
async def get_bid_history(
    auction_id: str,
    page: int = 1,
    size: int = 20,
    bid_service: BidService = Depends(get_bid_service)
):
    return await bid_service.get_bid_history(auction_id, page, size)
