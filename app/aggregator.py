"""
aggregator.py

Aggregate multiple A1.0 visual analysis results into a single
product-level consensus.

Key design principles:
- Each visual dimension is aggregated independently (A1.0 semantics)
- Aggregation is conservative: disagreement is surfaced, not hidden
- Attributes are voted on rather than averaged
- Uncertainty is preserved explicitly
"""

from statistics import mean, median
from typing import Iterable, List, Dict, Any, Tuple
from collections import Counter

# Conservative threshold used to flag wide disagreement across images.
# If the score range exceeds this value, the dimension is marked as disputed.
_DISAGREEMENT_RANGE_THRESHOLD = 4.0


def summarize_measurements(values: Iterable[float]) -> dict:
    """
    Compute basic descriptive statistics for a numeric measurement set.

    This helper is intentionally minimal and safe:
    - Returns only count/mean/median
    - Avoids assumptions when values are missing
    """
    vals = list(values)
    if not vals:
        return {"count": 0}

    return {
        "count": len(vals),
        "mean": mean(vals),
        "median": median(vals),
    }


# NOTE:
# A1.0 explicitly forbids collapsing different visual dimensions
# into a single composite score. Each dimension must remain independent.


def _majority_vote(items: List[Any]) -> Tuple[Any, float]:
    """
    Determine the majority value and its confidence.

    Returns:
        (winner, confidence)

    Confidence is computed as:
        winner_count / total_votes

    Important behavior:
    - 'uncertain' values are expected to be filtered by the caller
    - Ties are treated conservatively and return ("uncertain", 0.0)
    """
    if not items:
        return (None, 0.0)

    counts = Counter(items)
    most_common = counts.most_common()

    # Only one unique value → unanimous
    if len(most_common) == 1:
        val, cnt = most_common[0]
        return (val, cnt / len(items))

    # Check for tie at the highest count
    top_count = most_common[0][1]
    top_items = [v for v, c in most_common if c == top_count]

    if len(top_items) > 1:
        # Conservative fallback: ambiguity detected
        return ("uncertain", 0.0)

    val = most_common[0][0]
    return (val, top_count / len(items))


def aggregate_results(image_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate per-image A1.0 outputs into a product-level summary.

    Output structure:
        {
            visual_consensus: dimension-wise statistics,
            attribute_summary: majority-voted attributes,
            attribute_disagreements: low-confidence or conflicting attributes,
            raw: original per-image results
        }

    Aggregation rules:
    - Visual dimensions are averaged independently
    - Confidence reflects image coverage, not statistical certainty
    - Disagreement is flagged when score spread is high
    - Attributes use majority voting instead of averaging
    """

    # Maps dimension -> list of (image_index, score)
    # Index is retained for traceability/debugging
    dimension_scores: Dict[str, List[Tuple[int, float]]] = {}

    total_images = len(image_results)

    # Collect attribute votes across images
    attr_votes: Dict[str, List[Any]] = {}

    for idx, img in enumerate(image_results):
        # -----------------------------
        # Visual measurements
        # -----------------------------
        vm = img.get("visual_measurements")
        if isinstance(vm, dict):
            for dim, item in vm.items():
                if isinstance(item, dict) and item.get("score") is not None:
                    try:
                        score = float(item.get("score"))
                    except Exception:
                        # Skip malformed numeric values safely
                        continue
                    dimension_scores.setdefault(dim, []).append((idx, score))

        # -----------------------------
        # Attributes
        # -----------------------------
        attrs = img.get("attributes")
        if isinstance(attrs, dict):
            for k, v in attrs.items():
                # Attributes like dominant_colors may be lists.
                # We treat each element as an independent vote.
                if isinstance(v, (list, tuple)):
                    for vv in v:
                        attr_votes.setdefault(k, []).append(vv)
                else:
                    attr_votes.setdefault(k, []).append(v)

    # -----------------------------
    # Visual dimension aggregation
    # -----------------------------
    visual_consensus: Dict[str, Dict[str, Any]] = {}

    for dim, pairs in dimension_scores.items():
        values = [v for (_, v) in pairs]

        if values:
            mean_score = mean(values)
            score_range = [min(values), max(values)]

            # Confidence reflects how many images contributed to this dimension
            confidence = len(values) / total_images if total_images > 0 else 0.0

            # Disagreement is flagged conservatively using range spread
            disagreement = (score_range[1] - score_range[0]) > _DISAGREEMENT_RANGE_THRESHOLD

            visual_consensus[dim] = {
                "mean": mean_score,
                "range": score_range,
                "confidence": confidence,
                "disagreement": disagreement,
            }
        else:
            # Dimension was never scored by any image
            visual_consensus[dim] = {
                "mean": None,
                "range": None,
                "confidence": 0.0,
                "disagreement": False,
            }

    # -----------------------------
    # Attribute aggregation
    # -----------------------------
    attribute_summary: Dict[str, Dict[str, Any]] = {}
    attribute_disagreements: Dict[str, Any] = {}

    for attr, votes in attr_votes.items():
        counts = dict(Counter(votes))

        # Ignore 'uncertain' values when selecting a winner
        filtered_votes = [v for v in votes if v != "uncertain"]

        if not filtered_votes:
            attribute_summary[attr] = {
                "value": "uncertain",
                "confidence": 0.0,
                "counts": counts,
            }
            continue

        winner, _ = _majority_vote(filtered_votes)
        winner_count = Counter(filtered_votes)[winner]

        # Confidence is relative to total votes, not filtered votes
        confidence = winner_count / len(votes) if votes else 0.0

        attribute_summary[attr] = {
            "value": winner,
            "confidence": confidence,
            "counts": counts,
        }

        # Flag disagreement when multiple distinct values exist
        # and the winner is weak
        distinct_values = len([k for k in counts.keys() if k != "uncertain"])
        if distinct_values > 1 and confidence < 0.6:
            attribute_disagreements[attr] = {
                "counts": counts,
                "winner": winner,
                "confidence": confidence,
            }

    return {
        "visual_consensus": visual_consensus,
        "attribute_summary": attribute_summary,
        "attribute_disagreements": attribute_disagreements,
        # Raw data is preserved for transparency and debugging
        "raw": image_results,
    }
