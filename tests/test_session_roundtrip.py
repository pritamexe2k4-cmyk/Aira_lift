import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aira_lift.db import DEFAULT_DB
from aira_lift.seed import seed
from aira_lift import service

TEST_DB = ROOT / "data" / "test_aira_lift.db"

def setup_module():
    if TEST_DB.exists():
        TEST_DB.unlink()
    seed(TEST_DB)

def test_append_and_list():
    sess = service.append_session(
        {
            "session_type": "Push",
            "status": "completed",
            "source": "api",
            "exercises": [
                {
                    "name": "Chest press (machine)",
                    "sets": [{"weight_kg": 40, "reps": 10}, {"weight_kg": 42.5, "reps": 8}],
                }
            ],
        },
        db_path=TEST_DB,
    )
    assert sess["session_type"] == "Push"
    assert len(sess["exercises"]) == 1
    assert len(sess["exercises"][0]["sets"]) == 2
    listed = service.list_sessions(limit=5, db_path=TEST_DB)
    assert any(r["id"] == sess["id"] for r in listed)
    plan = service.get_active_plan(TEST_DB)
    assert plan["week"]["Mon"]["type"] == "Push"
