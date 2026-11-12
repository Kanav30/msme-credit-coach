# MSME Credit Health & Score Improvement Coach — Frontend

A modern, responsive, high-performance web frontend built with **React 19**, **Vite**, and **Vanilla CSS** for the MSME Credit Score Improvement Coach.

---

## Features

1. **Owner Coach View**:
   - **CIBIL MSME Rank (CMR) Gauge**: Semi-circular visual SVG meter mapping proxy scores to official CMR ranks (1 to 10), risk tier badge (Prime, Monitored, High Risk), and gap to target rank.
   - **Habit & Streak Tracker**: Animated flame streak counter tracking consecutive weeks of logged improvements, complete action timeline, and reset triggers.
   - **4 Factor Diagnostic Cards**: Dedicated cards for **Payment History** (~40%), **Credit Utilization** (~25%), **Credit Tenure** (~20%), and **Firm Profile** (~15%) ordered by **Actionable Priority** (combining headroom and improvement speed).
   - **Action Logging Modal**: Quick presets for high-leverage actions (e.g. balance paydown, autopay configuration, dispute filing), updating streak and trajectory forecasts in real time.
   - **Projected Trajectory Chart**: Responsive SVG visualization plotting projected rank improvements month-by-month, indicating target milestone month and displaying Random Forest ML cross-validation scores ($R^2 = 0.93$).
   - **Alternate Data Signals**: Interactive sliders for trailing 6-month GST filing regularity and UPI cash flow stability, providing supplementary early indicators.

2. **Lender & Loan Consultant Audit View**:
   - Underwriting summary with probability of default (PD) range estimates.
   - Full factor explainability matrix with weights and attribution.
   - Verified borrower action audit trail.
   - CICRA 2005 regulatory compliance statement.

3. **What-If Scenario Sandbox**:
   - Real-time sliders for credit utilization, on-time payment track, tenure, firm age, and target rank.
   - Monthly effort toggles to simulate varying discipline scenarios with instant trajectory recalculation.

4. **Multi-Business Archetype Selector**:
   - Seamlessly switch between 5 realistic MSME archetypes (Struggling, Healthy, Thin-file, Maxed-out utilization, Mediocre) or customize your business profile.

---

## Quickstart

### 1. Start the Backend API (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Backend API docs available at: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (Vite)
```bash
cd frontend
npm install
npm run dev
```
Visit: `http://localhost:5173/`
Vite proxies all `/api/*` calls directly to the FastAPI server at `http://127.0.0.1:8000`.
