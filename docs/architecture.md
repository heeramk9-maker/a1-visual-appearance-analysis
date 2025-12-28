# System Architecture

This document describes the internal architecture of the **A1.0 Visual Appearance Analysis System**, focusing on component responsibilities, data flow, and key design decisions.

The goal of the architecture is to support **safe, explainable, and extensible visual reasoning** while treating AI models as unreliable external dependencies.

---

## 1. Architectural Goals

The system is designed to:

- Analyze **visual appearance only**, not intent or business meaning
- Handle **one or more images per product**
- Be **provider-agnostic** with respect to vision AI models
- Fail safely when inputs or model outputs are invalid
- Produce **deterministic, machine-consumable outputs**
- Support future extensions without rewriting core logic

---

## 2. High-Level Architecture Flow

Core flow (ASCII):

```
Input (URLs / local files)
    │
    ▼
Input handler / loader (validation & normalization)    ← `app.input_handler`
    │
    ▼
Per-image processing
 ├─ Sync: `process_single_image` (calls `vision_client`)    ← `app.pipeline`
 └─ Async: `process_images_async` (concurrency-aware)     ← `app.async_pipeline`
    │
    ▼
Per-image parsing & schema validation (`app.schema`)
    │
    ▼
Aggregator (dimension-wise consensus)  ← `app.aggregator`
    │
    ▼
Exporter (JSON / CSV)  → `outputs/sync/` or `outputs/async/`  ← `app.exporter`
```

### Components (concise)

- Input: `app.input_handler` — normalize inputs (URLs, local files, Excel rows).
- Clients: `app.vision_client` (mock), `app.gemini_vision_client`, `app.openai_vision_client` — provider adapters exposing `infer(image, prompts)` and `model` when available.
- Processing: `app.pipeline` (sync) and `app.async_pipeline` (async)
- Validation & Aggregation: `app.schema`, `app.aggregator`
- Export: `app.exporter` writes JSON and CSV without changing schema
- Observability: `scripts/tools/run_metrics.py` provides `analysis_timer()` and `print_model_used()` for console-only runtime lines used by scripts
- Runners: `scripts/` has runnable entry points (sync & async) and demo scripts

### Data flow & guarantees

- Images are grouped per product and processed per-image; aggregation is conservative and surfaces disagreement across images.
- Outputs are deterministic given the same per-image results and are written to the `outputs/` hierarchy.
- Observability additions are console-only and do not change output files or schemas.

### Operational notes

- Sync runners measure wall-clock time; async runners measure total awaited runtime using `analysis_timer()`.
- Real-provider demos require SDKs and credentials (e.g., `google-genai` with `GEMINI_API_KEY`). Runners fall back to the mock client for local development if SDKs are missing.
- Test: run `pytest -q`; `conftest.py` ensures tests import the `app` package for local runs.

---

This document is intentionally concise and focused on architecture-level concerns; see `app/` and `scripts/` for implementation details.