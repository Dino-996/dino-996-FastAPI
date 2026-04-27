import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models.user import User
from app.core.security import hash_password
from app.db.base import Base

DATABASE_URL = os.environ["DATABASE_URL"]

async def create_admin() -> None:
    """ Initialize the database and ensure an admin user exists """
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if there is an admin
        result = await session.execute(select(User).where(User.is_admin==True))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"Admin already exists: {existing.email}")
            return

        email=input("Admin email: ").strip()
        password=input("Admin password: ").strip()

        if not email or not password:
            print()
            return

        admin = User(
            email = email,
            hashed_password = hash_password(password),
            is_active = True,
            is_admin = True
        )

        session.add(admin)
        await session.commit()
        print(f"Admin created: {email}")

    await engine.dispose()

