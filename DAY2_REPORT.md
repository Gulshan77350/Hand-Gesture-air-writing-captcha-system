# Day 2 Report — Air-Writing Captcha System

**Date:** July 20, 2026 (planned)
**Phase completed:** Phase 2 — Camera Access & Hand Landmark Tracking

## Objective
Get a live webcam feed running in the browser and confirm stable,
real-time detection of the 21 hand landmarks via MediaPipe, with a
clear read on the index fingertip position — the point that will act
as the "pen" for air-writing in later phases. No gesture logic or
trajectory capture yet; this phase is purely about proving the
tracking is reliable.

## Work completed

1. **`frontend/phase2_hand_tracking.html`**
   - Requests webcam access via `getUserMedia`.
   - Loads MediaPipe's `HandLandmarker` (Tasks Vision API) from CDN —
     no npm install / build step required, runs entirely client-side
     via WASM.
   - Runs detection per video frame (`runningMode: "VIDEO"`), draws the
     21-point hand skeleton and joint markers on a canvas overlay.
   - Highlights the index fingertip (landmark 8) distinctly and prints
     its live (x, y, z) normalized coordinates.
   - Mirrors the video/canvas (`scaleX(-1)`) so movement feels natural,
     like looking in a mirror, instead of reversed.
   - Start/Stop controls that properly release the camera stream on stop.

2. No backend changes needed this phase — the file is served
   automatically through the existing static mount in `main.py`.

## How to run it

With the Phase 1 backend already running:
```bash
uvicorn main:app --reload --port 8000
```
Open:
```
http://localhost:8000/static/phase2_hand_tracking.html
```
Click "Start camera," grant permission, and hold your hand in frame.

## What to check while testing

- Does the skeleton track smoothly, or does it jitter/lag noticeably?
- Does detection hold up in your actual lighting conditions (webcam
  angle, indoor light)?
- Does it recover quickly when the hand leaves and re-enters frame?
- Note fingertip coordinate stability when holding the hand still —
  small natural jitter is expected and will matter for gesture
  threshold tuning in Phase 3.

## Next steps (Phase 3)

- Design and implement pen-up/pen-down gesture detection (pinch
  distance between thumb tip and index tip) on top of this tracking.
- Add a visible trace overlay so the user can see what they're
  "writing" in the air.
- Tune thresholds/debounce so natural hand jitter doesn't cause false
  pen state toggles.
