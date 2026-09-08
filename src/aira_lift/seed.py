"""Seed exercise templates + active PPL plan prefs."""
from __future__ import annotations

import json
from pathlib import Path

from aira_lift.db import db_session, init_db

TEMPLATES = [
    # Push
    ("Chest press (machine)", "chest", "weight_reps", "machine"),
    ("Incline chest press (machine)", "chest", "weight_reps", "machine"),
    ("Pec deck / chest fly (machine)", "chest", "weight_reps", "machine"),
    ("Cable fly (mid)", "chest", "weight_reps", "cable"),
    ("Cable crossover / functional trainer", "chest", "weight_reps", "cable"),
    ("Shoulder press (machine/DB)", "shoulders", "weight_reps", "machine"),
    ("Cable lateral raise", "shoulders", "weight_reps", "cable"),
    ("Triceps pushdown", "triceps", "weight_reps", "cable"),
    ("Assisted dip", "chest", "weight_reps", "machine"),
    # Pull — lat+row combo floors still use separate templates for clean history
    ("Lat pulldown", "back", "weight_reps", "machine"),
    ("Single-arm cable lat pulldown", "back", "weight_reps", "cable"),
    ("Seated row", "back", "weight_reps", "machine"),
    ("Chest-supported row", "back", "weight_reps", "machine"),
    ("Assisted pull-up", "back", "weight_reps", "machine"),
    ("Face pull / rear delt", "rear_delts", "weight_reps", "cable"),
    ("Biceps curl (cable/DB)", "biceps", "weight_reps", "cable"),
    ("Biceps curl (machine)", "biceps", "weight_reps", "machine"),
    ("Back extension (hyper)", "lower_back", "weight_reps", "machine"),
    # Legs + abs / hip / calves (machines-first)
    ("Leg press", "quads", "weight_reps", "machine"),
    ("Hack squat", "quads", "weight_reps", "machine"),
    ("Leg curl", "hamstrings", "weight_reps", "machine"),
    ("Leg curl (seated/lying)", "hamstrings", "weight_reps", "machine"),
    ("Leg extension", "quads", "weight_reps", "machine"),
    ("Calf raise (seated/standing)", "calves", "weight_reps", "machine"),
    ("Hip abduction", "glutes", "weight_reps", "machine"),
    ("Hip adduction", "adductors", "weight_reps", "machine"),
    ("Glute bridge", "glutes", "weight_reps", "bodyweight"),
    ("Ab crunch (machine)", "core", "weight_reps", "machine"),
    ("Dead bug", "core", "weight_reps", "bodyweight"),
    ("Bird-dog", "core", "weight_reps", "bodyweight"),
    ("Side plank (knees)", "core", "duration", "bodyweight"),
    ("Wall angels", "posture", "weight_reps", "bodyweight"),
    # Walk days: one light cardio template only (no elliptical/treadmill catalogue)
    ("Zone-2 walk", "cardio", "duration", "outdoor_or_treadmill"),
]

ACTIVE_PLAN = {
    "name": "6-day PPL (locked 7 Sep 2026)",
    "timezone": "Asia/Kolkata",
    "sets_per_slot": 2,
    "week": {
        "Mon": {"type": "Push", "slots": 14},
        "Tue": {"type": "Pull", "slots": 12},
        "Wed": {"type": "Legs+Abs", "slots": 8},
        "Thu": {"type": "Push", "slots": 14},
        "Fri": {"type": "Pull", "slots": 12},
        "Sat": {"type": "Legs+Abs", "slots": 8},
        "Sun": {"type": "Rest", "slots": 0},
    },
    "prefs": {
        "pull": ["single-arm cable lat", "row only"],
        "push_mid": "cable fly",
        "legs": "machines only",
        "constraints": ["back-safe", "neck/head flare notes"],
    },
}


def seed(db_path: Path | None = None) -> None:
    init_db(db_path)
    with db_session(db_path) as conn:
        for name, muscle, etype, equip in TEMPLATES:
            conn.execute(
                """
                INSERT OR IGNORE INTO exercise_templates
                (name, primary_muscle, exercise_type, equipment_hint, is_custom)
                VALUES (?, ?, ?, ?, 0)
                """,
                (name, muscle, etype, equip),
            )
        conn.execute(
            """
            INSERT INTO app_meta(key, value) VALUES('active_plan', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (json.dumps(ACTIVE_PLAN),),
        )


if __name__ == "__main__":
    seed()
    print("Seeded templates + active plan ->", init_db())
