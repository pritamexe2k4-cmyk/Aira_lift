# Aira Lift

Personal gym tracker for one user: **phone-first web UI** + **stdio MCP** (so Aira can log/read workouts in chat). Black/white Hevy-style logging. No Hevy Pro. No cloud SaaS.

## What this is

| Piece | Role |
| --- | --- |
| SQLite `data/aira_lift.db` | Single source of truth |
| FastAPI + static SPA | Web UI + API on `:8787` |
| stdio MCP | Agents (Aira) read/write the **same** DB |
| Google OAuth | Allowlisted to your Gmail |

```
You (browser) ──► FastAPI/UI ──► SQLite ◄── MCP ◄── Aira (chat)
```

Do **not** run two different DB files. Web and MCP must share one path.

## Features (MVP)

- Start workout → add exercises → log sets (weight / assistance_kg / reps / side / drop sets) → finish
- History + session detail
- Bodyweight log
- Seeded machine-focused catalogue (Indian commercial gym) + 6-day PPL plan
- MCP tools: `append_session`, `list_sessions`, `get_session`, `day_status`, `log_bodyweight`, `get_prs`, `delete_session`, …

See `SCHEMA.md` for tables and tool list.

## Quick start (Windows / macOS / Linux)

```bash
git clone https://github.com/pritamexe2k4-cmyk/Aira_lift.git
cd Aira_lift
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python scripts/init_db.py
cp .env.example .env   # then fill Google keys (or use AUTH_DISABLED for local smoke)
```

### Dev smoke (no Google)

```bash
AUTH_DISABLED=1 HOST=0.0.0.0 PORT=8787 aira-lift-api
```

Open http://127.0.0.1:8787/ → **Continue (dev)**.

### Real Google login

1. Google Cloud Console → OAuth client type **Web application**
2. JavaScript origins: `http://127.0.0.1:8787`, `http://localhost:8787`
3. Redirect URIs: `http://127.0.0.1:8787/auth/google/callback`, `http://localhost:8787/auth/google/callback`
4. Put Client ID/Secret in `.env` (see `.env.example`)
5. Add your Gmail under **OAuth consent screen → Test users**
6. Run **without** `AUTH_DISABLED`:

```bash
# loads from .env if you export them, or:
set -a && source .env && set +a   # bash
aira-lift-api
```

On Windows you can use `start-aira-lift.bat` after creating `.env` (local only — not in git).

## MCP (Aira / Cursor)

```bash
python -m aira_lift.mcp_server
```

Point your MCP config at that module and the same project directory so it opens `data/aira_lift.db`.

## Project layout

```
src/aira_lift/
  api.py          # FastAPI + SPA routes
  auth.py         # Google OAuth + allowlist
  service.py      # domain logic (shared by API + MCP)
  mcp_server.py   # stdio MCP tools
  db.py / seed.py
  static/         # phone UI (HTML/CSS/JS)
scripts/init_db.py
SCHEMA.md
```

## Security notes

- Never commit `.env` or `data/*.db`
- `AUTH_DISABLED=1` is local-only
- Single-user allowlist via `ALLOWED_EMAILS`

## Status

Working local MVP. UI polish and edits welcome — this repo is the source of truth for code.
