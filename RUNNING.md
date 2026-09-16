# Running the PMS (Phase 1)

## Login credentials

| Field | Value |
|---|---|
| Username | `Vaishali` |
| Password | `Vaishali` |

Seeded by `app/seeds/seed.py`. Change this before any real deployment.

---

## 1. Backend (port 8000)

```bash
cd backend

# Dependencies
pip install -e .            # or: pip install -r requirements.txt
pip install pytest pytest-asyncio httpx

# Environment: .env already exists and defaults to SQLite.
# cp .env.example .env      # only if .env is missing

# Seed the database (idempotent - safe to re-run)
python -m app.seeds.seed

# Start
python -m uvicorn app.main:app --reload --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Note on `passlib`

`passlib` is intentionally **no longer used**. It is unmaintained and crashes
against `bcrypt` 5.x. `app/auth/security.py` calls `bcrypt` directly. Existing
`$2b$` hashes remain valid, so no password reset is needed.

---

## 2. Frontend (port 5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

**Do not create a frontend `.env` unless you need it.** By default the client
calls the relative path `/api`, which the Vite dev proxy forwards to
`localhost:8000`. This keeps the app same-origin, so there is no CORS involved
and the HttpOnly refresh cookie works without special handling.

If you do point at a different host, `VITE_API_URL` **must include the `/api`
suffix**:

```
VITE_API_URL=http://localhost:8000/api
```

and that origin must be listed in the backend's `CORS_ORIGINS`.

---

## 3. Tests

```bash
cd backend
python -m pytest app/tests -q     # 18 tests
```

`app/tests/test_auth_flow.py` covers the authentication regressions:
password hashing, login success/failure, refresh rotation, token-type
separation, and logout.

---

## How the session works

1. **Login** → returns a short-lived access token (15 min, held in memory only)
   and sets an HttpOnly `refresh_token` cookie scoped to `/api/auth`.
2. **Page reload** → `App.tsx` calls `bootstrap()`, which silently hits
   `/api/auth/refresh`. `ProtectedRoute` shows a spinner while this is in
   flight, so an authenticated user is never bounced to `/login`.
3. **Access token expires mid-session** → the axios interceptor catches the
   401, refreshes once (concurrent 401s share one refresh), and retries the
   original request.
4. **Refresh fails** → the token is cleared and the store drops to
   `unauthenticated`, sending the user to `/login`.
5. **Logout** → calls `POST /api/auth/logout` so the server clears the refresh
   cookie. Clearing local state alone would let the next reload silently sign
   the user back in.

The access token is deliberately **not** persisted to `localStorage`, which is
why the silent-refresh bootstrap exists.

---

## Environment variables (backend `.env`)

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./pms.db` | Swap for `postgresql+asyncpg://...` in production |
| `SECRET_KEY` | dev value | **Must** be replaced in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | |
| `ENVIRONMENT` | `development` | Set to `production` to force `Secure` + `SameSite=None` cookies (requires HTTPS) |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated. Must be explicit; `*` is invalid with credentials |

---

## Known gap

Login rate limiting (Milestone 1.3: 5 attempts/min/IP) is **not implemented**.
`slowapi` is already a declared dependency. This was left out deliberately so
it would not interfere with manual testing.
