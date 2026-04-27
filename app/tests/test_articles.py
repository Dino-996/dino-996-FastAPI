import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.article import Article
from app.core.security import hash_password
from datetime import datetime, timezone

# Test data

ADMIN = {"email": "admin@google.com", "password": "admin"}

ARTICLE = {
    "title": "Articolo di test",
    "description": "Descrizione di test",
    "tags": ["linux", "open-source"],
    "date": "2024-01-01T00:00:00Z",
    "excerpt": "Testo di anteprima",
    "image": "https://example.com/img.jpg",
    "imageAlt": "Immagine di test",
}

# Helper

async def create_admin_and_login(client: AsyncClient, db: AsyncSession) -> dict:
    """ Create the admin user directly in the db """
    admin = User(
        email=ADMIN["admin@gmail.com"],
        hashed_password=hash_password(ADMIN["admin"]),
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    await db.commit()

    response = await client.post("/auth/login", json=ADMIN)
    assert response.status_code == 200, "Login admin fallito"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Pubblic reading

async def test_list_articles_public_empty(client: AsyncClient):
    """Lista vuota senza token → 200 con lista vuota."""
    response = await client.get("/articles")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_article_public_not_found(client: AsyncClient):
    """Articolo inesistente senza token → 404."""
    response = await client.get("/articles/9999")
    assert response.status_code == 404


async def test_list_articles_public_with_data(client: AsyncClient, db: AsyncSession):
    """Lista pubblica con articoli → 200 con dati corretti."""
    headers = await create_admin_and_login(client, db)
    await client.post("/articles", json=ARTICLE, headers=headers)

    # Lettura senza token
    response = await client.get("/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == ARTICLE["title"]


async def test_get_article_public_success(client: AsyncClient, db: AsyncSession):
    """Dettaglio articolo pubblico → 200 con dati corretti."""
    headers = await create_admin_and_login(client, db)
    created = await client.post("/articles", json=ARTICLE, headers=headers)
    article_id = created.json()["id"]

    response = await client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    assert response.json()["id"] == article_id
    assert response.json()["title"] == ARTICLE["title"]


# ─── Test: paginazione ────────────────────────────────────────────────────────

async def test_list_articles_pagination(client: AsyncClient, db: AsyncSession):
    """Paginazione: limit e offset funzionano correttamente."""
    headers = await create_admin_and_login(client, db)
    for i in range(5):
        await client.post("/articles", json={**ARTICLE, "title": f"Articolo {i}"}, headers=headers)

    response = await client.get("/articles?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/articles?limit=2&offset=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/articles?limit=2&offset=4")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_list_articles_default_limit(client: AsyncClient, db: AsyncSession):
    """Senza parametri il limite di default è 5."""
    headers = await create_admin_and_login(client, db)
    for i in range(7):
        await client.post("/articles", json={**ARTICLE, "title": f"Articolo {i}"}, headers=headers)

    response = await client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 5


# ─── Test: creazione ─────────────────────────────────────────────────────────

async def test_create_article_success(client: AsyncClient, db: AsyncSession):
    """Creazione con admin → 201 con tutti i campi attesi."""
    headers = await create_admin_and_login(client, db)
    response = await client.post("/articles", json=ARTICLE, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == ARTICLE["title"]
    assert data["description"] == ARTICLE["description"]
    assert data["tags"] == ARTICLE["tags"]
    assert data["excerpt"] == ARTICLE["excerpt"]
    assert "id" in data


async def test_create_article_no_token(client: AsyncClient):
    """Creazione senza token → 403 Forbidden."""
    response = await client.post("/articles", json=ARTICLE)
    assert response.status_code == 403


async def test_create_article_invalid_token(client: AsyncClient):
    """Creazione con token falso → 401 Unauthorized."""
    response = await client.post(
        "/articles",
        json=ARTICLE,
        headers={"Authorization": "Bearer tokenfalso"}
    )
    assert response.status_code == 401


async def test_create_article_missing_title(client: AsyncClient, db: AsyncSession):
    """Creazione senza titolo (campo obbligatorio) → 422 Unprocessable Entity."""
    headers = await create_admin_and_login(client, db)
    payload = {k: v for k, v in ARTICLE.items() if k != "title"}
    response = await client.post("/articles", json=payload, headers=headers)
    assert response.status_code == 422


async def test_create_article_missing_date(client: AsyncClient, db: AsyncSession):
    """Creazione senza data (campo obbligatorio) → 422 Unprocessable Entity."""
    headers = await create_admin_and_login(client, db)
    payload = {k: v for k, v in ARTICLE.items() if k != "date"}
    response = await client.post("/articles", json=payload, headers=headers)
    assert response.status_code == 422


async def test_create_article_optional_fields(client: AsyncClient, db: AsyncSession):
    """Creazione con soli campi obbligatori → 201, campi opzionali sono None."""
    headers = await create_admin_and_login(client, db)
    payload = {"title": "Solo titolo", "date": "2024-06-01T00:00:00Z"}
    response = await client.post("/articles", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["description"] is None
    assert data["excerpt"] is None
    assert data["image"] is None
    assert data["tags"] == []


# ─── Test: aggiornamento ─────────────────────────────────────────────────────

async def test_update_article_success(client: AsyncClient, db: AsyncSession):
    """Aggiornamento parziale del titolo → 200, gli altri campi restano invariati."""
    headers = await create_admin_and_login(client, db)
    created = await client.post("/articles", json=ARTICLE, headers=headers)
    article_id = created.json()["id"]

    response = await client.put(
        f"/articles/{article_id}",
        json={"title": "Titolo aggiornato"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Titolo aggiornato"
    assert data["description"] == ARTICLE["description"]
    assert data["tags"] == ARTICLE["tags"]


async def test_update_article_not_found(client: AsyncClient, db: AsyncSession):
    """Aggiornamento articolo inesistente → 404."""
    headers = await create_admin_and_login(client, db)
    response = await client.put("/articles/9999", json={"title": "x"}, headers=headers)
    assert response.status_code == 404


async def test_update_article_no_token(client: AsyncClient):
    """Aggiornamento senza token → 403 Forbidden."""
    response = await client.put("/articles/1", json={"title": "x"})
    assert response.status_code == 403


# ─── Test: eliminazione ──────────────────────────────────────────────────────

async def test_delete_article_success(client: AsyncClient, db: AsyncSession):
    """Eliminazione → 204, poi il GET restituisce 404."""
    headers = await create_admin_and_login(client, db)
    created = await client.post("/articles", json=ARTICLE, headers=headers)
    article_id = created.json()["id"]

    response = await client.delete(f"/articles/{article_id}", headers=headers)
    assert response.status_code == 204

    response = await client.get(f"/articles/{article_id}")
    assert response.status_code == 404


async def test_delete_article_not_found(client: AsyncClient, db: AsyncSession):
    """Eliminazione articolo inesistente → 404."""
    headers = await create_admin_and_login(client, db)
    response = await client.delete("/articles/9999", headers=headers)
    assert response.status_code == 404


async def test_delete_article_no_token(client: AsyncClient):
    """Eliminazione senza token → 403 Forbidden."""
    response = await client.delete("/articles/1")
    assert response.status_code == 403