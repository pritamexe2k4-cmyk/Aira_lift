# Aira Lift

Personal gym tracker for one user: **SQLite store** + **FastAPI / phone web UI** + **stdio MCP** so an agent (Aira) can log and read workouts in chat.

Local-first. No Hevy Pro. No cloud SaaS.

## What / Why

One database is the source of truth. Browser and MCP both talk to the same SQLite file — no split stores.

```
You (browser) ──► FastAPI / UI ──► SQLite ◄── MCP ◄── Aira (chat)
```

## Features

- Start workout → add exercises → log sets (weight / assistance_kg / reps / side / drop sets) → finish
- History and session detail
- Bodyweight log
- Seeded machine-focused catalogue (Indian commercial gym) + 6-day PPL plan
- MCP tools: `append_session`, `list_sessions`, `get_session`, `day_status`, `log_bodyweight`, `get_prs`, …

See [SCHEMA.md](SCHEMA.md) and [MCP.md](MCP.md) when present in the tree.

## Stack

Python 3.11+ · FastAPI · Uvicorn · Pydantic · MCP · SQLite · Authlib (Google OAuth, allowlisted)

## Getting started

```bash
git clone https://github.com/pritamexe2k4-cmyk/Aira_lift.git
cd Aira_lift
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python scripts/init_db.py
cp .env.example .env
```

### Dev smoke (no Google)

```bash
AUTH_DISABLED=1 HOST=0.0.0.0 PORT=8787 aira-lift-api
```

Open http://127.0.0.1:8787/ → Continue (dev).

### MCP

```bash
python -m aira_lift.mcp_server
# or: aira-lift-mcp
```

Point MCP config at this project so it opens `data/aira_lift.db`.

## Project layout

```
src/aira_lift/
  api.py          # FastAPI + SPA routes
  auth.py         # Google OAuth + allowlist
  service.py      # domain logic (API + MCP)
  mcp_server.py   # stdio MCP tools
  db.py / seed.py
  static/         # phone UI
scripts/init_db.py
data/             # local SQLite (gitignored)
```

## Status

Local MVP (MCP + API + SQLite) is the working source of truth. This remote is the intended public home for that codebase; clone/install steps assume the Python package tree is present.

## Security

- Never commit `.env` or `data/*.db`
- `AUTH_DISABLED=1` is local-only
- Single-user allowlist via `ALLOWED_EMAILS`

## License

None yet.
