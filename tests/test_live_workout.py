import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aira_lift.seed import seed
from aira_lift import service

TEST_DB = ROOT / "data" / "test_live_workout.db"


def setup_module():
    if TEST_DB.exists():
        TEST_DB.unlink()
    seed(TEST_DB)


def test_start_add_finish_source_web():
    sess = service.start_workout("Push", title="Smoke", source="web", db_path=TEST_DB)
    assert sess["status"] == "partial"
    assert sess["source"] == "web"
    assert sess["exercises"] == []

    sess = service.add_exercise_to_session(sess["id"], "Chest press (machine)", db_path=TEST_DB)
    assert len(sess["exercises"]) == 1
    se_id = sess["exercises"][0]["id"]

    sess = service.add_set_to_exercise(
        se_id, weight_kg=40, reps=10, set_type="normal", db_path=TEST_DB
    )
    sess = service.add_set_to_exercise(
        se_id, weight_kg=35, reps=8, set_type="drop", db_path=TEST_DB
    )
    assert len(sess["exercises"][0]["sets"]) == 2
    assert sess["exercises"][0]["sets"][1]["set_type"] == "drop"

    set_id = sess["exercises"][0]["sets"][0]["id"]
    sess = service.update_set(set_id, weight_kg=42.5, db_path=TEST_DB)
    assert sess["exercises"][0]["sets"][0]["weight_kg"] == 42.5

    # assisted style
    sess = service.add_exercise_to_session(sess["id"], "Assisted dip", db_path=TEST_DB)
    dip_id = [e for e in sess["exercises"] if e["name"] == "Assisted dip"][0]["id"]
    sess = service.add_set_to_exercise(
        dip_id, assistance_kg=45, reps=12, db_path=TEST_DB
    )
    dip = [e for e in sess["exercises"] if e["name"] == "Assisted dip"][0]
    assert dip["sets"][0]["assistance_kg"] == 45

    done = service.finish_workout(sess["id"], duration_min=41, db_path=TEST_DB)
    assert done["status"] == "completed"
    assert done["duration_min"] == 41

    listed = service.list_sessions(limit=5, db_path=TEST_DB)
    row = next(r for r in listed if r["id"] == done["id"])
    assert row["source"] == "web"
    assert row["status"] == "completed"
