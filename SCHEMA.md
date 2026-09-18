# Aira Lift — schema & MCP

Personal gym tracker for Preetam (1-user). Agents (Aira) read/write via **stdio MCP**. Notion Gym stays an optional mirror later. Job hunt + Brum stay P0 — keep this tiny.

Hevy-shaped nested model (single-tenant log). Ref shape: ExerciseTemplate → Workout/Session → Exercise → Set; BodyMeasurement separate; **PRs derived**, not stored day-1.

## Tables

### `exercise_templates`
Catalogue (name, primary_muscle, type weight_reps|duration|distance, equipment_hint, `is_custom`). Seeded ~30 machine-focused lifts for Indian commercial/society gyms + athletic-hybrid PPL. Lat+row combo machines still log as separate templates (Lat pulldown vs Seated row).

### `sessions` (Workout)
Dated session: `date_ist`, `weekday`, `session_type` (Push|Pull|Legs+Abs|Walk|Rest|Other), `status`, optional duration/bodyweight/title, notes (`notes_back`, `notes_neck`, `notes_form`), `source`.

**`source` values:** `api` · `mcp_client` · **`web`** (phone UI live logging) · others as needed.

### `session_exercises` → `sets`
Ordered exercises referencing `template_id` + notes. Sets: `set_index`, `set_type` (normal/warmup/drop/failure), `weight_kg` (**0 OK** for bare cable / negligible load), `reps`, optional `rpe`/`side`/`assistance_kg`.

**Assisted machines:** `assistance_kg` is the assist counterweight — **higher = easier** (e.g. assisted dip 45 kg assist). Prefer `assistance_kg` over stuffing assist into `weight_kg`.

**Template match:** append resolves exact name, then light fuzzy (e.g. “Incline machine chest press” → `Incline chest press (machine)`); else creates `is_custom` template.

### `body_measurements`
Date → `bodyweight_kg` (unique per day).

### `app_meta.active_plan`
JSON: 6-day PPL + prefs (routines as plan, not timed workouts).

## Live workout APIs (web / Hevy-like)

Used by the phone SPA; same SQLite as MCP.

| HTTP | Service | Purpose |
| --- | --- | --- |
| `POST /workouts/start` | `start_workout` | Create session `status=partial`, default `source=web` |
| `POST /workouts/{id}/exercises` | `add_exercise_to_session` | Append exercise (template resolve) |
| `POST /workouts/exercises/{se_id}/sets` | `add_set_to_exercise` | Log one set (weight / assistance_kg / reps / side / set_type) |
| `PATCH /workouts/sets/{set_id}` | `update_set` | Edit a set |
| `POST /workouts/{id}/finish` | `finish_workout` | `status=completed` + optional `duration_min` |

Batch create remains: `POST /sessions` → `append_session`.

Auth: Google OAuth session cookies; mutating routes require login unless `AUTH_DISABLED=1`.

## MCP tools (stdio only — no network bind)
| Tool | Purpose |
| --- | --- |
| `append_session` / `log_workout` | Create session + exercises + sets |
| `list_sessions` | Last N / date filters |
| `get_last_n` | Recent workouts summary |
| `get_session` | Full detail |
| `get_exercise_history` | By template id/name |
| `get_active_plan` / routines stub | PPL map + prefs |
| `log_bodyweight` | date + kg |
| `get_latest_bodyweight` | Latest kg |
| `get_prs` | Computed max weight / e1RM |
| `day_status` | Logged today? (20:00 nudge) |
| `list_missing_days` | Forgot-nudge helper |
| `delete_session` | Remove one session (smoke/typo cleanup) |

No freeform SQL writes. DB file mode `0600`; never commit `data/*.db` / `.env`.

## Explicitly out of MVP
Mobile native · social · Postgres · Hevy Pro sync · Next.js day-1 · fancy charts · Notion as source of truth
