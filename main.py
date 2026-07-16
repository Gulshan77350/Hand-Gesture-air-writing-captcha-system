"""
Phase 1 - Backend API.

Endpoints:
  GET  /api/captcha        -> creates a new captcha, returns a session_id
                               and the PNG image (base64), stores the
                               plaintext answer server-side only.
  POST /api/verify         -> (temporary, for Phase 1 testing only —
                               Phase 6 will replace the "text" input
                               here with the transformer's prediction
                               from an air-writing trajectory)

Run locally with:
  uvicorn main:app --reload --port 8000
"""

import base64
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from captcha_gen import generate_captcha_text, generate_captcha_image

app = FastAPI(title="Air-Writing Captcha - Phase 1")

# Allow the frontend (served separately) to call this API during dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory session store -------------------------------------------
# Production should use Redis (or similar) instead of a process-local
# dict, so captcha state survives restarts and works across multiple
# backend instances.
SESSION_TTL_SECONDS = 120
MAX_ATTEMPTS = 3

_sessions: dict[str, dict] = {}


def _cleanup_expired():
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if s["expires_at"] < now]
    for sid in expired:
        del _sessions[sid]


class VerifyRequest(BaseModel):
    session_id: str
    text: str


@app.get("/api/captcha")
def get_captcha():
    _cleanup_expired()

    text = generate_captcha_text(length=5)
    image_bytes = generate_captcha_image(text)
    session_id = str(uuid.uuid4())

    _sessions[session_id] = {
        "answer": text,          # never sent to the client
        "expires_at": time.time() + SESSION_TTL_SECONDS,
        "attempts": 0,
        "verified": False,
    }

    return {
        "session_id": session_id,
        "image_base64": base64.b64encode(image_bytes).decode("ascii"),
        "expires_in": SESSION_TTL_SECONDS,
    }


@app.post("/api/verify")
def verify_captcha(req: VerifyRequest):
    """
    Phase 1 placeholder: accepts typed text directly.
    From Phase 6 onward, `text` will instead be the string produced
    server-side by running the transformer model on the submitted
    air-writing trajectory -- the client will never be trusted to
    self-report the recognized text.
    """
    _cleanup_expired()
    session = _sessions.get(req.session_id)

    if session is None:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    if session["verified"]:
        raise HTTPException(status_code=400, detail="Session already used")

    if session["attempts"] >= MAX_ATTEMPTS:
        del _sessions[req.session_id]
        raise HTTPException(status_code=429, detail="Too many attempts")

    session["attempts"] += 1

    is_match = req.text.strip().upper() == session["answer"].upper()

    if is_match:
        session["verified"] = True
        del _sessions[req.session_id]  # single-use
        return {"success": True}

    return {"success": False, "attempts_remaining": MAX_ATTEMPTS - session["attempts"]}


@app.get("/api/health")
def health():
    return {"status": "ok", "active_sessions": len(_sessions)}
