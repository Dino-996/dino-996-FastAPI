"""
TEST CRUD DELLA TUA RISORSA
─────────────────────────────
Adatta questo file al tuo dominio:
  - Rinomina il file (es. test_books.py, test_todos.py)
  - Aggiorna ITEM e le URL (/items → /books, /todos...)
  - Aggiorna i campi nei body delle richieste
"""
from httpx import AsyncClient

USER = {"email": "test@example.com", "password": "password123"}
# ← Aggiorna questi campi in base al tuo modello
ITEM = {"name": "Item di test", "description": "Descrizione di test"}


# ─── Helper: ottieni token di autenticazione ──────────────────────────────────
async def get_auth_headers(client: AsyncClient) -> dict:
    """
    Registra un utente, fa login e restituisce gli header di autenticazione.
    Riutilizzato in ogni test che richiede autenticazione.
    """
    await client.post("/auth/register", json=USER)
    response = await client.post("/auth/login", json=USER)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── Test: creazione ──────────────────────────────────────────────────────────
async def test_create_item_success(client: AsyncClient):
    """Creazione corretta → 201 con dati dell'item."""
    headers = await get_auth_headers(client)
    response = await client.post("/items", json=ITEM, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == ITEM["name"]
    assert data["description"] == ITEM["description"]
    assert "id" in data
    assert "owner_id" in data


async def test_create_item_no_auth(client: AsyncClient):
    """Creazione senza token → 403 Forbidden."""
    response = await client.post("/items", json=ITEM)
    assert response.status_code == 403


# ─── Test: lista ──────────────────────────────────────────────────────────────
async def test_list_items_empty(client: AsyncClient):
    """Lista vuota per un nuovo utente → 200 con lista vuota."""
    headers = await get_auth_headers(client)
    response = await client.get("/items", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


async def test_list_items_with_data(client: AsyncClient):
    """Lista con due item → 200 con lista di 2 elementi."""
    headers = await get_auth_headers(client)
    await client.post("/items", json=ITEM, headers=headers)
    await client.post("/items", json={"name": "Secondo", "description": "Altro"}, headers=headers)
    response = await client.get("/items", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_list_items_pagination(client: AsyncClient):
    """Paginazione: limit e offset funzionano correttamente."""
    headers = await get_auth_headers(client)
    for i in range(5):
        await client.post("/items", json={"name": f"Item {i}", "description": "x"}, headers=headers)
    # Prima pagina: 2 elementi
    response = await client.get("/items?limit=2&offset=0", headers=headers)
    assert len(response.json()) == 2
    # Seconda pagina: altri 2 elementi
    response = await client.get("/items?limit=2&offset=2", headers=headers)
    assert len(response.json()) == 2


# ─── Test: dettaglio ──────────────────────────────────────────────────────────
async def test_get_item_success(client: AsyncClient):
    """Dettaglio item esistente → 200 con dati corretti."""
    headers = await get_auth_headers(client)
    created = await client.post("/items", json=ITEM, headers=headers)
    item_id = created.json()["id"]
    response = await client.get(f"/items/{item_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == item_id


async def test_get_item_not_found(client: AsyncClient):
    """Item inesistente → 404 Not Found."""
    headers = await get_auth_headers(client)
    response = await client.get("/items/9999", headers=headers)
    assert response.status_code == 404


# ─── Test: aggiornamento ──────────────────────────────────────────────────────
async def test_update_item_success(client: AsyncClient):
    """Aggiornamento parziale: solo name, description invariata."""
    headers = await get_auth_headers(client)
    created = await client.post("/items", json=ITEM, headers=headers)
    item_id = created.json()["id"]
    response = await client.put(
        f"/items/{item_id}",
        json={"name": "Nome aggiornato"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Nome aggiornato"
    # Description non deve cambiare
    assert response.json()["description"] == ITEM["description"]


async def test_update_item_not_found(client: AsyncClient):
    """Aggiornamento item inesistente → 404 Not Found."""
    headers = await get_auth_headers(client)
    response = await client.put("/items/9999", json={"name": "x"}, headers=headers)
    assert response.status_code == 404


# ─── Test: eliminazione ───────────────────────────────────────────────────────
async def test_delete_item_success(client: AsyncClient):
    """Eliminazione → 204, poi il GET restituisce 404."""
    headers = await get_auth_headers(client)
    created = await client.post("/items", json=ITEM, headers=headers)
    item_id = created.json()["id"]
    response = await client.delete(f"/items/{item_id}", headers=headers)
    assert response.status_code == 204
    # Verifica che l'item non esista più
    response = await client.get(f"/items/{item_id}", headers=headers)
    assert response.status_code == 404


async def test_delete_item_not_found(client: AsyncClient):
    """Eliminazione item inesistente → 404 Not Found."""
    headers = await get_auth_headers(client)
    response = await client.delete("/items/9999", headers=headers)
    assert response.status_code == 404


# ─── Test: isolamento tra utenti ─────────────────────────────────────────────
async def test_user_isolation(client: AsyncClient):
    """
    SICUREZZA: un utente non può accedere agli item di un altro.
    Questo è il test più importante — verifica che l'ownership funzioni.
    """
    user_a = {"email": "a@test.com", "password": "pass123"}
    user_b = {"email": "b@test.com", "password": "pass123"}

    # Registra e logga entrambi gli utenti
    await client.post("/auth/register", json=user_a)
    await client.post("/auth/register", json=user_b)
    token_a = (await client.post("/auth/login", json=user_a)).json()["access_token"]
    token_b = (await client.post("/auth/login", json=user_b)).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # L'utente A crea un item
    created = await client.post("/items", json=ITEM, headers=headers_a)
    item_id = created.json()["id"]

    # L'utente B non deve poter vedere l'item dell'utente A
    response = await client.get(f"/items/{item_id}", headers=headers_b)
    assert response.status_code == 404
