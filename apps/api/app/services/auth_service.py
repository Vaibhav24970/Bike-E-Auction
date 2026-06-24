from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import hash_password, verify_password, create_access_token
from app.models import User
from app.schemas import UserRegister, UserLogin

class AuthService:
    """Business logic for Authentication."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, payload: UserRegister) -> User:
        result = await self.db.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
            
        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, payload: UserLogin) -> str:
        result = await self.db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
            
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")
            
        return create_access_token(user.id, user.email, user.role.value)
