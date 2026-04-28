# Script separato: python -m app/services/create_admin.py
import asyncio

from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base

async def _create_admin() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.is_admin == True))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Admin already exists: {existing.email}")
            return

        email = input("Admin email: ").strip()
        password = input("Admin password: ").strip()

        if not email or not password:
            print("Cancelled.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )
        session.add(admin)
        await session.commit()
        print(f"Admin created: {email}")

if __name__ == "__main__":
    asyncio.run(_create_admin())