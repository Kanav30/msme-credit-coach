"""
Alternate Data Enrichment (Phase 4 — stretch goal).

CRITICAL DESIGN RULE: this module NEVER touches or blends into the core CMR
proxy score (feature_engineering.py) or the trajectory prediction
(trajectory_simulator.py / trajectory_model.py). Those remain exactly as
validated in Phases 1-3.

GST filing regularity and UPI cash-flow stability are NOT official CMR
inputs — CIBIL doesn't use them. This module treats them purely as a
SEPARATE, supplementary "early signal" layer: a leading indicator that
might show a business's trajectory shifting before it's reflected in their
official bureau history (which typically updates monthly). It is explicitly
NOT a replacement, a proxy, or a competing score.
"""

from dataclasses import dataclass


@dataclass
class AlternateDataSignals:
    """Optional inputs, entirely separate from BusinessCreditProfile."""
    gst_filing_regularity: float   # 0-1: share of GST returns filed on/before due date (trailing 6 months)
    upi_inflow_stability: float    # 0-1: higher = more consistent UPI cash inflows (e.g. 1 - coefficient of variation, clipped to [0,1])


def compute_supplementary_signal(signals: AlternateDataSignals) -> dict:
    """
    Returns a supplementary 0-100 signal and a plain-language trend label.
    This is intentionally simple (equal-weighted average) — the point of
    this layer is directional signal, not precision, and it should never
    be dressed up to look more authoritative than the core diagnostic.
    """
    combined = (signals.gst_filing_regularity * 0.5 + signals.upi_inflow_stability * 0.5) * 100

    if combined >= 75:
        trend_label = "Positive early signal — recent GST/UPI activity suggests improving financial discipline."
    elif combined >= 50:
        trend_label = "Neutral early signal — no strong indication either way from GST/UPI activity."
    else:
        trend_label = "Caution — recent GST/UPI activity suggests emerging stress not yet reflected in bureau history."

    return {
        "supplementary_score": round(combined, 1),
        "trend_label": trend_label,
        "disclaimer": (
            "This is a supplementary, non-certified signal derived from GST/UPI patterns. "
            "It is NOT part of the CIBIL MSME Rank, does not affect the core diagnostic or "
            "prediction above, and should never be treated as a substitute for the official score."
        ),
    }
