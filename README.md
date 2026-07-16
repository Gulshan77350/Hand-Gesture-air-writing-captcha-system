# Phase 1 — Captcha generation & frontend display

This phase builds the baseline captcha lifecycle with no hand tracking yet:
generate a distorted captcha image server-side, display it in the browser,
and verify a submitted answer. It's the scaffold that later phases plug
the camera / air-writing / transformer pipeline into.

## Structure

```
captcha_phase1/
├── backend/
│   ├── captcha_gen.py   # random text + distorted PNG generation
│   ├── main.py           # FastAPI app: /api/captcha, /api/verify, /api/health
│   └── requirements.txt
└── frontend/
    └── index.html         # displays captcha, "Enter CAPTCHA" button (typed placeholder)
```

## Run it

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open `frontend/index.html` directly in a browser (or serve it with
`python3 -m http.server 5500` from the `frontend/` folder).

## What's real vs placeholder in this phase

- **Real**: captcha text generation, image distortion (rotation, noise,
  jitter), session lifecycle (single-use, TTL, attempt limiting), the
  verify endpoint's matching logic.
- **Placeholder**: the "Enter CAPTCHA" flow currently accepts typed text.
  From Phase 3 onward this is replaced by the camera view + air-writing
  trace, and from Phase 6 onward `/api/verify` will receive a trajectory
  and run the transformer server-side instead of trusting client-submitted
  text directly.

## Notes for the next phase

- The answer string (`session["answer"]`) never leaves the backend —
  keep it that way as you build the trajectory/recognition pipeline.
- Swap the in-memory `_sessions` dict for Redis before this goes near
  production; it currently won't survive a restart or scale past one
  process.
