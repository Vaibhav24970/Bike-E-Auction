from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_db, get_current_user
from app.models import User
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register(payload)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, payload: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    token = await auth_service.login(payload)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
