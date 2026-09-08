"""FastAPI HTTP surface for Aira Lift — API + phone-first SPA."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from aira_lift import service
from aira_lift.auth import (
    auth_disabled,
    google_configured,
    register_auth_routes,
    require_mutating,
    session_secret,
)
from aira_lift.seed import seed

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Aira Lift", version="0.1.0")
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret(),
    same_site="lax",
    https_only=False,
)

# Google OAuth (authlib) — only wired when credentials exist
oauth = None
if google_configured() and not auth_disabled():
    from authlib.integrations.starlette_client import OAuth

    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
register_auth_routes(app, oauth)


class SetIn(BaseModel):
    index: Optional[int] = None
    set_type: str = "normal"
    weight_kg: Optional[float] = None
    assistance_kg: Optional[float] = None
    reps: Optional[int] = None
    side: Optional[str] = None
    rpe: Optional[float] = None


class ExerciseIn(BaseModel):
    name: str
    notes: Optional[str] = None
    order_index: Optional[int] = None
    sets: list[SetIn] = Field(default_factory=list)


class SessionIn(BaseModel):
    date_ist: Optional[str] = None
    weekday: Optional[str] = None
    session_type: str
    status: str = "completed"
    duration_min: Optional[float] = None
    bodyweight_kg: Optional[float] = None
    notes_back: Optional[str] = None
    notes_neck: Optional[str] = None
    notes_form: Optional[str] = None
    plan_adherence: Optional[str] = None
    source: str = "api"
    title: Optional[str] = None
    exercises: list[ExerciseIn] = Field(default_factory=list)


class BodyweightIn(BaseModel):
    date_ist: Optional[str] = None
    bodyweight_kg: float


class StartWorkoutIn(BaseModel):
    session_type: str
    title: Optional[str] = None
    date_ist: Optional[str] = None
    source: str = "web"


class AddExerciseIn(BaseModel):
    name: str
    notes: Optional[str] = None
    order_index: Optional[int] = None


class AddSetIn(BaseModel):
    weight_kg: Optional[float] = None
    assistance_kg: Optional[float] = None
    reps: Optional[int] = None
    side: Optional[str] = None
    set_type: str = "normal"
    rpe: Optional[float] = None
    set_index: Optional[int] = None


class UpdateSetIn(BaseModel):
    weight_kg: Optional[float] = None
    assistance_kg: Optional[float] = None
    reps: Optional[int] = None
    side: Optional[str] = None
    set_type: Optional[str] = None
    rpe: Optional[float] = None


class FinishWorkoutIn(BaseModel):
    duration_min: Optional[float] = None
    status: str = "completed"


@app.on_event("startup")
def _startup() -> None:
    seed()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": "aira-lift",
        "auth_disabled": auth_disabled(),
        "google_configured": google_configured(),
    }


@app.post("/sessions")
def create_session(
    body: SessionIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        return service.append_session(body.model_dump(exclude_none=True))
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/sessions")
def get_sessions(
    limit: int = 10,
    session_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> list[dict[str, Any]]:
    return service.list_sessions(limit, session_type, date_from, date_to)


@app.get("/sessions/{session_id}")
def get_one(session_id: int) -> dict[str, Any]:
    try:
        return service.get_session(session_id)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.delete("/sessions/{session_id}")
def delete_one(
    session_id: int,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        return service.delete_session(session_id)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


# --- Live workout (Hevy-like) ---


@app.post("/workouts/start")
def start_workout(
    body: StartWorkoutIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        return service.start_workout(
            session_type=body.session_type,
            title=body.title,
            source=body.source or "web",
            date_ist=body.date_ist,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.post("/workouts/{session_id}/exercises")
def add_exercise(
    session_id: int,
    body: AddExerciseIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        return service.add_exercise_to_session(
            session_id, body.name, notes=body.notes, order_index=body.order_index
        )
    except KeyError as e:
        raise HTTPException(404, str(e)) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.post("/workouts/exercises/{session_exercise_id}/sets")
def add_set(
    session_exercise_id: int,
    body: AddSetIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        return service.add_set_to_exercise(
            session_exercise_id,
            weight_kg=body.weight_kg,
            assistance_kg=body.assistance_kg,
            reps=body.reps,
            side=body.side,
            set_type=body.set_type,
            rpe=body.rpe,
            set_index=body.set_index,
        )
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.patch("/workouts/sets/{set_id}")
def patch_set(
    set_id: int,
    body: UpdateSetIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    try:
        data = body.model_dump(exclude_unset=True)
        return service.update_set(set_id, **data)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.post("/workouts/{session_id}/finish")
def finish_workout(
    session_id: int,
    body: FinishWorkoutIn | None = None,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    body = body or FinishWorkoutIn()
    try:
        return service.finish_workout(
            session_id, duration_min=body.duration_min, status=body.status
        )
    except KeyError as e:
        raise HTTPException(404, str(e)) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/plan/active")
def plan() -> dict[str, Any]:
    return service.get_active_plan()


@app.get("/day-status")
def day_status(date_ist: Optional[str] = None) -> dict[str, Any]:
    return service.day_status(date_ist)


@app.get("/templates")
def templates(q: Optional[str] = None) -> list[dict[str, Any]]:
    rows = service.list_templates()
    if q:
        needle = q.lower().strip()
        rows = [r for r in rows if needle in (r.get("name") or "").lower()]
    return rows


@app.post("/bodyweight")
def post_bw(
    body: BodyweightIn,
    _user: dict = Depends(require_mutating),
) -> dict[str, Any]:
    return service.log_bodyweight(body.date_ist, body.bodyweight_kg)


@app.get("/bodyweight/latest")
def latest_bw() -> dict[str, Any]:
    row = service.get_latest_bodyweight()
    if not row:
        raise HTTPException(404, "no bodyweight logged")
    return row


@app.get("/missing-days")
def missing(lookback_days: int = 7) -> list[dict[str, Any]]:
    return service.list_missing_days(lookback_days)


# --- SPA ---


@app.get("/")
def spa_index() -> FileResponse:
    index = STATIC_DIR / "index.html"
    if not index.exists():
        raise HTTPException(404, "frontend not built")
    return FileResponse(index)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def main() -> None:
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8787"))
    uvicorn.run("aira_lift.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
