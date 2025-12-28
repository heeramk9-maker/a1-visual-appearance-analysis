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

The current implementation prioritizes clarity over throughput. With more time, I would:

- Add asynchronous or batched inference calls  
- Parallelize multi-image analysis  
- Implement basic retry and rate-limiting logic  

### 3. Persistent Caching

Extend the existing in-memory cache to:

- Persist results across runs  
- Avoid re-processing identical images  
- Support cache invalidation by model or prompt version  

### 4. Stronger Validation and Testing

Expand testing beyond structural validation to include:

- Golden test cases with expected visual outcomes  
- Regression tests for prompt changes  
- Stress tests using noisy or ambiguous images  

### 5. Multi-Provider Fallback Strategy

Formalize support for multiple vision providers by:

- Implementing automatic fallback logic  
- Comparing outputs across providers  
- Calibrating confidence scores per model  

### Final Reflection

Rather than aiming for feature completeness, this project focuses on demonstrating **clear reasoning, modular design, and safe AI integration**. With more time, the priority would be improving scale, UX, and operational robustness while preserving the core principles of transparency and correctness.
