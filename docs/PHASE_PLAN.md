# Phase Plan — MSME Credit Score Improvement Coach

Simpler than the original plan since this version doesn't need any regulated
data integration (GST/UPI/AA) to have a working core product — that's now a
stretch goal in Phase 4, not a dependency for everything else.

### Phase 0 — Foundations (Weeks 1–4)
- Python data stack: pandas, numpy, matplotlib, scikit-learn basics
- Research: how CMR is actually calculated — read up on the public factor
  weights (payment history, credit utilization, credit tenure, firm profile)
- Read up on FixMyScore and similar tools for positioning context

### Phase 1 — Diagnostic Engine (Weeks 5–8)
- Build a rule-based scoring breakdown from the known public CMR factors
  (not a trained model — this part should be transparent and explainable
  by design, since you're interpreting a real score, not predicting a new one)
- Build the gap-to-target calculator: current score → target score → what's costing the gap

### Phase 2 — Action Plan + Self-Logging (Weeks 9–14)
- Prioritized recommendation engine: rank fixes by impact and speed (quick wins vs. slow fixes)
- Self-logging feature: owner records actions taken, with a streak/consistency tracker
- Basic app UI: score gauge, action checklist, log history

### Phase 3 — Trajectory Prediction Model (Weeks 15–20)
- Simulate synthetic score-movement trajectories grounded in the known factor
  formulas (e.g. utilization drop of X% → expected point movement over Y months)
- Train a lightweight regression model on these simulated trajectories
- Output: "if you keep this up for N months, expect to move from CMR-X to CMR-Y"
- Be upfront in your report: this is a calibrated estimate, not a certified prediction

### Phase 4 — Alternate Data Enrichment (Weeks 21–26) — stretch goal
- Add GST filing regularity / UPI cash flow stability as supplementary leading
  indicators alongside the core CMR-factor model
- Frame explicitly as "early signal," never as a replacement for the real score

### Phase 5 — Real User Testing (Weeks 27–32)
- This pivot's biggest advantage: get actual MSME owners (or a CA who works
  with them) to try it with their real CMR/CIBIL numbers
- Collect feedback on whether the recommendations feel accurate and the
  logging habit is easy enough to stick with

### Phase 6 — Polish, Docs, Demo, Pitch Prep (Weeks 33–40)
- UI polish based on real feedback
- Write up methodology (doubles as your report)
- Demo video + slide deck
- Target relevant MSME/fintech hackathons for external validation

*(~9-10 months total — compress Phase 0 if you're already comfortable with the basics from earlier practice.)*
