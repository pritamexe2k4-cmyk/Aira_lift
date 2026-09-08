# Aira Lift

**Brand focus right now: MCP + SQLite store** (Aira logs workouts here). Phone/client UI can be rebuilt later — see [`MCP.md`](./MCP.md) for how Aira connects.

Personal gym tracker for one user: **stdio MCP** (Aira) + optional web UI later. No Hevy Pro. No cloud SaaS.

## What this is

| Piece | Role |
| --- | --- |
| SQLite `data/aira_lift.db` | Single source of truth |
| stdio MCP (`user-aira-lift`) | Aira read/write workouts in chat |
| FastAPI + static SPA | Optional phone UI on `:8787` |
| Google OAuth | Allowlisted to your Gmail (UI only) |

```
You ↔ Aira (chat) → MCP tools → service.py → SQLite
                         ↑
              optional web UI (source=web)
```

Do **not** run two different DB files.

## MCP-only quick start

```bash
git clone https://github.com/pritamexe2k4-cmyk/Aira_lift.git
cd Aira_lift
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python scripts/init_db.py
python -m aira_lift.mcp_server
```

Wire that command as a **stdio MCP** in Grok Bot / Cursor. Details: **[MCP.md](./MCP.md)**. Schema: **[SCHEMA.md](./SCHEMA.md)**.

## Optional web UI

```bash
AUTH_DISABLED=1 HOST=0.0.0.0 PORT=8787 aira-lift-api
# http://127.0.0.1:8787/
```

Google OAuth: see `.env.example`.

## Status

MCP store is the product core. Client UI is secondary and can be redesigned later.
