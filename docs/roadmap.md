# Roadmap

Phased plan. Each phase is shippable on its own.

## Phase 1 — Detection upgrade (2–3 weeks)

- **Frame sampling**: replace "first 10 frames" with stratified sampling across the full video duration.
- **Temporal coherence head**: lightweight LSTM or attention over frame-level features to model frame-to-frame consistency — currently the strongest deepfake signal we ignore.
- **Audio path**: add a second model for audio-only deepfakes (lip-sync mismatch detection via Wav2Vec embeddings).
- **Real artifact localization**: replace the synthetic `artifacts` field with Grad-CAM-derived attention maps over the ViT, or add a second pretrained detection-localization model.

## Phase 2 — Frontend decomposition (1 week)

- Extract `useDetection()`, `useChat()`, `useAuth()` hooks from the 1,808-line `App.tsx`.
- Route `App.tsx` down to ~200 lines as a shell + router.
- Add component-level tests with React Testing Library.
- Per-screen Storybook stories.

## Phase 3 — Operational hardening (1–2 weeks)

- Structured logging (`structlog` JSON formatter) in the Flask backend.
- Rate limiting (Flask-Limiter or reverse-proxy layer).
- Sentry integration for both frontend and backend error capture.
- Health endpoint (`/api/healthz`) and readiness probe.
- Dockerfile + docker-compose for one-command local stack (frontend + backend + Supabase emulator).

## Phase 4 — Browser extension (2–3 weeks)

- Manifest V3 Chrome / Firefox extension.
- Right-click any image → "Verify with DeepShield".
- Twitter / Instagram / Facebook / news-site context menus.
- Background page calls the Flask backend; results render in an in-page popover.

## Phase 5 — Open API (1 week)

- Stable REST surface for researchers, journalists, content moderators.
- API keys + per-key rate limits.
- OpenAPI / Swagger spec auto-generated from Flask routes.
- Usage dashboard.

## Phase 6 — Detection dashboard (2 weeks)

- Per-tenant trend chart: detections over time, fake-rate by file type, confidence distribution.
- Risk-scoring rules: alert on rolling fake-rate above a threshold.
- Export to CSV / PDF for journalist workflows.

## Long-term

- **Model quantization** (4-bit / 8-bit) for sub-100ms inference.
- **Edge deployment** via TensorFlow.js or ONNX in the browser.
- **Multi-language i18n** for the React frontend.
- **Verified watermarking** — opt-in cryptographic signature on known-authentic content, paired with detection.
- **Real-time video stream analysis** — different architecture (frame streaming + sliding-window inference).

## Explicitly out of scope

- **Deepfake generation.** This platform detects, it does not generate. Building a generator would invert the value proposition and undermine the safety story.
- **Forensic-grade evidence chain.** We can be one signal in a verification workflow, not a chain-of-custody system for legal evidence.
