# Architecture Decision Records

Dated decisions that capture *why* something was built the way it was. ADRs are append-only.

## ADR-001 · Pretrained ViT, not a custom-trained model

**Date:** 2026-03
**Status:** Accepted

We use `ashish-001/deepfake-detection-using-ViT` directly from Hugging Face. No custom training, no fine-tuning, no in-house dataset.

**Why:** building a real deepfake detector requires (a) a large labeled corpus of real/fake media that doesn't overlap with public test sets, (b) GPU training budget, and (c) a continuous re-training loop because generators evolve weekly. A pretrained ViT gets us a working demo in one HTTP call. The architectural seam is real — `detector.py` loads the model behind a function boundary, so swapping for a fine-tuned or ensemble model is a one-file change.

**Cost:** the model is only as good as its training set. Generator architectures published after the model was trained will not be reliably detected. We're explicit about this in [limitations.md](limitations.md).

---

## ADR-002 · Flask for the live backend, FastAPI for batch tooling

**Date:** 2026-03
**Status:** Accepted

`backend/` is Flask. `detection_model/` is FastAPI. Same Python ecosystem, different request paths.

**Why:** Flask is simpler for the live demo's 2-endpoint surface. The detection-model subdirectory needs async file iteration + streaming responses for batch jobs, which is FastAPI's wheelhouse. We picked the right tool per role rather than forcing one framework everywhere.

**Cost:** two Python web frameworks in the same repo. Mitigated by clear directory boundaries: `backend/` is the only thing the frontend talks to; `detection_model/` is research tooling.

**When to reconsider:** if we add more live endpoints or need async upload streaming on the live path, consolidate on FastAPI.

---

## ADR-003 · Video as majority-vote over up to 10 sampled frames

**Date:** 2026-03
**Status:** Accepted

`detect_video` extracts up to `MAX_VIDEO_FRAMES = 10` frames sequentially from the start of the video, runs each through the ViT, and returns the most-voted label plus the average confidence over matching frames.

**Why:**
- Single-frame is too noisy — a brief expression or lighting glitch can flip the label.
- Full-frame is too expensive — a 30-second video at 30 fps is 900 ViT forward passes (~7.5 minutes on CPU).
- Ten frames gives stable majority voting in ~5 seconds.
- Sequential-from-start (not random sample) is reproducible — same video → same frames → same prediction.

**Cost:** we miss deepfakes that are limited to frames beyond frame 10. Real-world deepfakes tend to be consistent (the generator was trained once, applied across the video), so the first 10 frames are usually representative.

**Confidence math:** we average confidence over frames that voted with the winning label, not all 10. This is deliberate — averaging across dissenting predictions would muddy the signal.

---

## ADR-004 · Synthetic `artifacts` field, honestly labeled

**Date:** 2026-03
**Status:** Accepted, technical-debt

The detection response includes `"artifacts": [{"type": "face_texture", "score": confidence * 100}]`. This is **not** a real artifact detection — it's a synthetic packaging of the same softmax confidence under a descriptive label so the frontend has a uniform field.

**Why we did it:** the UI was designed around per-artifact breakdowns before we picked the model. Rather than rewrite the UI, we backfilled a field. It works for the demo but does not represent multi-factor detection.

**What honest looks like:** the `architecture.md` doc names this out and the [roadmap.md](roadmap.md) defines the upgrade path (multi-head architecture or ensemble of single-purpose detectors). This is the kind of decision that's fine to ship as long as it isn't dressed up as more than it is.

---

## ADR-005 · LLM explanation is best-effort, not blocking

**Date:** 2026-03
**Status:** Accepted

If `llm_service.generate_analysis_explanation` raises (missing API key, network error, rate limit), `agent.py` catches and returns `"LLM explanation unavailable. Core detection succeeded."` The detection itself never fails because of an LLM problem.

**Why:** the LLM layer is a nice-to-have explanation; the binary classification is the load-bearing answer. Coupling failure modes would be a regression.

---

## ADR-006 · Monolithic `App.tsx` — deferred decomposition

**Date:** 2026-03
**Status:** Accepted, technical-debt

`src/App.tsx` is 1,808 lines. State, handlers, render functions, type definitions — all in one file.

**Why it happened:** the demo evolved iteratively. Each feature (auth, upload, chat, settings) started as a state hook in `App` and migrated to its own component only when it grew large enough to justify the extraction.

**What we'd do differently:** extract a `useDetection()` hook, a `useChat()` hook, a `useAuth()` hook, and let `App.tsx` be the routing shell. The blocker is regression risk on the demo loop — the rewrite isn't 1:1 because some state interactions are subtle.

**Tracked in [roadmap.md](roadmap.md)** under "Frontend refactor".

---

## ADR-007 · Supabase over a custom Postgres + Auth + S3 stack

**Date:** 2026-03
**Status:** Accepted

Auth, Postgres, storage, and row-level security all from one vendor.

**Why:** the value proposition isn't novel auth or novel storage — it's the deepfake detection. Spending a week on a custom auth flow + S3 wiring would be displacement activity. Supabase ships JWT auth, Postgres with RLS, and a storage bucket in ~15 minutes of configuration.

**Cost:** vendor lock-in for auth + storage. Acceptable because the seam is the JavaScript Supabase client; if we ever need to migrate, the surface is a few files in `src/services/`.

---

## ADR-008 · LLM endpoint pluggable (GMI Cloud + OpenAI)

**Date:** 2026-03
**Status:** Accepted

`llm_service.py` calls a chat-completions endpoint configured by env vars:

```python
API_KEY = os.getenv("GMI_API_KEY")
API_URL = os.getenv("GMI_API_URL", "https://api.gmi.cloud/v1/chat/completions")
```

GMI Cloud (Northeastern's AI cloud) is the default; OpenAI is a drop-in alternative (its REST surface is compatible).

**Why:** GMI offers free credits for Northeastern students; OpenAI is the production-grade fallback. The compatibility means the codebase doesn't fork.

---

## ADR-009 · Brand: repo = `Echolin.ai`, in-product = `DeepShield AI`

**Date:** 2026-03
**Status:** Accepted, naming-debt

The GitHub repo is named `Echolin.ai`. The in-product brand (sidebar, system prompts, system status badge) is "DeepShield AI". The team is ICE-CUBA (per LICENSE).

**Why both:** the project was renamed mid-development from Echolin → DeepShield AI. The repo name stayed for URL stability (link rot in shared course materials). The in-product name reflects the final product identity.

**When to reconcile:** if the project gets a real domain or App Store presence, fold both into a single brand and rename the repo with `gh repo rename`.
