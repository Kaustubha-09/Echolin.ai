# Architecture

Echolin.ai (DeepShield AI in-product) is a three-tier deepfake detection system. The user uploads an image or video; a pretrained Vision Transformer classifies it as real or fake with a softmax confidence; an LLM layer optionally generates a plain-English explanation; results persist to Supabase under row-level security.

## System diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       Frontend (React 19 + TS)                  │
│  App.tsx · UploadComponent · AuthModal · ChatHistory ·          │
│  SettingsModal · UserProfile · openaiService · supabaseService  │
└─────────────────────────────────────────────────────────────────┘
              │                                  │
              │  multipart/form-data             │  Supabase JS
              ▼                                  ▼
┌─────────────────────────────┐      ┌──────────────────────────────┐
│   Flask API  (port 5000)    │      │   Supabase                   │
│   backend/app.py            │      │   - Auth (JWT)               │
│   ├─ POST /api/detect       │      │   - Postgres                 │
│   └─ POST /api/agent-detect │      │     · chat_sessions          │
└─────────────────────────────┘      │     · chat_messages          │
              │                      │     · detections             │
              │                      │   - Storage (uploads bucket) │
              ▼                      │   - RLS on every table       │
┌─────────────────────────────┐      └──────────────────────────────┘
│  detector.py                │
│  - Hugging Face ViT          │
│    ashish-001/deepfake-      │
│    detection-using-ViT      │
│  - PIL + torch.no_grad()    │
│  - OpenCV for video frames  │
└─────────────────────────────┘
              │  (only on /agent-detect)
              ▼
┌─────────────────────────────┐      ┌──────────────────────────────┐
│  agent.py                   │ ───► │  llm_service.py              │
│  detect → explain pipeline  │      │  GMI Cloud (or OpenAI)        │
└─────────────────────────────┘      │  gpt-3.5-turbo                │
                                     │  per-mode system prompts:    │
                                     │  analysis · educational ·    │
                                     │  conversational · threat     │
                                     └──────────────────────────────┘

(detection_model/ is a parallel FastAPI service for batch
 experimentation; not on the request path of the live demo.)
```

## The two backend services

The repo contains two Python services, which is the most-confused thing about the architecture:

| Service | Framework | Port | Purpose |
|---|---|---|---|
| `backend/` | **Flask** | 5000 | Live API used by the React frontend. `/api/detect` (label + confidence only) and `/api/agent-detect` (adds LLM explanation). |
| `detection_model/` | **FastAPI** | 8000 | Standalone batch tooling — `deepfake_image.py`, `deepfake_video.py`, `fast_api.py`. Used during model evaluation and for running batch jobs against folders of media. Not on the production request path. |

The live demo uses `backend/` only. The `detection_model/` folder is the **research tooling**, kept in-repo so the experiments are reproducible.

## Request flow — `/api/agent-detect`

```
1. Frontend (App.tsx)
     └─ user drops an image/video into UploadComponent
     └─ POST multipart/form-data → Flask /api/agent-detect

2. Flask (app.py)
     └─ file_type = file.content_type
     └─ calls deepfake_agent(file, file_type) in agent.py

3. agent.py
     ├─ image  → detect_image(file)   (detector.py)
     └─ video  → detect_video(file)   (detector.py)

4. detector.py
     ├─ Image path:
     │    ├─ PIL.Image.open(file).convert("RGB")
     │    ├─ AutoImageProcessor(images=..., return_tensors="pt")
     │    ├─ AutoModelForImageClassification (no_grad)
     │    └─ softmax(logits) → label, max_prob = confidence
     │
     └─ Video path:
          ├─ tempfile → cv2.VideoCapture
          ├─ for up to 10 frames:
          │    same ViT pipeline as image
          ├─ majority-vote winning label
          └─ average confidence over frames matching the winning label

5. agent.py (continued)
     └─ generate_analysis_explanation(detection_result, filename, level)
          via llm_service.py → GMI Cloud / OpenAI / gpt-3.5-turbo
     └─ returns { label, confidence, artifacts, explanation }

6. Flask responds JSON → Frontend renders detection card + explanation
```

If the LLM call fails (network, missing API key), `agent.py` catches the exception and returns `"LLM explanation unavailable. Core detection succeeded."` — detection always succeeds independent of the LLM.

## Why the artifacts field is a synthetic placeholder

The response includes:

```python
"artifacts": [{"type": "face_texture", "score": confidence * 100}]
```

This is **not** a real artifact detection. The base ViT model is a single binary classifier — it outputs one softmax probability over `{real, fake}` and gives no localization or sub-feature breakdown. The artifact entry repackages the same confidence under a descriptive label so the frontend has a uniform field to display.

A real artifact pipeline would require either (a) a multi-head architecture trained on labeled artifact regions (Grad-CAM, attention rollouts) or (b) an ensemble of single-purpose detectors (blink rate, lip-sync, face-edge gradient, frequency-domain irregularity). Both are documented in [roadmap.md](roadmap.md) as the upgrade path.

## Model

| Property | Value |
|---|---|
| Architecture | Vision Transformer (ViT-Base) |
| Hugging Face ID | `ashish-001/deepfake-detection-using-ViT` |
| Input | 224×224 RGB image |
| Output | Binary softmax over `{Real, Fake}` |
| Inference | `torch.no_grad()`, CPU by default, ~0.5s per image on standard hardware |
| Loaded | Module-level singleton on backend startup |

The image processor and model are loaded once at import time in `detector.py` so per-request latency is just the forward pass plus preprocessing. There is no warm-up cost after the first request.

## Frontend organization

`src/App.tsx` is a 1,808-line "god component" that owns the entire UI state — known issue, called out in [decisions.md, ADR-006](decisions.md#adr-006--monolithic-apptsx-deferred-decomposition). Sub-components (`AuthModal`, `ChatHistory`, `SettingsModal`, `UploadComponent`, `UserProfile`) live in `src/components/`. Services in `src/services/`:

- `supabaseService.ts` — auth state, session + message CRUD, RLS-aware queries
- `openaiService.ts` — direct OpenAI client for in-browser explanation (alternative to the backend's LLM path)
- `LLMService.js` — legacy LLM helper

## Persistence

Three Postgres tables on Supabase, all with row-level security:

```sql
chat_sessions(id, user_id, title, created_at, updated_at)
chat_messages(id, session_id, type, content, metadata, created_at)
detections(id, user_id, file_path, storage_bucket, analysis_result, confidence, status, created_at)
```

RLS policies (full SQL in the main README) restrict every row to `auth.uid() = user_id`. The frontend uses the Supabase anon key; row-level filtering happens on Postgres, not in app code.

## What runs where

| Concern | Lives in |
|---|---|
| File upload UI | `src/App.tsx` + `src/components/UploadComponent.tsx` |
| Multipart upload | Frontend → `axios` → Flask |
| Image preprocessing | `backend/detector.py` (PIL + transformers' AutoImageProcessor) |
| Video frame extraction | `backend/detector.py` (OpenCV) |
| Model inference | `backend/detector.py` (PyTorch ViT) |
| LLM explanation | `backend/llm_service.py` *or* `src/services/openaiService.ts` |
| Auth | Supabase (frontend JS client) |
| RLS enforcement | Postgres |
| File storage | Supabase Storage bucket `uploads` |
| Session + message persistence | Supabase Postgres via `src/services/supabaseService.ts` |
