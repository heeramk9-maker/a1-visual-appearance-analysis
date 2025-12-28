# A1.0 Visual Appearance Analysis — Concise Design Write-up

## Overview

- Purpose: Analyze product *visual appearance* only. No merchandising, intent, or business logic is inferred.
- Supports multiple images per product; outputs continuous scores in the range −5.0 … +5.0.
- Exports product-level results as JSON and CSV.

## High-level Architecture

Product images (URLs / local files)
    │
    ▼
Input normalization & validation
    │
    ▼
Vision client (mock or real provider)
    │
    ▼
Per-image parsing → schema validation
    │
    ▼
Dimension-wise aggregation → product output (JSON, CSV)

## Key Assumptions & Design Decisions

- Visual-only: results reflect observable appearance only; no business or merchandising inference.
- Provider-agnostic client abstraction to allow mock testing and real-provider demos.
- Schema-first parsing and conservative aggregation to surface disagreement across images.
- Both synchronous and asynchronous runners are provided: sync for parity and async for throughput.

## Limitations & Future Improvements

- Visual judgments are subjective and depend on image quality and framing.
- CLI demo (not a production service); no long-term persistence in current scope.
- Future work: lightweight UI, persistent caching, multi-provider fallback, confidence calibration.

## Setup Instructions

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

## Steps to Run Locally

Synchronous runners:
- Mock demo: python scripts/run_demo_mock.py
- Folder-based sync: python scripts/run_from_folder.py <folder_path>
- Excel (sync): python scripts/run_from_excel.py --excel-file <path>

Asynchronous (non-blocking) runners:
- Folder-based async: python scripts/run_demo_async.py <folder_path> [concurrency]
- Excel (async): python scripts/run_from_excel_async.py --excel-file <path> --concurrency <N>

Optional real-provider demo (Gemini): python scripts/run_demo_real_gemini.py (requires GEMINI_API_KEY)

Run tests: pytest -q

## Dependencies / Assumptions

- Python 3.10+ (tested on 3.12)
- `pip install -r requirements.txt` for core dependencies
- Optional: `google-genai` for Gemini demos and `python-dotenv` for .env loading
- Real-AI demos expect URL-based images; local-file demos support folder runners

---

This concise write-up is formatted for submission review and omits implementation detail. For full technical context, see the source files under `app/` and `scripts/`.
            │
            ▼
   Multi-Image Aggregator
 (dimension-wise consensus)
            │
            ▼
      Final Output
    (JSON / CSV)
```

### Key design principles

- Separation of concerns (input, model, parsing, aggregation)
- Provider-agnostic core logic
- Strict schema validation
- Explicit uncertainty handling
- Explainability-first outputs


## 4. Observable Attributes

In addition to scores, the system extracts clearly visible attributes when unambiguous, including:

- Dominant colors
- Frame / structural geometry
- Transparency or opacity
- Visible textures or surface patterns
- Presence of visible wirecore
- Suitability for kids

Unknown or unclear attributes are explicitly marked as "uncertain".


## 5. Multi-Image Handling

- Each image of a product is analyzed independently
- Results are aggregated per dimension, not averaged blindly
- Disagreement across images is detected and flagged
- Confidence reflects the fraction of contributing images

This ensures robustness when images show different angles, lighting, or partial views.


## 6. Running the Project

**Setup**

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

**Run mock demo (no API keys required)**

```bash
python scripts/run_demo_mock.py
```

**Console observability (what you'll see)**

Runners now print a compact, consistent summary for each run (console-only, does not change outputs):

- Processed products: <count>
- Model Used: <model-name or mock-client>
- Analyzing...
- Analyzing completed in <X.XX>s
- Sample product ids: [...]
- No processing errors detected.
- Wrote results to: <output-path>

This behavior is implemented via `scripts/tools/run_metrics.py` which exposes `analysis_timer()` and `print_model_used()` and is used by all runners (sync + async).

**Outputs directory layout**

- `outputs/sync/` — files written by synchronous runners (folder, Excel, and sync demos)
- `outputs/async/` — files written by asynchronous runners

Both directories contain the same JSON/CSV schema and the runners remain fully backward compatible.

**Run with Excel input (sync)**

```bash
# Place your Excel file at data/A1.0_data_product_images.xlsx, or provide a custom path
python scripts/run_from_excel.py --excel-file data/A1.0_data_product_images.xlsx
```

**Run with Excel input (async)**

```bash
# Async runner supports concurrency and custom Excel path
python scripts/run_from_excel_async.py --excel-file data/A1.0_data_product_images.xlsx --concurrency 5
```

**Run tests**

```bash
pytest -q
```

A lightweight `conftest.py` (repo root) ensures pytest can import the `app` package and local tests easily.

**Optional: Real AI mode**

Set the API key via environment variables or a `.env` file (never commit keys).


## 7. Example Output (Simplified)

```json
{
  "visual_consensus": {
    "formality": {
      "mean": 0.8,
      "range": [-0.2, 1.4],
      "confidence": 1.0,
      "disagreement": false
    }
  },
  "attribute_summary": {
    "dominant_colors": {
      "value": ["black"],
      "confidence": 1.0
    }
  }
}
```


## 8. Key Design Decisions

- Model abstraction: Vision models are injected, enabling mock testing and future provider swaps
- Strict schemas: Prevent malformed or hallucinated outputs from propagating
- Conservative aggregation: Disagreement is surfaced, not hidden
- Fail-safe behavior: Explicit errors over silent assumptions


## 9. Limitations & Future Improvements

**Limitations**

- Visual judgments are subjective and image-quality dependent
- Demo-level interface (CLI-based)
- No long-term persistence

**Future improvements**

- Lightweight web UI for uploads
- Async batch processing
- Persistent caching
- Multi-provider fallback
- Confidence calibration


## 10. Repository Contents

- `app/` — core pipeline modules
- `scripts/` — demo and Excel runners
- `data/` — sample inputs
- `outputs/` — generated results

**Notes**

This prototype prioritizes clarity, correctness, and extensibility over UI polish or production hardening, in line with the assignment scope.



**Real AI Mode (Optional)**

Set the `OPENAI_API_KEY` environment variable before running the optional real-AI demo. Any vision-capable model can be specified via the `OPENAI_VISION_MODEL` environment variable (defaults to `gpt-4o-mini`). Examples:

PowerShell (temporary session):

```powershell
$env:OPENAI_API_KEY = "your_key"
python scripts/run_demo_real_ai.py
```

PowerShell (persist across sessions):

```powershell
setx OPENAI_API_KEY "your_key"
# close and reopen your terminal for the change to take effect
python scripts/run_demo_real_ai.py
```

macOS / Linux (bash/zsh):

```bash
export OPENAI_API_KEY=your_key
python scripts/run_demo_real_ai.py
```

Local development using a `.env` file (recommended for local testing only):

1. Create a `.env` file in the repository root:

```
OPENAI_API_KEY=your_key
```

2. Ensure `.env` is listed in `.gitignore` (already added).
3. Install `python-dotenv` and load it in your script (optional):

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()  # loads variables from .env into the environment
```

**Security note:** Keep API keys out of source control. Use CI secrets or a secrets manager for production.

Optional extensions include adding runtime dependencies to `requirements.txt`, integrating a real vision model, and expanding automated tests. Make `How to run the demo` and `Testing` sections optional additions upon request.
