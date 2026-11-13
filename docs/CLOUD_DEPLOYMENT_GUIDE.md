# Cloud Deployment & Infrastructure Guide

This guide details the complete production cloud architecture and step-by-step deployment procedure for the **MSME Credit Improvement Coach** platform, operating 100% on free-tier, enterprise-grade cloud services with zero server maintenance overhead.

---

## 1. Cloud Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION CLOUD TOPOLOGY                         │
└────────────────────────────────────────────────────────────────────────┘

    Client Browser (MSME Owner / Chartered Accountant / Evaluator)
                               │
                               │ HTTPS / TLS 1.3
                               ▼
        ┌──────────────────────────────────────────────┐
        │        Vercel Global Edge CDN (Frontend)     │
        │  • Framework: React 18 + Vite                │
        │  • Styling: High-contrast Navy & Hot Pink    │
        │  • SPA Routing: vercel.json rewrite to index │
        │  • Env: VITE_BACKEND_URL                     │
        └──────────────────────┬───────────────────────┘
                               │
                               │ RESTful JSON over HTTPS (Port 443)
                               ▼
        ┌──────────────────────────────────────────────┐
        │       Render.com Web Service (Backend)       │
        │  • Engine: FastAPI + Uvicorn (Python 3.11)   │
        │  • Workers: Asynchronous event loop          │
        │  • ML Engine: Scikit-learn Ridge Regression  │
        │  • PDF Engine: ReportLab + PyPDF CIR Parser  │
        └──────────────────────┬───────────────────────┘
                               │
                               │ Native MySQL Protocol + TLS (Port 4000)
                               ▼
        ┌──────────────────────────────────────────────┐
        │   TiDB Cloud Serverless (MySQL Database)     │
        │  • Provider: AWS Singapore (ap-southeast-1)  │
        │  • Architecture: Distributed NewSQL / MySQL  │
        │  • Storage: 5 Normalized Relational Tables   │
        │  • Security: Encrypted in transit (SSL/TLS)  │
        └──────────────────────────────────────────────┘
```

---

## 2. TiDB Cloud Serverless Database Setup (Already Active)

- **Cluster Name:** `msme-credit-coach`
- **Region:** AWS Singapore (`ap-southeast-1`)
- **Compatibility:** MySQL 8.0 Wire Protocol
- **Connection Host:** `gateway01.ap-southeast-1.prod.aws.tidbcloud.com`
- **Port:** `4000`
- **User:** `<YOUR_TIDB_USERNAME>` (from TiDB Cloud console)
- **Database:** `test`
- **SSL Requirement:** Required (`MYSQL_SSL=true`)

### Normalized Relational Schema (BCNF)
The cloud database hosts 5 tables:
1. `users` — Authentication credentials with salted PBKDF2 hashes.
2. `business_credit_profiles` — Core financial, utilization, and vintage parameters per MSME.
3. `cibil_cir_reports` — Extracted metadata from ingested TransUnion CIBIL CIR documents.
4. `logged_actions` — Timestamped record of daily borrower habits with weekly streak attribution.
5. `alternate_data_signals` — Supplementary GST filing and UPI transaction health metrics.

---

## 3. Render Backend Deployment (FastAPI)

1. Open [dashboard.render.com](https://dashboard.render.com/) and authenticate with GitHub.
2. Click **New +** $\to$ **Web Service**.
3. Choose the repository: **`Kanav30/msme-credit-coach`**.
4. Configure service parameters:
   - **Name:** `msme-credit-coach-api`
   - **Region:** `Singapore (Southeast Asia)`
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`
5. Configure Environment Variables in Render Dashboard (Never commit raw passwords to Git):
   ```env
   DB_ENGINE=mysql
   MYSQL_HOST=gateway01.ap-southeast-1.prod.aws.tidbcloud.com
   MYSQL_PORT=4000
   MYSQL_USER=YOUR_TIDB_USERNAME
   MYSQL_PASSWORD=YOUR_TIDB_PASSWORD
   MYSQL_DATABASE=test
   MYSQL_SSL=true
   APP_ENV=production
   JWT_SECRET=YOUR_SECURE_RANDOM_JWT_SECRET_KEY
   ```
6. Click **Deploy Web Service**.
7. Note down your public backend URL: `https://<YOUR-RENDER-APP>.onrender.com`.

---

## 4. Vercel Frontend Deployment (React + Vite)

1. Open [vercel.com](https://vercel.com/) and authenticate with GitHub.
2. Click **Add New...** $\to$ **Project**.
3. Import **`Kanav30/msme-credit-coach`**.
4. Configure project settings:
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click **Edit** and select `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Configure Environment Variables:
   ```env
   VITE_BACKEND_URL=https://<YOUR-RENDER-APP>.onrender.com
   ```
   *(Ensure no trailing slash)*
6. Click **Deploy**.
7. Deployment completes within ~40 seconds with a production HTTPS domain (e.g., `https://msme-credit-coach.vercel.app`).

---

## 5. End-to-End Verification Checklist

| Step | Action | Expected Result |
| :---: | :--- | :--- |
| 1 | Visit `https://<backend>.onrender.com/health` | `{"status": "healthy"}` |
| 2 | Visit `https://<frontend>.vercel.app/` | Landing page renders in Navy & Hot Pink theme |
| 3 | Check Navigation Bar status indicator | **🟢 Cloud MySQL: Connected** |
| 4 | Register new user via Auth Page | User account created and persisted to TiDB Cloud |
| 5 | Log daily financial action | Action timestamped in `logged_actions` table |
| 6 | Upload CIBIL CIR sample report | PDF parsed and profile updated in real-time |
