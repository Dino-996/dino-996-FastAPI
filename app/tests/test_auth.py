"""
TEST DI AUTENTICAZIONE
────────────────────────
Questi test coprono tutti gli endpoint di /auth.
Non modificarli — funzionano per qualsiasi progetto che usa questo skeleton.
"""
from httpx import AsyncClient

# Utente di test riutilizzato in tutti i test
USER = {"email": "test@example.com", "password": "password123"}


async def test_register_success(client: AsyncClient):
    """Registrazione corretta → 201 con dati utente (senza password)."""
    response = await client.post("/auth/register", json=USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == USER["email"]
    assert data["is_active"] is True
    # La password non deve mai comparire nella risposta
    assert "hashed_password" not in data
    assert "password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    """Registrazione con email già usata → 409 Conflict."""
    await client.post("/auth/register", json=USER)
    response = await client.post("/auth/register", json=USER)
    assert response.status_code == 409


async def test_login_success(client: AsyncClient):
    """Login corretto → 200 con access_token e refresh_token."""
    await client.post("/auth/register", json=USER)
    response = await client.post("/auth/login", json=USER)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    """Password sbagliata → 401 Unauthorized."""
    await client.post("/auth/register", json=USER)
    response = await client.post("/auth/login", json={
        "email": USER["email"],
        "password": "passwordsbagliata"
    })
    assert response.status_code == 401


async def test_login_user_not_found(client: AsyncClient):
    """Email inesistente → 401 (stesso errore di password sbagliata, per sicurezza)."""
    response = await client.post("/auth/login", json=USER)
    assert response.status_code == 401


async def test_me_success(client: AsyncClient):
    """GET /auth/me con token valido → 200 con dati utente."""
    await client.post("/auth/register", json=USER)
    login = await client.post("/auth/login", json=USER)
    token = login.json()["access_token"]
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == USER["email"]


async def test_me_no_token(client: AsyncClient):
    """GET /auth/me senza token → 403 Forbidden."""
    response = await client.get("/auth/me")
    assert response.status_code == 403


async def test_me_invalid_token(client: AsyncClient):
    """GET /auth/me con token falso → 401 Unauthorized."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer tokenfalso"}
    )
    assert response.status_code == 401


async def test_refresh_success(client: AsyncClient):
    """Refresh token valido → 200 con nuovi token."""
    await client.post("/auth/register", json=USER)
    login = await client.post("/auth/login", json=USER)
    refresh_token = login.json()["refresh_token"]
    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
