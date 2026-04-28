# dino-996-FastAPI

REST API for personal blog content management. Exposes public endpoints for reading articles and protected endpoints for creating, updating, and deleting content, accessible only to the administrator via JWT authentication.

## Tech Stack

- **Python** 3.12.x
- **FastAPI** + Uvicorn
- **SQLAlchemy** (async) + Supabase (PostgreSQL) + Alembic
- **Pydantic** v2 + pydantic-settings
- **JWT** (python-jose) + bcrypt (passlib)
- **pytest** + pytest-asyncio + in-memory SQLite for tests

---

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config.py         # Environment variables (.env)
│   │   ├── security.py       # bcrypt + JWT
│   │   └── dependencies.py   # get_db, get_current_user
│   ├── db/
│   │   ├── base.py           # SQLAlchemy Base
│   │   └── session.py        # Engine + SessionLocal
│   ├── models/
│   │   ├── user.py           # users table
│   │   └── article.py        # articles table
│   ├── schemas/
│   │   ├── user.py           # User schemas
│   │   ├── token.py          # Token schema
│   │   └── article.py        # Article schemas
│   ├── routers/
│   │   ├── auth.py           # Login, refresh, me
│   │   └── article.py        # Article CRUD
│   ├── tests/
│   │   ├── conftest.py       # pytest fixtures
│   │   ├── test_auth.py      # Authentication tests
│   │   └── test_articles.py  # Article tests
│   ├── create_admin.py       # Admin user creation script
│   └── main.py               # Entry point
├── alembic/
│   └── env.py                # Migrations configuration
├── .env.example              # Environment variables template
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── run.py                    # Start script
```

---

## Local Development

### 1. Virtual environment and dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env.example` to `.env` and fill in all values:

```powershell
copy .env.example .env
```

Generate a secure `SECRET_KEY` with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Database

Run the migrations against your Supabase database:

```powershell
alembic upgrade head
```

### 4. Admin user

```powershell
python -m app.create_admin
```

### 5. Start the server

```powershell
python run.py
```

Interactive API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

---

## Deploy on Render + Supabase

### Supabase — Database setup

1. Create a new project on [Supabase](https://supabase.com)
2. Go to **Project Settings → Database → Connection string**
3. Copy the **URI** connection string and replace `postgresql://` with `postgresql+asyncpg://`
4. Make sure the **Connection pooling** mode is set to **Session** (not Transaction), as Alembic requires a persistent connection for migrations

The resulting `DATABASE_URL` should look like this:

```
postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres?ssl=require
```

### Render — Web Service setup

Create a new **Web Service** on [Render](https://render.com) connected to this repository, then configure it as follows:

| Field | Value |
|-------|-------|
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:main --host 0.0.0.0 --port $PORT` |

### Environment variables

In the **Environment** section of the Render Web Service, add all variables from `.env.example`, including the `DATABASE_URL` obtained from Supabase.

### Migrations

Migrations are not run automatically on deploy. You can handle them in two ways:

**Option A — manually from the Render shell**, using the **Shell** tab of the Web Service:

```bash
alembic upgrade head
```

**Option B — automatically on every deploy**, by appending migrations to the build command:

```
pip install -r requirements.txt && alembic upgrade head
```

### Admin user

Once the deploy is complete and migrations have run, create the admin user from the Render shell:

```bash
python -m app.create_admin
```

---

## API Endpoints

### Authentication (`/auth`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/auth/login` | Login, returns access and refresh tokens | No |
| `POST` | `/auth/refresh` | Renews tokens using the refresh token | No |
| `GET` | `/auth/me` | Returns authenticated user data | Bearer token |

### Articles (`/articles`)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/articles` | List articles with pagination (`limit`, `offset`) | No |
| `GET` | `/articles/{id}` | Single article detail | No |
| `POST` | `/articles` | Create a new article | Bearer token (admin) |
| `PUT` | `/articles/{id}` | Update an existing article | Bearer token (admin) |
| `DELETE` | `/articles/{id}` | Delete an article | Bearer token (admin) |

### System

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |

---

## Useful Commands

```powershell
# Start development server
python run.py

# Create a new migration after modifying models
alembic revision --autogenerate -m "description"
alembic upgrade head

# Revert last migration
alembic downgrade -1

# Run tests
pytest app/tests/ -v

# Generate a SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```