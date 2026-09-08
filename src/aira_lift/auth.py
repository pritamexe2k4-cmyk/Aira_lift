"""Google OAuth + session cookies for the Aira Lift web UI.

Env:
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET  — Google OAuth client
  SESSION_SECRET                         — cookie signing key (required when auth on)
  ALLOWED_EMAILS                         — comma-separated allowlist (default Preetam)
  BASE_URL                               — public origin, default http://127.0.0.1:8787
  AUTH_DISABLED=1                        — bypass OAuth for local smoke tests
                                           (sets a fake session user; NEVER use in prod)
"""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import HTTPException, Request
from starlette.responses import RedirectResponse

ALLOWED_DEFAULT = "pritam.exe2k4@gmail.com"


def auth_disabled() -> bool:
    return os.environ.get("AUTH_DISABLED", "").strip() in {"1", "true", "True", "yes", "YES"}


def allowed_emails() -> set[str]:
    raw = os.environ.get("ALLOWED_EMAILS", ALLOWED_DEFAULT)
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def base_url() -> str:
    return os.environ.get("BASE_URL", "http://127.0.0.1:8787").rstrip("/")


def session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-insecure-session-secret-change-me")


def google_configured() -> bool:
    return bool(os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"))


def current_user(request: Request) -> Optional[dict[str, Any]]:
    """Return the logged-in user dict from the session, or a fake user if AUTH_DISABLED."""
    if auth_disabled():
        return {
            "email": next(iter(allowed_emails())),
            "name": "Dev User",
            "picture": None,
            "auth_disabled": True,
        }
    user = request.session.get("user")
    if not user:
        return None
    return user


def require_user(request: Request) -> dict[str, Any]:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="not authenticated")
    return user


def require_mutating(request: Request) -> dict[str, Any]:
    """Protect POST/PATCH/DELETE when auth is enabled. No-op under AUTH_DISABLED."""
    return require_user(request)


def register_auth_routes(app, oauth) -> None:
    """Attach /auth/google, /auth/google/callback, /auth/logout, /auth/me."""

    @app.get("/auth/me")
    def auth_me(request: Request) -> dict[str, Any]:
        user = current_user(request)
        return {
            "authenticated": user is not None,
            "auth_disabled": auth_disabled(),
            "google_configured": google_configured(),
            "user": user,
        }

    @app.get("/auth/google")
    async def login_google(request: Request):
        if auth_disabled():
            return RedirectResponse("/")
        if not google_configured():
            raise HTTPException(
                503,
                "Google OAuth not configured. Set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET "
                "or use AUTH_DISABLED=1 for local smoke.",
            )
        redirect_uri = f"{base_url()}/auth/google/callback"
        return await oauth.google.authorize_redirect(request, redirect_uri)

    @app.get("/auth/google/callback")
    async def auth_callback(request: Request):
        if auth_disabled():
            return RedirectResponse("/")
        if not google_configured():
            raise HTTPException(503, "Google OAuth not configured")
        token = await oauth.google.authorize_access_token(request)
        info = token.get("userinfo")
        if not info:
            # authlib usually populates userinfo; fall back to userinfo endpoint
            resp = await oauth.google.get("userinfo", token=token)
            info = resp.json()
        email = (info.get("email") or "").lower()
        if email not in allowed_emails():
            request.session.clear()
            raise HTTPException(403, f"email {email} not allowlisted")
        request.session["user"] = {
            "email": email,
            "name": info.get("name"),
            "picture": info.get("picture"),
        }
        return RedirectResponse("/")

    @app.post("/auth/logout")
    @app.get("/auth/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/", status_code=303)
