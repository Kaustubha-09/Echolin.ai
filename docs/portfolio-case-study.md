# Echolin.ai (DeepShield AI) — Portfolio Case Study

Skim time: 3 minutes.

## The problem

Deepfake fraud rose ~2,100% from 2019 to 2023 (Sumsub, Onfido). Journalists, content moderators, students, and average users have no fast way to ask "is this image or video real?" without a forensic specialist. Existing tools are either gated behind enterprise contracts or live in research repos with a 50-step setup.

## The product

A clean web app: drag in a file, get a Real/Fake label with a confidence score in ~0.5s, and an optional plain-English LLM explanation. Auth and history are persistent per user; everything is row-level-secured.

## The architecture I'd defend in an interview

### 1. Three-tier separation with explicit failure containment

Flask backend → PyTorch ViT inference → optional LLM explanation. If the LLM layer fails, the detection result is returned anyway with a graceful "LLM explanation unavailable" string. Critical-path independence — the detection never depends on the LLM working. See [decisions.md, ADR-005](decisions.md#adr-005--llm-explanation-is-best-effort-not-blocking).

### 2. Pretrained ViT, with the seam to swap

We don't pretend to have trained our own model. We use `ashish-001/deepfake-detection-using-ViT` from Hugging Face behind a function boundary in `detector.py`. Real engineering judgment: building a detector is a multi-quarter research project; building the *system around* the detector is the portfolio-shippable piece. See [ADR-001](decisions.md#adr-001--pretrained-vit-not-a-custom-trained-model).

### 3. Video as majority vote over 10 frames

Single-frame is too noisy; full-frame is too expensive. Ten frames sampled sequentially from the start, run through the same ViT, majority-voted label, average confidence over matching frames. Deterministic, reproducible, runs in ~5s. See [ADR-003](decisions.md#adr-003--video-as-majority-vote-over-up-to-10-sampled-frames).

### 4. Honest about the `artifacts` field

The API returns an `artifacts` list, but the base ViT is a single binary classifier — it has no localization. The artifacts entry repackages the same confidence under a descriptive label. **We call this out in the docs** rather than dressing it up. The roadmap defines the upgrade path (multi-head architecture or detector ensemble). See [ADR-004](decisions.md#adr-004--synthetic-artifacts-field-honestly-labeled).

### 5. Supabase for everything not the model

Auth (JWT), Postgres (sessions, messages, detections), Storage (uploads), Row-Level Security on every table. The value proposition isn't novel auth; it's the detection. We refused displacement activity and used a managed BaaS for the boring parts. See [ADR-007](decisions.md#adr-007--supabase-over-a-custom-postgres--auth--s3-stack).

### 6. LLM endpoint pluggable across providers

`llm_service.py` calls a chat-completions endpoint configured by `GMI_API_URL` / `GMI_API_KEY` env vars. GMI Cloud is the default (Northeastern student credits); OpenAI is a drop-in alternative because their REST surface is compatible. One config flip, no code fork.

## What I'd own about the codebase

`src/App.tsx` is 1,808 lines. State, handlers, render functions all in one file. I called this out in [ADR-006](decisions.md#adr-006--monolithic-apptsx-deferred-decomposition) — it's tracked, it's not pretending to be clean, and the decomposition path is documented. Shipping with known debt that's tracked is healthier than shipping with hidden debt that's not.

## What I'd do next

Phase 1 of the [roadmap](roadmap.md): temporal coherence model over video frames, audio path for lip-sync detection, real artifact localization via Grad-CAM. These are the upgrades that turn the demo into a real product.

## What this signals to a recruiter

- I can ship a working ML web app — frontend, backend, model service, auth, storage — end to end.
- I know what I built and what I didn't. The README distinguishes the pretrained model from custom training, the synthetic artifacts field from real localization, the Flask live path from the FastAPI research path. No bullshit, no padding.
- I write ADRs, not just code.
- I read the failure modes (LLM down, model down, video frames missing, malformed upload) and design containment, not retries.
- I picked the right vendor (Supabase) for the boring parts so I could spend time on the interesting parts.
