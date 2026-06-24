from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from datetime import datetime

from app.api.deps import get_db, require_admin
from app.models import AuctionStatus, User
from app.schemas import AuctionCreate, AuctionResponse
from app.services.auction_service import AuctionService
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter()

def get_auction_service(db: AsyncSession = Depends(get_db)) -> AuctionService:
    return AuctionService(db)



@router.get("/", response_model=List[AuctionResponse])
async def list_auctions(auction_service: AuctionService = Depends(get_auction_service)):
    return await auction_service.list_auctions()

@router.post("/", response_model=AuctionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_auction(
    request: Request,
    payload: AuctionCreate, 
    current_user: User = Depends(require_admin),
    auction_service: AuctionService = Depends(get_auction_service)
):
    return await auction_service.create_auction(payload, current_user)

@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(auction_id: str, auction_service: AuctionService = Depends(get_auction_service)):
    return await auction_service.get_auction(auction_id)
