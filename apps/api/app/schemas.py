from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re
from app.models import Role

class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserRegister(ConfiguredBaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*#?&]', v):
            raise ValueError('Password must contain at least one special character (@$!%*#?&)')
        return v

class UserLogin(ConfiguredBaseModel):
    email: EmailStr
    password: str

class UserResponse(ConfiguredBaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: Role
    created_at: datetime
    
class TokenResponse(ConfiguredBaseModel):
    access_token: str
    token_type: str = "bearer"

class BikeCreate(ConfiguredBaseModel):
    make: str
    model: str
    year: int
    mileage_km: int
    condition: str
    description: str
    images: list[str] = []
    vin: str | None = None
    engine_cc: int | None = None
    color: str | None = None

class BikeUpdate(ConfiguredBaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    mileage_km: int | None = None
    condition: str | None = None
    description: str | None = None
    images: list[str] | None = None
    vin: str | None = None
    engine_cc: int | None = None
    color: str | None = None

class BikeResponse(ConfiguredBaseModel):
    id: str
    make: str
    model: str
    year: int
    mileage_km: int
    condition: str
    description: str
    images: list[str]
    vin: str | None
    engine_cc: int | None
    color: str | None
    created_at: datetime

class AuctionCreate(ConfiguredBaseModel):
    bike_id: str
    title: str
    description: str | None = None
    starting_price: int
    reserve_price: int | None = None
    bid_increment: int = 10000
    scheduled_start: datetime
    scheduled_end: datetime

class AuctionResponse(ConfiguredBaseModel):
    id: str
    bike_id: str
    title: str
    description: str | None
    status: str
    starting_price: int
    current_bid: int | None
    scheduled_start: datetime
    scheduled_end: datetime

class BidPlaceRequest(BaseModel):
    amount: int

class BidResponse(ConfiguredBaseModel):
    id: str
    auction_id: str
    user_id: str
    amount: int
    is_winning: bool
    created_at: datetime

class BidHistoryItem(ConfiguredBaseModel):
    id: str
    amount: int
    is_winning: bool
    created_at: datetime
    bidder_name: str
    
class PaginatedBidHistory(ConfiguredBaseModel):
    items: list[BidHistoryItem]
    total: int
    page: int
    size: int
