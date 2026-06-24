from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.auctions import router as auctions_router
from app.api.v1.bids import router as bids_router
from app.api.v1.bikes import router as bikes_router
from app.api.v1.ws import router as ws_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(auctions_router, prefix="/auctions", tags=["Auctions"])
api_router.include_router(bids_router, prefix="/bids", tags=["Bids"])
api_router.include_router(bikes_router, prefix="/bikes", tags=["Bikes"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSockets"])
