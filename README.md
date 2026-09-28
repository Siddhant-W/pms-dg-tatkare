<p align="center">
  <img src="frontend/public/assets/presento-logo.png" alt="Presento logo" width="420" />
</p>

<p align="center">
  <strong>Attendance marked. Proxies managed.</strong><br />
  A mobile-first PWA that runs the morning roll call for D.G. Tatkare Secondary &amp; Higher Secondary School —
  who's absent, who covers their periods, and who's free to do it.
</p>

---

## What it does

A school supervisor's morning starts with the same manual work every day: mark who's absent, cross-check
every affected period against the weekly timetable, find a free teacher for each one, and keep a record of
who covered what. Presento turns that into a five-screen loop:

- **Today** — a live dashboard: who's absent, how many periods still need coverage, and what's already resolved.
- **Attendance** — mark each teacher Present or Absent for the day, with a one-tap reset back to Not Marked if
  a status was set by mistake.
- **Timetable** — browse any teacher's weekly schedule by day; add new teachers and edit their periods directly
  (subject, class, free/recess, start and end time) without touching a spreadsheet.
- **Analytics** — attendance and proxy-load trends over time.
- **History** — a full audit log of every attendance change and proxy assignment, filterable by date or teacher.

The core engine is proxy assignment: when a teacher is marked absent, Presento cross-references their
timetable for that day, generates a coverage requirement for every affected period, and recommends an
eligible substitute — someone free that period, not already teaching, and not already covering something
else at the same time — ranked by how light their proxy load has been.

## Tech stack

**Frontend** — React 18 + TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, React Router. Ships as an
installable PWA (`vite-plugin-pwa`).

**Backend** — FastAPI (async), SQLAlchemy 2.0 + `asyncpg`, Postgres in production (SQLite for local dev),
Alembic for migrations. JWT access tokens held in memory, with an HttpOnly refresh cookie for silent
re-authentication — the access token is never touched by `localStorage`.

**Deployment** — frontend on Vercel, backend on Render, database on Neon Postgres. `frontend/vercel.json`
proxies `/api/*` server-side to the Render backend so the app works the same way in every Vercel environment
(production and every preview) without depending on per-environment variable scoping.

## Project structure

```
backend/
  app/
    api/routes/      REST endpoints (teachers, timetable, attendance, proxy, analytics, history)
    auth/             JWT issuing/verification, password hashing
    models/           SQLAlchemy models
    schemas/          Pydantic request/response schemas
    services/         Business logic (proxy assignment, attendance, availability, analytics)
    seeds/            Dev database seed script + the real school timetable data
    tests/            pytest suite
frontend/
  src/
    features/         One folder per screen (dashboard, attendance, timetable, analytics, history, auth, settings)
    components/ui/     Shared UI primitives (Button, Card, Modal, StatusPill, ...)
    services/          Typed API clients, one per resource
    styles/            Design tokens (tokens.css) and global styles
design.md               Design system: brand direction, color/type tokens, component and screen specs
PRESENTO_PRD.md          Product requirements document
RUNNING.md               Detailed local setup, auth flow internals, environment variables
render.yaml              Render blueprint for the backend service
```

## Quick start

```bash
# Backend (port 8000) - defaults to a local SQLite database, no setup needed
cd backend
pip install -e .
pip install pytest pytest-asyncio httpx
python -m app.seeds.seed        # idempotent - safe to re-run
python -m uvicorn app.main:app --reload --port 8000

# Frontend (port 5173), in a second terminal
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` and sign in with the seeded dev account (`Vaishali` / `Vaishali`). API docs are
served at `http://localhost:8000/docs`.

Full setup details — environment variables, how the auth session actually works, and known gaps — are in
[`RUNNING.md`](./RUNNING.md).

## Testing

```bash
cd backend && python -m pytest app/tests -q

cd frontend && npx tsc --noEmit && npm run build && npm run lint
```

## Design system

[`design.md`](./design.md) is the spec of record for Presento's visual language — navy/gold on a warm cream
canvas, Cinzel for headings, Manrope for body text — implemented as CSS custom properties in
`frontend/src/styles/tokens.css` and consumed through Tailwind's semantic color names, so no component
hardcodes a color value directly.
