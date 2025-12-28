"""schema.py
Pydantic models and validators for all external-facing JSON data.

Models validate numeric ranges, required fields, enums, and forbid extra
fields to prevent garbage or unexpected AI outputs from propagating.
"""
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, ValidationError, RootModel, ConfigDict



class VisualScore(BaseModel):
    # A1.0 requires scores in [-5.0, 5.0]
    score: float = Field(..., ge=-5.0, le=5.0)
    justification: str = Field(..., min_length=1)
    uncertain: bool

    model_config = ConfigDict(extra="forbid")


class VisualMeasurements(BaseModel):
    gender_expression: VisualScore
    visual_weight: VisualScore
    embellishment: VisualScore
    unconventionality: VisualScore
    formality: VisualScore

    model_config = ConfigDict(extra="forbid")


def validate_visual_measurements(data: dict) -> VisualMeasurements:
    return VisualMeasurements.model_validate(data)




def validate_visual_score(data: dict) -> VisualScore:
    """Validate a VisualScore-like dict. Raises on invalid input."""
    return VisualScore.model_validate(data)


class ImageAnalysis(BaseModel):
    image_id: str
    visual_measurements: VisualMeasurements
    attributes: dict[str, object] = Field(default_factory=dict)
    confidence_notes: Optional[str] = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def validate_image_analysis(data: dict) -> ImageAnalysis:
    return ImageAnalysis.model_validate(data)


__all__ = ["VisualScore", "validate_visual_score", "validate_visual_measurements", "validate_image_analysis", "ValidationError"]
