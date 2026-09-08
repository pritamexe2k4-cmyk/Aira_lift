"""stdio MCP server for Aira Lift — tools Aira needs."""
from __future__ import annotations

import json
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from aira_lift import service
from aira_lift.seed import seed

seed()
mcp = FastMCP("aira-lift")


@mcp.tool()
def append_session(payload_json: str) -> str:
    """Log one workout session. Pass a JSON object with session_type, status, exercises[], etc."""
    payload = json.loads(payload_json)
    payload.setdefault("source", "mcp_client")
    return json.dumps(service.append_session(payload), indent=2)


@mcp.tool()
def log_workout(payload_json: str) -> str:
    """Alias of append_session (Researchy brief name)."""
    return append_session(payload_json)


@mcp.tool()
def list_sessions(
    limit: int = 10,
    session_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """List recent sessions (optional filters)."""
    return json.dumps(service.list_sessions(limit, session_type, date_from, date_to), indent=2)


@mcp.tool()
def get_session(session_id: int) -> str:
    """Get one session with exercises and sets."""
    return json.dumps(service.get_session(session_id), indent=2)


@mcp.tool()
def get_active_plan() -> str:
    """Return current PPL map + exercise prefs."""
    return json.dumps(service.get_active_plan(), indent=2)


@mcp.tool()
def log_bodyweight(bodyweight_kg: float, date_ist: Optional[str] = None) -> str:
    """Log bodyweight for a date (IST YYYY-MM-DD)."""
    return json.dumps(service.log_bodyweight(date_ist, bodyweight_kg), indent=2)


@mcp.tool()
def get_latest_bodyweight() -> str:
    """Latest bodyweight entry."""
    row = service.get_latest_bodyweight()
    return json.dumps(row or {}, indent=2)


@mcp.tool()
def list_missing_days(lookback_days: int = 7) -> str:
    """Plan days in lookback with no session (for forgot-nudge)."""
    return json.dumps(service.list_missing_days(lookback_days), indent=2)


@mcp.tool()
def day_status(date_ist: Optional[str] = None) -> str:
    """Did he log this IST day? For 20:00 forgot nudge."""
    return json.dumps(service.day_status(date_ist), indent=2)


@mcp.tool()
def get_last_n(n: int = 5) -> str:
    """Recent workouts summary."""
    return json.dumps(service.get_last_n(n), indent=2)


@mcp.tool()
def get_exercise_history(
    name: Optional[str] = None,
    template_id: Optional[int] = None,
    limit: int = 20,
) -> str:
    """History of sets for one exercise (name or template_id)."""
    return json.dumps(
        service.get_exercise_history(name=name, template_id=template_id, limit=limit),
        indent=2,
    )


@mcp.tool()
def get_prs() -> str:
    """Derived PRs (max weight + e1RM) per exercise — not a stored table."""
    return json.dumps(service.get_prs(), indent=2)


@mcp.tool()
def delete_session(session_id: int) -> str:
    """Delete one session (and nested sets). Use for smoke/typo cleanup."""
    return json.dumps(service.delete_session(session_id), indent=2)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
