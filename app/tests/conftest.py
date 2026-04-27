import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app as fastapi_app
from app.db.base import Base
from app.core.dependencies import get_db
import app.models.user
import app.models.article

# Test DB in-memory
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Fixture: expose session
@pytest_asyncio.fixture
async def db():
    """ Exposes the DB session to tests that need it directly """
    async with TestSessionLocal() as session:
        yield session

# Fixture: setup database
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """ Create all tables before testing, delete them afterward """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Fixture: clean database
@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """ Clear all tables after each test """
    yield
    async with engine.begin() as conn:
        # sorted_tables in ordine inverso rispetta le foreign key
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


# Fixture: client HTTP
@pytest_asyncio.fixture
async def client():
    """
    Client HTTP per i test — simula richieste reali all'API.
    Usa il DB SQLite in memoria invece di PostgreSQL.
    """
    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    # dependency_overrides replace get_db with the test version
    fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Restore the original dependencies after testing
    fastapi_app.dependency_overrides.clear()