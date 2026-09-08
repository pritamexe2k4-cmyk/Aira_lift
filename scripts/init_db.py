#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aira_lift.db import init_db
from aira_lift.seed import seed

if __name__ == "__main__":
    path = init_db()
    seed()
    print("Initialized", path)
