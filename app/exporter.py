"""exporter.py
Export finalized product-level results to JSON (and optional CSV).

Responsibilities
- Add `product_id`, `metadata`, and `confidence_notes`
- Save JSON to `outputs/` (default) and optionally produce CSV
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from pathlib import Path
import json
import uuid
import datetime
import csv


def _compute_overall_confidence(aggregated: Dict[str, Any]) -> Tuple[float, list]:
    """Compute a simple overall confidence score in [0,1] and notes.

    Preference order:
      1. If `visual_consensus` is present, derive confidence primarily from its per-dimension confidence and disagreements.
      2. Fallback to legacy fields (`score_summary`, `score_disagreements`, `attribute_disagreements`).

    Returns (confidence, notes)
    """
    notes: list[str] = []

    # Prefer visual_consensus when available
    vc = aggregated.get("visual_consensus") or {}
    if vc:
        # collect per-dimension confidence scores and disagreement flags
        conf_vals = []
        disagreements = []
        for dim, info in vc.items():
            c = info.get("confidence")
            if isinstance(c, (int, float)):
                conf_vals.append(float(c))
            if info.get("disagreement"):
                disagreements.append(dim)

        avg_conf = float(sum(conf_vals) / len(conf_vals)) if conf_vals else 0.0
        conf = max(0.0, min(1.0, avg_conf))
        if disagreements:
            notes.append(f"dimensions with disagreement: {disagreements}")
            # conservative penalty for disagreements: 0.08 per disagreed dimension, capped
            penalty = min(0.5, 0.08 * len(disagreements))
            conf = max(0.0, conf - penalty)
        notes.insert(0, f"visual_consensus mean confidence: {avg_conf:.3f}")
        if not notes:
            notes.append("no notable disagreements or missing values")
        return conf, notes

    # Legacy fallback: compute based on score_summary and disagreement fields
    conf = 1.0
    ss = aggregated.get("score_summary", {})
    count = ss.get("count", 0)
    missing = ss.get("missing", 0)
    total_images = count + missing
    if total_images > 0:
        missing_frac = missing / total_images
        if missing_frac > 0:
            notes.append(f"{missing} of {total_images} images missing numeric scores")
            conf -= 0.2 * missing_frac

    # attribute disagreements reduce confidence proportionally to number of attributes in disagreement
    attr_disagreements = aggregated.get("attribute_disagreements", {}) or {}
    if attr_disagreements:
        notes.append(f"attribute disagreements: {list(attr_disagreements.keys())}")
        # scale penalty: 0.1 per disputed attribute (capped)
        penalty = min(0.5, 0.1 * len(attr_disagreements))
        conf -= penalty

    # score disagreements (outliers) further reduce confidence
    score_disagreements = aggregated.get("score_disagreements", []) or []
    if score_disagreements:
        notes.append(f"score disagreements: {len(score_disagreements)} outlier(s)")
        conf -= min(0.4, 0.15 * len(score_disagreements))

    conf = max(0.0, min(1.0, conf))
    if not notes:
        notes.append("no notable disagreements or missing values")

    return conf, notes

def export_product_result(
    aggregated_result: Dict[str, Any],
    product_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    output_dir: str = "outputs",
    as_csv: bool = False,
) -> Dict[str, str]:
    """Finalize and write product-level result files.

    Returns a dict with paths to written files, e.g. {"json": "path", "csv": "path"}
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pid = product_id or str(uuid.uuid4())
    # Use timezone-aware UTC timestamp to avoid deprecation of utcnow()
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    conf, notes = _compute_overall_confidence(aggregated_result)

    final = {
        "product_id": pid,
        "timestamp": timestamp,
        "confidence": conf,
        "confidence_notes": notes,
        "metadata": metadata or {},
        "result": aggregated_result,
    }

    json_path = out_dir / f"{pid}.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(final, fh, indent=2, ensure_ascii=False)

    csv_path = None
    if as_csv:
        # produce a flattened CSV with one row summarizing main fields
        csv_path = out_dir / f"{pid}.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            # base header and values
            base_header = ["product_id", "timestamp", "confidence", "confidence_notes", "score_mean", "score_median"]
            base_values = [pid, timestamp, f"{conf:.3f}", " | ".join(notes), None, None]

            score_summary = aggregated_result.get("score_summary", {})
            base_values[4] = score_summary.get("mean")
            base_values[5] = score_summary.get("median")

            # If visual_consensus is present, include per-dimension mean/confidence/disagreement columns
            vc = aggregated_result.get("visual_consensus") or {}
            vc_header = []
            vc_values = []
            if vc:
                # stable iteration order for columns
                for dim in sorted(vc.keys()):
                    vc_header.extend([f"{dim}_mean", f"{dim}_confidence", f"{dim}_disagreement"])
                    info = vc.get(dim, {}) or {}
                    vc_values.extend([
                        info.get("mean"),
                        info.get("confidence"),
                        bool(info.get("disagreement")),
                    ])

            header = base_header + vc_header
            values = base_values + vc_values

            writer.writerow(header)
            writer.writerow(values)

    result = {"json": str(json_path)}
    if csv_path:
        result["csv"] = str(csv_path)
    return result


__all__ = ["export_product_result"]
