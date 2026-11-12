# MSME Credit Score Improvement Coach

### An AI-guided coaching app that helps MSMEs understand and improve their CIBIL MSME Rank (CMR) — without creating a competing score.

---

## The Elevator Pitch

> "MSMEs get rejected for loans because of a low CIBIL MSME Rank (CMR), but most owners have no idea what's actually dragging their score down or how long it'll take to fix. We built an app that reads official TransUnion CIBIL CIR reports, analyzes the 4 documented CMR scoring factors, tells the owner exactly what to fix and in what priority order, tracks weekly actions, and predicts when they'll hit the score a lender needs — all without touching or replacing the official bureau score itself."

---

## The Problem

- India's MSME credit gap is roughly ₹25–30 lakh crore, with formal credit penetration around 14%.
- MSMEs have a business-specific credit rank — the **CIBIL MSME Rank (CMR)**, scaled from 1 (best) to 10 (riskiest) — separate from the owner's personal CIBIL score.
- A business can be denied a loan for being at CMR-6 when a lender needs CMR-3, with no clear roadmap on how to close that gap.
- Existing tools either check the score (bureaus, aggregator sites) or explain it in a generic blog post — nobody guides an MSME through a structured, trackable improvement plan.

## Why We're Not Building a New Score (CICRA 2005)

Only four RBI-licensed Credit Information Companies — TransUnion CIBIL, Experian, Equifax, CRIF High Mark — are legally authorized to compute credit scores used in lending decisions (Credit Information Companies Regulation Act, 2005). This product **never computes or issues a competing score**. It interprets and coaches around the *existing* official score the MSME already has. This keeps it legally safe, compliant, and realistic to build and test.

## How It Works

1. **Ingestion & Input** — the owner can either upload their official TransUnion CIBIL CIR report (.pdf) for auto-extraction, select a realistic archetype, or enter their baseline metrics.
2. **Diagnostic breakdown** — using documented CMR factors (payment history ~40%, credit utilization, credit tenure, firm profile), the app shows exactly what's costing them rank points.
3. **Prioritized action plan** — recommendations sorted by **Actionability Priority**: quick wins (lowering utilization, clearing recent delays) vs. slower fixes (building credit tenure).
4. **Self-logging** — the owner logs actions taken weekly ("paid down overdraft by ₹50,000," "activated NACH mandate"), building a visible streak over the calendar weeks.
5. **Trajectory prediction** — using known factor weights plus logged actions, the app estimates a probable rank movement and timeline ("keep this up for 3 more months, expect to move from CMR-6 to CMR-3").
6. **Alternate data enrichment** — GST filing regularity and UPI cash flow stability used as early, supplementary signals that move *before* the monthly bureau update.

## Why This Is Different

| Dimension | FixMyScore (Credgenics) | Generic Credit Checkers | This Project |
|---|---|---|---|
| **Focus** | Individual/personal CIBIL score | Consumer score pull | MSME business credit rank (CMR 1 to 10) |
| **Framing** | General score improvement | Lead gen for credit cards | Explicit gap-to-loan-eligibility (e.g. CMR-3) |
| **Tracking** | Score monitoring | Periodic email alerts | Self-logged action streaks tied to a prediction timeline |
| **Ingestion** | User credentials pull | Bureau API lead capture | Document parser for official CIBIL CIR PDF reports |

## Tech Stack

- **Backend**: Python (FastAPI)
- **Ingestion & Document Parsing**: `pypdf` (CIBIL PDF parser) & `reportlab` (authentic CIBIL CIR generator)
- **Diagnostic Engine**: Rule-based, built from published CMR factor weights and actionability weighting
- **Prediction Model**: Calibrated deterministic simulator + Random Forest regression surrogate ($R^2 \approx 0.93$)
- **Frontend**: React 19 + Vite + Vanilla CSS — high-contrast modern theme (Navy `#0F1B3D`, Light Beige/Soft White `#FAF7F2`, and Hot Pink `#FF3D8B`), score gauge, daily habits & logs tracker, structured multi-step factor playbooks, trajectory chart, CIBIL upload tab, what-if sandbox, and educational landing page
- **Database**: Persistent SQLite (`app_data.db`) storing users (SHA-256 hashed) and action logs; ready for PostgreSQL / Supabase migration

## Honest Pros / Cons

**Pros**: legally compliant (no CIC licensing conflict), handles real bureau PDF documents without expensive B2B API contracts, realistic MSME owners and CAs can test it with actual reports, clear differentiation from consumer credit tools.

**Cons**: self-reported logging must be verified against actual bureau monthly updates (bureaus update monthly, not live), requires clear UX so users understand the difference between personal score (300-900) and commercial rank (CMR 1-10).

## Future Scope

- Real-data pilot with a CA/loan consultant who works directly with MSME clients
- WhatsApp-based logging for lower-friction daily/weekly updates
- Vernacular-language support for tier-2/3/4 town MSME owners
