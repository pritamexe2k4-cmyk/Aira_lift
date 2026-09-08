
"""SQLite access for Aira Lift."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator, Optional

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "aira_lift.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS exercise_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  primary_muscle TEXT,
  exercise_type TEXT NOT NULL DEFAULT 'weight_reps',
  equipment_hint TEXT,
  is_custom INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date_ist TEXT NOT NULL,
  weekday TEXT NOT NULL,
  session_type TEXT NOT NULL,
  status TEXT NOT NULL,
  duration_min REAL,
  bodyweight_kg REAL,
  notes_back TEXT,
  notes_neck TEXT,
  notes_form TEXT,
  plan_adherence TEXT,
  source TEXT NOT NULL DEFAULT 'api',
  title TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_exercises (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  template_id INTEGER NOT NULL REFERENCES exercise_templates(id),
  order_index INTEGER NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS sets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_exercise_id INTEGER NOT NULL REFERENCES session_exercises(id) ON DELETE CASCADE,
  set_index INTEGER NOT NULL,
  set_type TEXT NOT NULL DEFAULT 'normal',
  weight_kg REAL,
  assistance_kg REAL,
  reps INTEGER,
  side TEXT,
  rpe REAL
);

CREATE TABLE IF NOT EXISTS body_measurements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date_ist TEXT NOT NULL UNIQUE,
  bodyweight_kg REAL NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS app_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""

def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = Path(db_path or DEFAULT_DB)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> Path:
    path = Path(db_path or DEFAULT_DB)
    with connect(path) as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


@contextmanager
def db_session(db_path: Path | None = None) -> Iterator[sqlite3.Connection]:
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)
