## Data Overview

This directory contains **input data provided by the company** for the
A1.0 Visual Appearance Analysis assignment.

The data in this folder is used **only as input** to demonstrate and
validate the visual analysis pipeline implemented in this project.

---

## Files

### `A1.0_data_product_images.xlsx`

- Official input sheet shared by the company
- Contains product identifiers and corresponding image URLs
- Serves as the **source of truth** for demo and evaluation runs

The file is treated as **read-only** and is not modified by the system.

---

## Important Notes

- This data is **not training data**
- No machine learning models are trained or fine-tuned using this data
- Images are processed independently for visual appearance analysis only
- No labels, annotations, or derived datasets are created

---

## Usage in This Project

The Excel file is read by the demo script to:
1. Extract image URLs per product
2. Run A1.0 visual analysis on each image
3. Aggregate results across multiple images of the same product

The resulting outputs are written to the `outputs/` directory.

---

## Scope Clarification

This project focuses on **system design, validation, and aggregation logic**.
The quality or content of the images themselves is outside the scope of
this implementation.
