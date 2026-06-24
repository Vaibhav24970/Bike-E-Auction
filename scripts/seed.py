import asyncio
import os
from datetime import datetime, timedelta

# Set up env vars for the script before importing app modules
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/eauction"
os.environ["ENVIRONMENT"] = "development"
os.environ["JWT_SECRET_KEY"] = "dev-secret-key-do-not-use-in-prod"

from app.database import AsyncSessionLocal, engine
from sqlalchemy.future import select
from app.models import Base, User, Bike, Auction, AuctionStatus, BikeCondition
from app.core.security import hash_password
from app.models import now_utc

async def seed():
    print("Starting database seed...")
    
    # Optional: create tables if they don't exist (useful for dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        # Check if Admin exists
        result = await db.execute(select(User).where(User.email == "admin@example.com"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=hash_password("Admin123!"),
                first_name="Admin",
                last_name="User",
                role="ADMIN"
            )
            db.add(admin)
            
        # Check if Normal User exists
        result = await db.execute(select(User).where(User.email == "user@example.com"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email="user@example.com",
                hashed_password=hash_password("User123!"),
                first_name="Normal",
                last_name="User",
                role="USER"
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(admin)
        
        # Check if Bikes exist
        result = await db.execute(select(Bike).where(Bike.make == "Yamaha"))
        bike1 = result.scalars().first()
        if not bike1:
            bike1 = Bike(
                make="Yamaha", model="R15", year=2023, mileage_km=1500,
                condition=BikeCondition.EXCELLENT, description="Almost new Yamaha R15",
                engine_cc=155,
            )
            db.add(bike1)

        result = await db.execute(select(Bike).where(Bike.make == "Royal Enfield"))
        bike2 = result.scalars().first()
        if not bike2:
            bike2 = Bike(
                make="Royal Enfield", model="Classic 350", year=2021, mileage_km=12000,
                condition=BikeCondition.GOOD, description="Well maintained Classic 350",
                engine_cc=349,
            )
            db.add(bike2)
            
        await db.commit()
        await db.refresh(bike1)
        await db.refresh(bike2)
        
        # Create Auctions only if none exist
        result = await db.execute(select(Auction))
        existing_auctions = result.scalars().all()
        
        if not existing_auctions:
            now = now_utc()
            
            # Live Auction
            auction1 = Auction(
                bike_id=bike1.id,
                title="Mint Condition Yamaha R15",
                description="Bidding is now open for this excellent condition Yamaha R15.",
                starting_price=100000,
                reserve_price=120000,
                bid_increment=5000,
                status=AuctionStatus.LIVE,
                scheduled_start=now - timedelta(hours=1),
                scheduled_end=now + timedelta(hours=2),
                actual_start=now - timedelta(hours=1)
            )
            
            # Scheduled Auction
            auction2 = Auction(
                bike_id=bike2.id,
                title="Classic 350 for sale",
                description="Upcoming auction for RE Classic 350.",
                starting_price=120000,
                reserve_price=150000,
                bid_increment=5000,
                status=AuctionStatus.SCHEDULED,
                scheduled_start=now + timedelta(hours=24),
                scheduled_end=now + timedelta(hours=48),
            )
            
            db.add_all([auction1, auction2])
            await db.commit()
        
        print("Database seeded successfully!")
        print("Admin login: admin@example.com / Admin123!")
        print("User login: user@example.com / User123!")

if __name__ == "__main__":
    asyncio.run(seed())
