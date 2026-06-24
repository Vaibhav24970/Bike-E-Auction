import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def _uuid_default() -> str:
    return str(uuid.uuid4())

def now_utc():
    return datetime.now(timezone.utc)

class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class BikeCondition(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"

class AuctionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    ENDED = "ENDED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid_default)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(Role), nullable=False, default=Role.USER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Bike(Base):
    __tablename__ = "bikes"

    id = Column(String, primary_key=True, default=_uuid_default)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=False)
    condition = Column(Enum(BikeCondition), nullable=False)
    description = Column(Text, nullable=False)
    images = Column(ARRAY(String), nullable=False, default=list)
    vin = Column(String(17), unique=True, nullable=True)
    engine_cc = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

class Auction(Base):
    __tablename__ = "auctions"

    id = Column(String, primary_key=True, default=_uuid_default)
    bike_id = Column(String, ForeignKey("bikes.id"), nullable=False)
    created_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AuctionStatus), nullable=False, default=AuctionStatus.DRAFT)
    
    # Values in paise (INR * 100)
    starting_price = Column(Integer, nullable=False)
    reserve_price = Column(Integer, nullable=True)
    current_bid = Column(Integer, nullable=True)
    bid_increment = Column(Integer, nullable=False, default=10000)
    
    current_winner_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    extension_count = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), default=now_utc)

    # Relationships
    bike = relationship("Bike", lazy="selectin")
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    current_winner = relationship("User", foreign_keys=[current_winner_id], lazy="selectin")
    bids = relationship("Bid", back_populates="auction", lazy="selectin")

class Bid(Base):
    __tablename__ = "bids"

    id = Column(String, primary_key=True, default=_uuid_default)
    auction_id = Column(String, ForeignKey("auctions.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    is_winning = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    # Relationships
    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", lazy="selectin")
