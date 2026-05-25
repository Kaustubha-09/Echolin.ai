# Model Card

A short, honest description of the model that drives Echolin.ai.

## Model

| Field | Value |
|---|---|
| Name | `ashish-001/deepfake-detection-using-ViT` |
| Architecture | Vision Transformer (ViT-Base) |
| Source | [Hugging Face Hub](https://huggingface.co/ashish-001/deepfake-detection-using-ViT) |
| Task | Binary image classification — `{Real, Fake}` |
| Input | 224 × 224 RGB image |
| Output | Softmax probability over 2 classes |
| Parameters | ~86M (ViT-Base) |
| Authors | `ashish-001` on Hugging Face — third-party model, used as-is |

We do not fine-tune. We do not retrain. The model is loaded at import time in `detector.py` and used for inference only.

## Intended use

- Image and video deepfake screening for verification workflows.
- Educational content moderation.
- Journalist fact-checking as **one signal among multiple**.
- Personal authenticity checks.

## Out-of-scope use

- Legal forensic evidence (no chain of custody, no audit trail).
- Final arbitration in high-stakes content decisions (use as a signal in a multi-method workflow).
- Detection of generators released after the model's training cutoff (will degrade silently).

## Inference contract

| Property | Behavior |
|---|---|
| Image: input | One file (`image/*`) |
| Image: output | `{type: "image", label: "Real" \| "Fake", confidence: float, artifacts: [...]}` |
| Video: input | One file (`video/*`), processed via OpenCV |
| Video: sampling | First 10 frames sequentially (constant `MAX_VIDEO_FRAMES`) |
| Video: aggregation | Majority vote on label, average confidence over frames matching the winning label |
| Latency | ~0.5s/image, ~5s/video, on CPU |
| Concurrency | Single global model instance, Flask request thread |

## Known weaknesses

- **No localization.** The model outputs one binary verdict. "Which part of the face was manipulated?" is unanswerable.
- **No temporal modeling.** Frame-to-frame consistency is one of the strongest deepfake signals; the current pipeline ignores it. See [roadmap.md](roadmap.md), Phase 1.
- **No audio path.** Lip-sync manipulation, voice cloning are out of scope.
- **Training set drift.** Newer generator architectures (StyleGAN3+, Diffusion-based face synthesis post-2023) may evade detection.

## How accuracy claims should be read

The model's Hugging Face page reports 92–98% accuracy on standard test sets. We have not independently re-evaluated. Treat published numbers as **upper bounds on optimistic test conditions**, not as production guarantees. Real-world distribution shift (compression artifacts, social-media re-encoding, screen-recorded fakes) reduces these numbers.

## Recommended verification workflow

Use Echolin.ai as **one tool in a chain**:

1. Provenance check (C2PA / Content Credentials if present).
2. Reverse image search.
3. Source-trail verification.
4. Echolin.ai detection.
5. Human reviewer if any of the above conflict.

A high-confidence "Fake" verdict from this system is a strong reason to escalate; it is not by itself sufficient to publish a correction or take a moderation action.
