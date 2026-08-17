"""
Feature engineering functions for the MSME Financial Health Card.
Each function computes one of the four scoring pillars from raw input data.

These are stubs for Phase 2 — fill in the real logic once your synthetic
dataset (Phase 1) is ready. Keeping them separate like this means your
scoring pillars map 1:1 to the design discussed in docs/PROJECT_PITCH.md.
"""

import pandas as pd


def compute_revenue_stability(df: pd.DataFrame) -> pd.Series:
    """Score based on GST filing regularity and invoice consistency."""
    raise NotImplementedError("Phase 2: implement using GST filing pattern features")


def compute_cash_flow_health(df: pd.DataFrame) -> pd.Series:
    """Score based on UPI/bank transaction velocity and volatility."""
    raise NotImplementedError("Phase 2: implement using UPI transaction features")


def compute_repayment_discipline(df: pd.DataFrame) -> pd.Series:
    """Score based on any existing credit history, however thin."""
    raise NotImplementedError("Phase 2: implement using existing repayment/bureau features")


def compute_formalization_depth(df: pd.DataFrame) -> pd.Series:
    """Score based on Udyam registration completeness and EPFO contributions."""
    raise NotImplementedError("Phase 2: implement using registration/EPFO features")
