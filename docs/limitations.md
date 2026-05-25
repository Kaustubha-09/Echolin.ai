# Limitations

Honest scope boundary. Detection systems that overpromise are a security risk; we'd rather be specific than impressive.

## Model limitations

- **Single pretrained ViT.** We use one Hugging Face model (`ashish-001/deepfake-detection-using-ViT`). No ensemble, no consensus, no model-vs-model corroboration.
- **Training-set coverage.** The model performs well on generator architectures it has seen during training. Newer generators (released after the model's training cutoff) may evade detection.
- **No per-region localization.** The model outputs one softmax over `{real, fake}`. It cannot tell you *which part* of an image was manipulated.
- **`artifacts` field is synthetic.** The detection response includes an `artifacts` list, but this is a label-wrapped repackaging of the same softmax confidence — not a real artifact detection. See [decisions.md, ADR-004](decisions.md#adr-004--synthetic-artifacts-field-honestly-labeled).
- **Accuracy claims hedged.** Public benchmark numbers (92–98% on standard datasets) come from the model card on Hugging Face. We have not independently re-evaluated on out-of-distribution media; treat as upper bounds, not guarantees.

## Video limitations

- **Up to 10 frames analyzed.** `detect_video` reads the first 10 frames sequentially. Deepfakes confined to later frames will be missed.
- **No temporal coherence model.** Each frame is classified independently, then majority-voted. We do not model frame-to-frame consistency (which is one of the strongest deepfake signals).
- **No audio analysis.** Audio-only or lip-sync manipulations are not detected.

## Detection pipeline limitations

- **CPU inference.** No GPU acceleration. Per-image latency is ~0.5s on standard hardware; videos are ~5s for 10 frames.
- **No batching on the live path.** Each upload is processed independently. Throughput is not optimized for high concurrency.
- **No streaming inference.** The full file must upload before detection begins. Real-time deepfake detection on a live video stream is a different system.

## System limitations

- **LLM explanation is optional and best-effort.** If the API call fails, the explanation is omitted but core detection succeeds.
- **No multi-tenant isolation beyond RLS.** Row-level security in Supabase scopes data to the authenticated user. There is no further organizational tenancy (no teams, no shared workspaces).
- **File retention.** Files in Supabase Storage are not auto-deleted by default. Production deployments should configure a TTL bucket policy.

## Trust limitations

- **One signal among many.** Deepfake detection is one verification method. Real-world verification (journalism, fact-checking, legal evidence) should combine technical detection with provenance metadata, source verification, and human review.
- **False positives and negatives both happen.** Treat results as probabilistic, not definitive.

## Operational

- **Demo-grade error handling.** Some upload edge cases (corrupted EXIF, exotic codecs) may surface as 500s rather than user-friendly errors.
- **No rate limiting on the Flask backend.** Production deployment should put this behind a gateway (Cloudflare, AWS API Gateway).
- **No structured logging.** `print()` statements in `agent.py` are fine for development but should move to a proper logger (`structlog` or stdlib `logging` with JSON formatter) for production.
