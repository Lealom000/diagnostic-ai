"""
Deterministic Tools — Section 20 of diagnostic-ai-blueprint-v6.md.

Exact operations, performed by plain code, never left to the LLM.
"""

from __future__ import annotations


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5 / 9


def is_in_range(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def example_vital_sign_subscore(
    value: float, bands: list[tuple[float, float, int]], default: int = 0
) -> int:
    """
    Generic illustrative pattern for how a deterministic
    early-warning-style subscore could be structured — a sequence of
    (low, high, score) bands.

    This is NOT derived from, and must not be presented as, any
    specific named clinical scoring system. A real implementation
    must use a properly licensed, validated scoring system with
    clinician sign-off before it is used beyond synthetic test cases.
    """
    for low, high, score in bands:
        if low <= value <= high:
            return score
    return default
