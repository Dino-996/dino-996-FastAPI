import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app as fastapi_app
from app.db.base import Base
from app.core.dependencies import get_db
import app.models.user
import app.models.article  # ← Aggiungi qui i tuoi modelli

# ─── Database di test ─────────────────────────────────────────────────────────
# SQLite in memoria — esiste solo durante i test, non tocca mai il DB reale.
# "/:memory:" = database temporaneo in RAM, distrutto alla fine dei test.
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# ─── Fixture: setup database ──────────────────────────────────────────────────
# scope="session" = eseguita una volta sola per tutta la sessione di test.
# autouse=True = applicata automaticamente senza doverla richiedere nei test.
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Crea tutte le tabelle prima dei test, le elimina alla fine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ─── Fixture: pulizia database ────────────────────────────────────────────────
# scope="function" (default) = eseguita prima e dopo ogni singolo test.
# Garantisce che ogni test parta con un DB pulito — i test sono indipendenti.
@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Svuota tutte le tabelle dopo ogni test."""
    yield
    async with engine.begin() as conn:
        # sorted_tables in ordine inverso rispetta le foreign key
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


# ─── Fixture: client HTTP ─────────────────────────────────────────────────────
# Sostituisce get_db con la versione SQLite per i test.
# ASGITransport simula il server HTTP senza avviarne uno reale.
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

    # dependency_overrides sostituisce get_db con la versione di test
    fastapi_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test"
    ) as ac:
        yield ac

    # Ripristina le dependency originali dopo il test
    fastapi_app.dependency_overrides.clear()