# BehaviorPulse

Behavioral analytics API platform for computer-vision and detection pipelines — cameras, sensors, or models that produce timestamped "I detected X, from this source, with this confidence" records.

## The idea

Consumer apps with a detection pipeline (wildlife cameras, traffic cameras, security systems, field sensors) send structured observation data to BehaviorPulse. The backend computes deterministic analytics — frequency patterns, time-of-day trends, recurring-day detection, confidence scoring — using pandas/numpy. Only after every fact is already computed does an LLM step in, and its only job is to explain those facts in plain English.

The LLM never sees raw observation data, never counts anything, never invents a metric or a confidence score. It receives a compact, pre-computed evidence packet it's contractually forbidden from contradicting. Most "AI-powered analytics" tools let a model eyeball raw data and guess — this one structurally can't.

```
Consumer app's CV/detection pipeline
  → normalizes rows into BehaviorPulse's JSON format
  → BehaviorPulse authenticates the request
  → computes metrics with pandas/numpy
  → sends only the computed facts to an LLM
  → LLM writes explanation/recommendation only
  → returns structured JSON (summary, prediction, pattern table, confidence)
```

## Core endpoint

`POST /v1/observations/analyze` accepts a mixed batch of observations — any number of distinct subjects in one call (all animal species a backyard camera saw, every vehicle type a traffic camera logged) — and returns:

- Frequency breakdown by subject and by source
- Day-of-week and time-of-day pattern detection
- A recurring-pattern check via real calendar math (e.g. "4 of the last 5 Wednesdays")
- A plain-English summary, a cautious prediction, and a computed confidence score
- Recommendations, always paired with an explicit "not a guarantee" warning

## Auth & security

Beyond the API layer, the dashboard runs a full session-security system, not a bare JWT:

- **Rotating refresh tokens** — every refresh issues a new token and permanently kills the old one
- **Reuse detection with a grace period** — replaying an already-rotated token outside a short grace window is treated as a theft signal and revokes every session for that user; replays *within* the window (two tabs, a double-navigation) are correctly treated as a benign race, not an attack
- **Instant revocation via token versioning** — changing your password or email kills every other active session immediately, without waiting for a token to naturally expire
- **Cascading, transactional deletes** — deleting an app or an account removes every dependent row (API keys, logs, analyses, scopes) in one transaction, explicitly, not via invisible DB-level cascade

## Tech stack

**Backend:** FastAPI, PostgreSQL, SQLAlchemy 2.x, Alembic, Pydantic, pandas/numpy, pytest

**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS v4, shadcn/ui, React Hook Form + Zod

**LLM:** DeepSeek, behind a provider-agnostic interface with a deterministic no-network fallback

**Auth:** JWT access tokens + rotating refresh tokens, both httpOnly cookies, silently refreshed via Next.js middleware

## Key design decisions

- **Domain-blind by design** — the platform has no fixed list of valid subjects and no filtering logic. It computes patterns on whatever batch of `{observed_at, subject, source, confidence}` records arrives. Deciding *what* to send is entirely the consuming application's job.
- **Generic schema, domain-specific detail lives in `metadata`** — top-level fields (`subject`, `source`, `observations`) stay generic across wildlife, vehicles, security, or field-sensor use cases; species names, camera-ID conventions, etc. live inside a free-form `metadata` object, never as top-level fields.
- **Provider-swappable by construction** — both the LLM client and the email client sit behind a small interface + factory, each with a safe fallback when unconfigured, so swapping providers later means adding one file, not touching any calling code.

## Local development

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

See `DEV.md` for full environment setup, including required `.env` variables.

## Project structure

```
backend/
  app/
    api/routes/       # FastAPI route handlers
    services/
      analytics/       # pandas/numpy analytics engine
      llm/              # provider-agnostic LLM client + factory
      email/             # provider-agnostic email client + factory
    db/models/          # SQLAlchemy models
  alembic/               # migrations
  tests/                  # pytest suite

frontend/
  src/
    app/                  # Next.js App Router pages
    components/            # UI components, organized by feature
    lib/                    # server actions, API client
    proxy.ts                 # silent token-refresh middleware
```

---

*Built as a solo project. Backend-first, tested at every layer — pytest coverage on the analytics engine, the auth system, and every route; hand-verified end-to-end against real API keys and a real LLM provider.*