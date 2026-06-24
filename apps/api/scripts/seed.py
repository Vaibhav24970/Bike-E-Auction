"""
Simple script to seed the database with initial users and bikes.
"""
import asyncio
from datetime import timedelta
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import engine, AsyncSessionLocal
from app.models import User, Role, Bike, BikeCondition, Auction, AuctionStatus, now_utc
from app.core.security import hash_password

async def seed_data():
    # Ensure tables exist using alembic, not init_db

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already contains data. Seeding skipped.")
            return

        print("Seeding users...")
        admin = User(
            email="admin@eauction.dev",
            password_hash=hash_password("Admin@123456"),
            first_name="Super",
            last_name="Admin",
            role=Role.ADMIN
        )
        user1 = User(
            email="rahul@example.com",
            password_hash=hash_password("User@123456"),
            first_name="Rahul",
            last_name="Sharma"
        )
        user2 = User(
            email="priya@example.com",
            password_hash=hash_password("User@123456"),
            first_name="Priya",
            last_name="Patel"
        )
        db.add_all([admin, user1, user2])
        await db.flush()

        print("Seeding bikes...")
        bike1 = Bike(
            make="Royal Enfield",
            model="Classic 350",
            year=2021,
            mileage_km=15000,
            condition=BikeCondition.EXCELLENT,
            description="Pristine condition Classic 350, single owner.",
            engine_cc=350,
            color="Stealth Black"
        )
        db.add(bike1)
        await db.flush()

        print("Seeding auctions...")
        auction1 = Auction(
            bike_id=bike1.id,
            created_by_id=admin.id,
            title="2021 Royal Enfield Classic 350 - Stealth Black",
            description="A beautiful Royal Enfield up for auction.",
            status=AuctionStatus.SCHEDULED,
            starting_price=10000000, # 1,00,000 INR
            reserve_price=12000000,  # 1,20,000 INR
            bid_increment=500000,    # 5,000 INR
            scheduled_start=now_utc() + timedelta(days=1),
            scheduled_end=now_utc() + timedelta(days=3)
        )
        db.add(auction1)
        
        await db.commit()
        print("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
