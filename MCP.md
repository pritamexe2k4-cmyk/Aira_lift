# Aira Lift — MCP store (how Aira logs)

This is the **data + MCP** half of Aira Lift. The phone UI can come later; Aira already logs through this path.

## Mental model

```
You (chat with Aira)
        │
        ▼
   Aira (fitness agent)
        │  calls MCP tools
        ▼
   stdio MCP server  ←  `python -m aira_lift.mcp_server`
   namespace in Grok Bot: `user-aira-lift`
        │
        ▼
   service.py  (validated writes — no freeform SQL)
        │
        ▼
   SQLite file: data/aira_lift.db
```

One database file. Chat logs and (optional) web UI both use it. Sources stay distinct: `aira_chat` vs `web`.

## Where it stores

| What | Where |
| --- | --- |
| DB file | `data/aira_lift.db` (gitignored) |
| On Spider’s computer (live MCP today) | `/workspace/aira-lift/data/aira_lift.db` |
| On your PC copy | `Desktop\aira-lift\data\aira_lift.db` |
| Schema | `SCHEMA.md` + `src/aira_lift/db.py` |

Tables: `exercise_templates`, `sessions`, `session_exercises`, `sets`, `body_measurements`, `app_meta` (active PPL plan JSON).

## How it stores (shape)

- **Session** = one training day (`date_ist`, `session_type`, `status`, notes, `source`, …)
- **Exercises** nested under session → reference a **template**
- **Sets** nested under exercise (`weight_kg` / `assistance_kg`, `reps`, `side`, `set_type`)
- **Bodyweight** = separate per-day upsert
- **PRs** = computed from history, not a primary table
- **skipped/rest** = session with **zero** exercises (enforced)

## How MCP links to Aira

1. Grok Bot runs a **stdio** MCP process pointed at this package:
   ```bash
   /workspace/aira-lift/.venv/bin/python -m aira_lift.mcp_server
   ```
2. That process exposes tools under connector namespace **`user-aira-lift`**.
3. When you tell Aira you trained, she calls tools such as:
   - `append_session` / `log_workout` — write a full session JSON
   - `list_sessions`, `get_session`, `get_last_n`
   - `get_exercise_history`, `get_prs`
   - `log_bodyweight`, `get_latest_bodyweight`
   - `get_active_plan` — 6-day PPL + prefs
   - `day_status`, `list_missing_days` — 9:00 / 20:00 nudges
   - `delete_session` — cleanup (if reloaded)
4. Tools call `service.py` → SQLite. Aira never sees raw SQL for writes.

## Run MCP only (no UI)

```bash
cd aira-lift   # or Aira_lift clone
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install -e .
python scripts/init_db.py
python -m aira_lift.mcp_server   # stdio — wire this in Cursor/Grok Bot MCP settings
```

## Brand note

Product name: **Aira Lift**. Client/web UI is optional and can be rebuilt later; **MCP + SQLite is the source of truth** for Aira’s logging.
