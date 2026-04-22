# FastAPI Template

Template riutilizzabile per API REST con autenticazione JWT e CRUD.

## Stack
- Python 3.12.x
- FastAPI + Uvicorn
- SQLAlchemy (async) + PostgreSQL + Alembic
- Pydantic v2 + pydantic-settings
- JWT (python-jose) + bcrypt (passlib)
- pytest + pytest-asyncio + SQLite in memoria per i test

---

## Checklist per ogni nuovo progetto

### 1. Setup iniziale
- [ ] Copia questa cartella e rinominala
- [ ] `python -m venv .venv && .venv\Scripts\Activate.ps1`
- [ ] `pip install -r requirements.txt`
- [ ] Copia `.env.example` in `.env` e compila i valori
- [ ] Genera SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Crea DB e utente PostgreSQL

### 2. Personalizza la risorsa principale
- [ ] Rinomina `app/models/item.py` → es. `book.py`
- [ ] Rinomina la classe `Item` → es. `Book`
- [ ] Aggiorna `__tablename__` → es. `"books"`
- [ ] Modifica i campi del modello (name, description → title, author, isbn...)
- [ ] Aggiorna la relazione in `app/models/user.py` (items → books)
- [ ] Rinomina `app/schemas/item.py` → es. `book.py`
- [ ] Aggiorna gli schemi (ItemCreate, ItemUpdate, ItemResponse → BookCreate...)
- [ ] Rinomina `app/routers/items.py` → es. `books.py`
- [ ] Aggiorna prefix e tag del router (`/items` → `/books`)
- [ ] Aggiorna gli import in `app/main.py`
- [ ] Aggiorna gli import in `alembic/env.py`
- [ ] Aggiorna gli import in `app/tests/conftest.py`
- [ ] Rinomina e aggiorna `app/tests/test_items.py`

### 3. Migrazioni e avvio
- [ ] `alembic init alembic` (se non già fatto)
- [ ] `alembic revision --autogenerate -m "initial"`
- [ ] `alembic upgrade head`
- [ ] `python run.py`
- [ ] Apri http://127.0.0.1:8000/docs

### 4. Test
- [ ] `pytest app/tests/ -v`
- [ ] Tutti i test devono essere verdi prima del deploy

---

## Struttura del progetto

```
├── app/
│   ├── core/
│   │   ├── config.py       # Variabili d'ambiente (.env)
│   │   ├── security.py     # bcrypt + JWT
│   │   └── dependencies.py # get_db, get_current_user
│   ├── db/
│   │   ├── base.py         # Base SQLAlchemy
│   │   └── session.py      # Engine + SessionLocal
│   ├── models/
│   │   ├── user.py         # Tabella users (NON modificare)
│   │   └── item.py         # ← Rinomina con la tua risorsa
│   ├── schemas/
│   │   ├── user.py         # Schemi utente (NON modificare)
│   │   ├── token.py        # Schema token (NON modificare)
│   │   └── item.py         # ← Rinomina con la tua risorsa
│   ├── routers/
│   │   ├── auth.py         # Login, register, refresh, me (NON modificare)
│   │   └── items.py        # ← Rinomina con la tua risorsa
│   ├── tests/
│   │   ├── conftest.py     # Fixture pytest (aggiorna import modelli)
│   │   ├── test_auth.py    # Test autenticazione (NON modificare)
│   │   └── test_items.py   # ← Rinomina con la tua risorsa
│   └── main.py             # Entry point
├── alembic/
│   └── env.py              # Configurazione migrazioni
├── .env.example            # Template variabili d'ambiente
├── pytest.ini
├── requirements.txt
└── run.py                  # Script di avvio
```

---

## Comandi utili

```powershell
# Avvio server
python run.py

# Nuova migrazione dopo aver modificato i modelli
alembic revision --autogenerate -m "descrizione"
alembic upgrade head

# Annulla ultima migrazione
alembic downgrade -1

# Test
pytest app/tests/ -v

# Genera SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```
 
---

## Note

Fastapi -> framework per la creazione di API
Uvicorn -> server web in locale
Pydantic -> struttura lo schema dei dati (template pydantic) 
Swagger -> documentazione API interattiva
