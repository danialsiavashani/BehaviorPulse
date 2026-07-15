# Dev startup

## First time only — backend venv
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in JWT_SECRET_KEY

## First time only — Postgres DB + role
sudo su postgres -c "psql -c \"CREATE USER behaviorpulse WITH PASSWORD 'behaviorpulse';\""
sudo su postgres -c "psql -c \"CREATE DATABASE behaviorpulse OWNER behaviorpulse;\""

## Every session — start PostgreSQL (if not already running)
sudo service postgresql start
# if that hangs asking for a sudo password, use instead:
sudo su postgres -c "pg_ctlcluster 16 main start"
# check it's actually up:
pg_isready

## Terminal 1 — backend (FastAPI)
cd backend
source .venv/bin/activate && uvicorn app.main:app --reload
# → http://localhost:8000/health

## Terminal 2 — frontend (Next.js)
# not built yet