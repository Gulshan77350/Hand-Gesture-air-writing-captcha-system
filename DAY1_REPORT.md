# Day 1 Report — Air-Writing Captcha System

**Date:** July 19, 2026
**Phase completed:** Phase 1 — Captcha Generation & Frontend Display

## Objective
Build the baseline captcha lifecycle (generation → display → verification)
with no hand-tracking or ML yet, to serve as the scaffold that later
phases (camera input, gesture segmentation, transformer recognition)
will plug into.

## Work completed

1. **Captcha generation (`backend/captcha_gen.py`)**
   - Random 5-character alphanumeric string generator, excluding visually
     ambiguous characters (0/O, 1/I/l).
   - Distorted PNG rendering: per-character random rotation and vertical
     jitter, background line noise, dot noise, and smoothing filter to
     resist basic OCR while staying human-readable.

2. **Backend API (`backend/main.py`)** — built with FastAPI
   - `GET /api/captcha` — generates a captcha, creates a server-side
     session (UUID-keyed, TTL-based, in-memory store), returns the image
     as base64. The plaintext answer never leaves the server.
   - `POST /api/verify` — placeholder endpoint for Phase 1: accepts typed
     text, compares case-insensitively against the stored answer,
     enforces single-use sessions and a max-attempt limit (3).
   - `GET /api/health` — basic liveness check.
   - Frontend is served from the same FastAPI app/port (`/` route +
     static mount) to avoid cross-origin fetch issues during local dev.

3. **Frontend (`frontend/index.html`)**
   - Single-page UI displaying the captcha image inside a styled
     "scan-frame," a typed-text input as a temporary stand-in for the
     eventual air-writing input, an "Enter CAPTCHA" button, and a
     status line with clear success/error states.
   - Defensive error handling: if the backend is unreachable, the UI
     shows an explicit message instead of a silent blank state.

## Verification

- Ran the backend logic directly (session create → wrong attempt →
  correct attempt → cleanup) — confirmed correct match logic, attempt
  counting, and single-use session deletion.
- Ran the full stack locally via `uvicorn` and exercised the UI in the
  browser: captcha image renders correctly, "Enter CAPTCHA" against the
  correct text returns "✓ Verified!".

## Issues encountered & resolved

- Initial frontend was opened via `file://`, which silently failed to
  reach the backend on `localhost:8000` (no CORS/console visibility) —
  resolved by serving the frontend from the FastAPI app itself so both
  run on one origin.
- `pip install` timed out behind a slow institutional HTTP/SOCKS proxy
  (`172.31.2.4:8080`) — resolved by installing packages individually
  with an extended `--timeout`, which succeeded without needing to
  change the proxy configuration.

## Next steps (Phase 2)

- Integrate MediaPipe Hand Landmarker in the browser for real-time
  hand/fingertip tracking via webcam.
- Validate landmark tracking stability under varied lighting before
  building the gesture segmentation (pen up/down) logic on top of it.
