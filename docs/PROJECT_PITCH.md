# MSME Credit Score Improvement Coach

### An AI-guided coaching app that helps MSMEs understand and improve their CIBIL MSME Rank (CMR) — without creating a competing score.

---

## The Elevator Pitch

> "MSMEs get rejected for loans because of a low CIBIL MSME Rank (CMR), but most owners have no idea what's actually dragging their score down or how long it'll take to fix. We built an app that reads the known, public CMR scoring factors, tells the owner exactly what to fix and in what order, lets them log the actions they take each week, and predicts when they'll hit the score a lender needs — all without touching or replacing the official bureau score itself."

---

## The Problem

- India's MSME credit gap is roughly ₹25–30 lakh crore, with credit penetration around 14%.
- MSMEs have a business-specific credit rank — the **CIBIL MSME Rank (CMR)**, scaled 1 (best) to 10 (riskiest) — separate from the owner's personal CIBIL score.
- A business can be denied a loan for being at CMR-6 when a lender needs CMR-3, with no clear roadmap on how to close that gap.
- Existing tools either check the score (bureaus, aggregator sites) or explain it in a generic blog post — nobody guides an MSME through a structured, trackable improvement plan.

## Why We're Not Building a New Score

Only four RBI-licensed Credit Information Companies — TransUnion CIBIL, Experian, Equifax, CRIF High Mark — are legally authorized to compute credit scores used in lending decisions (Credit Information Companies Regulation Act, 2005). This product **never computes or issues a competing score**. It interprets and coaches around the *existing* official score the MSME already has. This keeps it legally safe and realistic to actually build and test.

## How It Works

1. **Input** — the owner enters their current CMR (or CIBIL score) and the target score needed for a loan they want.
2. **Diagnostic breakdown** — using publicly documented CMR factors (payment history ~40%, credit utilization, credit tenure, firm profile), the app shows exactly what's costing them rank points.
3. **Prioritized action plan** — recommendations sorted by impact and speed: quick wins (fixing report errors, lowering utilization) vs. slower fixes (building credit tenure).
4. **Self-logging** — the owner logs actions taken weekly ("paid down X," "reduced utilization to Y%"), building a visible streak over the 90-day-to-12-month window real CMR changes actually take.
5. **Trajectory prediction** — using the known factor weights plus logged actions, the app estimates a probable rank movement and timeline ("keep this up for 3 more months, expect to move from CMR-6 to CMR-4/5").
6. **(Stretch goal)** — alternate data (GST filing regularity, UPI cash flow stability) used as early, supplementary signals that may move *before* the official bureau update.

## Why This Is Different

| | FixMyScore (Credgenics, launched Jan 2026) | This project |
|---|---|---|
| Focus | Individual/personal CIBIL score | MSME business credit rank (CMR) |
| Framing | General score improvement | Explicit gap-to-loan-eligibility |
| Tracking | Score monitoring | Self-logged action streaks tied to a prediction timeline |

FixMyScore proves this category is real and fundable — it's just built for individuals, not businesses. The CMR-specific, loan-eligibility-framed, self-logging version is the open gap.

## Tech Stack

- **Backend**: Python (FastAPI)
- **Diagnostic engine**: rule-based, built from published CMR factor weights (not a black box)
- **Prediction model**: simple regression/trajectory simulation trained on synthetic score-movement patterns, calibrated against known factor formulas
- **Frontend**: React — dashboard with score gauge, action checklist, streak tracker, projected timeline
- **Database**: PostgreSQL/SQLite for storing logged actions and score history

## Honest Pros / Cons

**Pros**: legally safe (no licensing conflict), genuinely buildable without any regulated data access, real MSME owners can actually test it (self-report their own score), clear differentiation from the one existing competitor.

**Cons**: self-reported logging can't be instantly verified against a real score change (bureaus update monthly, not live), less flashy than a "bank dashboard" demo, needs a real design effort to make the habit-tracking loop actually engaging rather than a boring checklist.

## Future Scope

- Real-data pilot with a CA/loan consultant who works directly with MSME clients
- WhatsApp-based logging for lower-friction daily/weekly updates
- Vernacular-language support for tier-2/3/4 town MSME owners
