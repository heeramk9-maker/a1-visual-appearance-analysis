# Experience / Notes

## Experience Working on the AI-Powered Visual Product Measurement System

Working on this assignment was a practical exercise in designing a realistic AI-powered system under time and scope constraints. The core challenge was building a solution that focuses strictly on **visual appearance reasoning**, without drifting into business logic, recommendations, or inferred intent.

### Problem Understanding

An important early step was identifying what the system should *not* do. The assignment is explicitly about A1.0 visual reasoning—not physical measurements or product classification. Treating the problem as a **visual measurement pipeline** helped avoid over-engineering and kept the scope aligned with the requirements.

### Design Approach

The system was built using a staged, pipeline-oriented approach:

- Define a strict data contract for visual measurements  
- Build a deterministic single-image analysis flow  
- Extend the pipeline to support multiple images per product with conservative aggregation  

A deliberate design choice was to **separate core logic from AI providers**. This allowed development and testing with a mock vision client first, followed by integration of a real vision-capable model (Gemini) without changing the pipeline. This significantly reduced debugging complexity and avoided tight coupling to external APIs.

### Handling AI Non-Determinism

Vision models can produce inconsistent or partially structured outputs, especially for subjective attributes. To handle this safely:

- Prompts enforce strict JSON-only responses  
- Outputs are validated using schemas before aggregation  
- Uncertainty is explicitly represented instead of forcing a decision  

This design treats the AI model as an unreliable external dependency and ensures failures are explicit and contained.

### Working with Real-World Data

Processing the provided Excel dataset surfaced common real-world issues such as missing image URLs, variable numbers of images per product, and ambiguous visuals. The system is designed to fail safely—skipping invalid inputs while continuing to process valid ones—and to aggregate results only when sufficient visual data is available.

### Trade-offs and Limitations

Given the time constraints, I intentionally avoided building a full graphical UI. Instead, the focus was on:

- A clean CLI-based interface  
- Dataset ingestion via Excel files  
- Structured JSON and CSV outputs for inspection  

This approach satisfies usability requirements while keeping the prototype focused and maintainable.

### Key Learnings

This project reinforced the importance of:

- Clear contracts between system components  
- Modular, provider-agnostic architecture  
- Defensive handling of non-deterministic AI outputs  
- Prioritizing clarity, correctness, and explainability over feature count  

---

## What I’d Do Differently With More Time

With additional time, the focus would shift toward improving usability, scalability, and validation depth rather than adding surface-level features.

### 1. Lightweight User Interface

Introduce a minimal web or Streamlit-based interface to allow non-technical users to:

- Upload product images or Excel files  
- Trigger analysis interactively  
- Visualize per-image and aggregated results  

This would improve accessibility without altering the core pipeline.

### 2. Asynchronous and Parallel Processing

The project already includes both synchronous and asynchronous runners; with more time, I would:

- Expand async batching for higher throughput  
- Add retry/backoff and rate-limiting strategies  
- Add more stress and concurrency tests

### 3. Observable Runs (Added)

A recent addition improves console-only observability across all runners without changing any core behavior or output schema:

- A lightweight helper `scripts/tools/run_metrics.py` exposes:
  - `analysis_timer()` — context manager usable as `with` or `async with` to print `Analyzing...` and `Analyzing completed in <X.XX>s` with wall-clock or awaited runtime.
  - `print_model_used(client)` — prints `Model Used: <model-name>` or `Model Used: mock-client` safely.
- All runners under `scripts/` now print these lines in order:
  1. `Processed products: <count>`
  2. `Model Used: <model-name or mock-client>`
  3. `Analyzing...`
  4. `Analyzing completed in <X.XX>s`
  5. `Sample product ids: [...]`
  6. `No processing errors detected.` (if no errors)
  7. `Wrote results to: <output-path>`

These prints are console-only and do not alter JSON/CSV outputs or aggregation behavior.

### 4. Persistent Caching

Extend the existing in-memory cache to:

- Persist results across runs  
- Avoid re-processing identical images  
- Support cache invalidation by model or prompt version  

### 5. Stronger Validation and Testing (Updated)

Testing has been extended and developer ergonomics improved:

- A `conftest.py` helper ensures pytest can import the `app` package and local tests easily.
- Additions include async pipeline tests and cache-focused tests.

### Final Reflection

This project prioritizes **clear reasoning, modular design, safe AI integration, and developer ergonomics**. The recent observability and testing improvements make the repo easier to run and verify while keeping the core pipeline unchanged and stable.
