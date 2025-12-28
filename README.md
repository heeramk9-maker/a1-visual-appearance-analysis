# A1.0 Visual Appearance Analysis System

A modular prototype for visual appearance reasoning (A1.0) over product images, built as part of the Lenskart AI assignment.

The system analyzes one or more product images using a vision-capable AI model and produces structured, explainable, machine-readable visual measurements based strictly on observable appearance.


## 1. Overview

This project implements a visual product measurement pipeline that:

- Accepts one or more images per product
- Uses a vision-enabled AI model (or mock) for analysis
- Produces continuous scores (−5.0 to +5.0) across independent visual dimensions
- Aggregates multi-image outputs into a conservative consensus
- Exports results in JSON / CSV formats

The system is intentionally designed to:

- Avoid business logic or merchandising assumptions
- Never infer missing information
- Fail safely on invalid inputs or model outputs


## 2. Visual Dimensions (A1.0)

Each dimension is evaluated independently and includes a score, justification, and uncertainty flag.

- Gender Expression (masculine → feminine)
- Visual Weight (light → heavy presence)
- Embellishment (simple → ornate)
- Unconventionality (classic → avant-garde)
- Formality (casual → formal)

Scores are continuous in the range −5.0 to +5.0.


## 3. High-Level Architecture

```
Product Images (URLs / Excel)
            │
            ▼
      Input Handler
 (validation & normalization)
            │
            ▼
     Vision Client
  (mock or real AI)
            │
            ▼
  Visual Parsing Layer
 (scores & attributes)
            │
            ▼
   Schema Validation
 (strict contract)
            │
            ▼
   Per-Image Results
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
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Run mock demo (no API keys required)**

```bash
python scripts/run_demo_mock.py
```

**Outputs directory layout**

- `outputs/sync/` — files written by synchronous runners (folder, Excel, and sync demos)
- `outputs/async/` — files written by asynchronous runners

Both directories contain functionally equivalent JSON and CSV outputs; async runners are provided for throughput improvements and do not change the output schema or aggregation semantics.

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

**Optional: Real AI mode**

Set the API key via environment variables or .env (never commit keys).


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
