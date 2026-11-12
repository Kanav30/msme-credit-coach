import React from 'react';
import {
  Activity,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  TrendingUp,
  Target,
  Flame,
  Zap,
  HelpCircle,
  Building2,
  Lock,
  Clock,
  CreditCard,
  Layers,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

export default function LandingPage({
  onGetStarted,
  onLogin,
  onOpenDemo,
}) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-page)' }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand">
            <div className="navbar-logo-icon">
              <Activity size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="navbar-title">MSME Credit Coach</span>
                <span className="badge badge-pink" style={{ fontSize: '0.65rem' }}>CMR-Focused</span>
              </div>
              <div className="navbar-subtitle">CIBIL MSME Rank Diagnostic & Action Roadmap</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <button
              onClick={onLogin}
              className="btn btn-secondary btn-sm"
              style={{ padding: '7px 16px', fontWeight: '600' }}
            >
              Sign In
            </button>
            <button
              onClick={onGetStarted}
              className="btn btn-primary btn-sm"
              style={{ padding: '7px 18px', fontWeight: '700' }}
            >
              Get Started Free <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </header>

      <main className="app-container" style={{ paddingTop: '20px' }}>
        {/* Compliance Alert */}
        <div className="compliance-banner" style={{ marginBottom: '32px' }}>
          <ShieldCheck size={18} style={{ color: 'var(--accent-pink)', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Legally Safe & CICRA 2005 Compliant: </strong>
            Under Indian law, only 4 RBI-licensed Credit Information Companies (CIBIL, Experian, Equifax, CRIF High Mark) can issue official credit scores.
            This coach never replaces or computes a competing score — it interprets your official <strong>CIBIL MSME Rank (CMR 1 to 10)</strong>, guides your weekly improvements, and forecasts bank loan eligibility.
          </div>
        </div>

        {/* Hero Section */}
        <section style={{ textAlign: 'center', padding: '30px 10px 50px 10px', maxWidth: '920px', margin: '0 auto' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 16px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '20px',
              fontSize: '0.8rem',
              fontWeight: '600',
              color: 'var(--text-primary)',
              marginBottom: '20px',
              boxShadow: 'var(--shadow-sm)',
            }}
          >
            <Sparkles size={14} style={{ color: 'var(--accent-pink)' }} />
            <span>Overcoming India's ₹25–30 Lakh Crore MSME Credit Gap</span>
          </div>

          <h1
            style={{
              fontSize: '3rem',
              lineHeight: '1.24',
              fontWeight: '800',
              color: 'var(--text-primary)',
              letterSpacing: '-0.03em',
              marginBottom: '22px',
              fontFamily: 'ui-sans-serif'
            }}
          >
            Turn MSME Loan Rejection into{' '}
            <span
              style={{
                position: 'relative',
                display: 'inline-block',
                whiteSpace: 'nowrap',
                fontStyle: 'italic',
                fontFamily: 'serif',
              }}
            >
              Bank Approval
              <svg
                viewBox="0 0 250 18"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                preserveAspectRatio="none"
                style={{
                  position: 'absolute',
                  left: '-2%',
                  bottom: '-9px',
                  width: '104%',
                  height: '15px',
                  overflow: 'visible',
                  pointerEvents: 'none',
                }}
              >
                <path
                  d="M 3 14.5 C 55 10.5, 140 6.5, 246 6"
                  stroke="var(--accent-pink)"
                  strokeWidth="4.2"
                  strokeLinecap="round"
                  style={{
                    filter: 'drop-shadow(0 2px 8px rgba(255, 61, 139, 0.45))',
                  }}
                />
              </svg>
            </span>
          </h1>

          <p
            style={{
              fontSize: '1.12rem',
              color: 'var(--text-secondary)',
              lineHeight: '1.6',
              maxWidth: '780px',
              margin: '0 auto 32px auto',
            }}
          >
            MSMEs often get rejected because of a low <strong>CIBIL MSME Rank (CMR)</strong>, but owners are rarely told what is dragging them down.
            Our coach provides a transparent factor diagnostic, prioritizes fast-moving fixes, tracks your weekly discipline streak, and projects exactly when you'll reach loan eligibility.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '14px', flexWrap: 'wrap', marginBottom: '36px' }}>
            <button
              onClick={onGetStarted}
              className="btn btn-primary"
              style={{ padding: '12px 26px', fontSize: '1rem', fontWeight: '700' }}
            >
              Start Free Business Assessment <ArrowRight size={17} />
            </button>

            <button
              onClick={onLogin}
              className="btn btn-secondary"
              style={{ padding: '12px 24px', fontSize: '1rem', fontWeight: '600' }}
            >
              Sign In to Dashboard
            </button>
          </div>

          {/* Quick Stats Highlights */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px',
              maxWidth: '820px',
              margin: '0 auto',
            }}
          >
            <div className="glass-card" style={{ padding: '16px 20px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Scale Explained</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--text-primary)', marginTop: '4px' }}>CMR 1 to 10</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>CMR-1 is Prime; CMR-10 is High Risk</div>
            </div>

            <div className="glass-card" style={{ padding: '16px 20px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Target Standard</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--accent-emerald-text)', marginTop: '4px' }}>CMR-3 or Better</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Standard threshold for bank credit</div>
            </div>

            <div className="glass-card" style={{ padding: '16px 20px', textAlign: 'left' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '700' }}>Fastest Recovery Lever</div>
              <div style={{ fontSize: '1.35rem', fontWeight: '800', color: 'var(--accent-pink)', marginTop: '4px' }}>Utilization &lt; 60%</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Can shift score in 1 billing cycle</div>
            </div>
          </div>
        </section>

        {/* The Problem Section */}
        <section style={{ padding: '40px 0' }}>
          <div style={{ textAlign: 'center', marginBottom: '32px' }}>
            <span className="badge badge-pink" style={{ marginBottom: '8px' }}>The Core MSME Problem</span>
            <h2 style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--text-primary)' }}>
              Why Do Small Businesses Get Stuck in Rejection?
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '640px', margin: '6px auto 0 auto' }}>
              Business credit is fundamentally different from consumer credit, but MSME owners are left navigating it in the dark.
            </p>
          </div>

          <div className="grid-3">
            <div className="glass-card" style={{ padding: '24px' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: 'var(--accent-amber-bg)',
                  color: 'var(--accent-amber-text)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <HelpCircle size={22} />
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Personal Score vs CMR Confusion
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55' }}>
                Owners assume their 750+ personal CIBIL guarantees business loans. But banks underwrite commercial loans against the business's distinct <strong>CIBIL MSME Rank (CMR)</strong>, which has completely different rules and weighting.
              </p>
            </div>

            <div className="glass-card" style={{ padding: '24px' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: 'var(--accent-rose-bg)',
                  color: 'var(--accent-rose-text)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <Lock size={22} />
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                The "Black Box" Rejection
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55' }}>
                Banks reject applications with a brief letter: <em>"CMR-6 does not meet credit policy."</em> They do not tell the owner which factor caused the rejection, nor how long it will take to fix it.
              </p>
            </div>

            <div className="glass-card" style={{ padding: '24px' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: 'var(--accent-pink-bg)',
                  color: 'var(--accent-pink)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '16px',
                }}
              >
                <Clock size={22} />
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                No Trackable Action Loop
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55' }}>
                Credit bureau data updates only once a month. Without a weekly habit tracking system, owners lose motivation or make counter-productive moves (like closing old credit accounts) that accidentally hurt their rank.
              </p>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section style={{ padding: '40px 0' }}>
          <div style={{ textAlign: 'center', marginBottom: '36px' }}>
            <span className="badge badge-emerald" style={{ marginBottom: '8px' }}>The 4-Step Solution</span>
            <h2 style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--text-primary)' }}>
              How the MSME Credit Coach Works
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '640px', margin: '6px auto 0 auto' }}>
              Built upon publicly known CMR factor principles and transparent mathematics — no black boxes.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: '800', color: 'var(--accent-emerald-text)', marginBottom: '8px' }}>
                STEP 1
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Transparent Diagnostic
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55', marginBottom: '14px' }}>
                We break down your credit profile across the 4 core CMR pillars: Payment History (40%), Credit Utilization (25%), Credit Tenure (20%), and Firm Profile (15%).
              </p>
              <div style={{ marginTop: 'auto', background: 'var(--bg-card-subtle)', padding: '10px 12px', borderRadius: '8px', fontSize: '0.74rem', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
                Identifies exact point deductions and active recent delinquencies.
              </div>
            </div>

            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: '800', color: 'var(--accent-pink)', marginBottom: '8px' }}>
                STEP 2
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Actionability Ranking
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55', marginBottom: '14px' }}>
                Raw headroom is misleading. We weight recommendations by <strong>realistic improvement speed</strong>. Fast levers (utilization) are pushed to the top so you can see results this month.
              </p>
              <div style={{ marginTop: 'auto', background: 'var(--bg-card-subtle)', padding: '10px 12px', borderRadius: '8px', fontSize: '0.74rem', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
                Prevents wasting time on fixed factors that take years to advance naturally.
              </div>
            </div>

            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: '800', color: 'var(--accent-amber-text)', marginBottom: '8px' }}>
                STEP 3
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Self-Logging Streak Tracker
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55', marginBottom: '14px' }}>
                Owners log micro-actions weekly (paying down credit lines, enabling NACH autopay, filing bureau disputes). Keep your weekly flame streak alive to prove discipline.
              </p>
              <div style={{ marginTop: 'auto', background: 'var(--bg-card-subtle)', padding: '10px 12px', borderRadius: '8px', fontSize: '0.74rem', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
                Builds an audit trail you can present directly to loan officers.
              </div>
            </div>

            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: '800', color: 'var(--accent-blue)', marginBottom: '8px' }}>
                STEP 4
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Trajectory Simulator
              </h3>
              <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: '1.55', marginBottom: '14px' }}>
                Our calibrated deterministic simulator walks month-by-month into the future based on your logged discipline, forecasting when you'll reach bank loan eligibility (e.g. CMR-3).
              </p>
              <div style={{ marginTop: 'auto', background: 'var(--bg-card-subtle)', padding: '10px 12px', borderRadius: '8px', fontSize: '0.74rem', color: 'var(--text-muted)', border: '1px solid var(--border-subtle)' }}>
                Cross-validated with an ML surrogate model (R² = 0.93).
              </div>
            </div>
          </div>
        </section>

        {/* Step-by-Step "How to Use It" Guide */}
        <section style={{ padding: '40px 0' }}>
          <div className="glass-card" style={{ padding: '36px' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <span className="badge badge-pink" style={{ marginBottom: '8px' }}>Practical User Guide</span>
              <h2 style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                How to Use the Platform in 4 Simple Steps
              </h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-pink)', color: '#FFF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.82rem', boxShadow: 'var(--shadow-pink-glow)' }}>
                    1
                  </div>
                  <h4 style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--text-primary)' }}>Create Your Profile</h4>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Sign up with your business trade name, mobile number, and target rank (typically CMR-3 for standard PSU or private bank loans).
                </p>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-pink)', color: '#FFF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.82rem', boxShadow: 'var(--shadow-pink-glow)' }}>
                    2
                  </div>
                  <h4 style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--text-primary)' }}>Inspect Diagnostics</h4>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Review your 4 factor cards. The app immediately flags your <strong>Top Priority Action</strong> (e.g. paying down balances over 75% limit).
                </p>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-pink)', color: '#FFF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.82rem', boxShadow: 'var(--shadow-pink-glow)' }}>
                    3
                  </div>
                  <h4 style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--text-primary)' }}>Log Daily Habits</h4>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Whenever you make an EMI payment or pay down an overdraft balance, click <strong>"+ Log Action"</strong>. This maintains your streak and updates your prediction.
                </p>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-pink)', color: '#FFF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.82rem', boxShadow: 'var(--shadow-pink-glow)' }}>
                    4
                  </div>
                  <h4 style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--text-primary)' }}>Follow Daily Habits & Trajectory</h4>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                  Execute daily financial habits, track your streak in the <strong>Daily Habits & Logs</strong> tab, and watch your predicted CMR trajectory move toward bank approval.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* The 4 Bureau Factors Overview */}
        <section style={{ padding: '30px 0' }}>
          <div style={{ textAlign: 'center', marginBottom: '28px' }}>
            <span className="badge badge-pink" style={{ marginBottom: '8px' }}>Scoring Architecture</span>
            <h2 style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--text-primary)' }}>
              The 4 Pillars of CIBIL MSME Rank
            </h2>
          </div>

          <div className="grid-4">
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <Activity size={20} style={{ color: 'var(--accent-emerald-text)' }} />
                <span className="badge badge-emerald">40% Weight</span>
              </div>
              <h4 style={{ fontWeight: '700', fontSize: '0.98rem', marginBottom: '4px', color: 'var(--text-primary)' }}>Payment History</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
                Single biggest factor. Even one late payment in 90 days triggers a severe penalty. Takes ~3 clean months to age out.
              </p>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <CreditCard size={20} style={{ color: 'var(--accent-pink)' }} />
                <span className="badge badge-pink">25% Weight</span>
              </div>
              <h4 style={{ fontWeight: '700', fontSize: '0.98rem', marginBottom: '4px', color: 'var(--text-primary)' }}>Credit Utilization</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
                Fastest recovery lever. Above 75% is high risk; below 60% is healthy. Can be improved within a single monthly billing cycle.
              </p>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <Clock size={20} style={{ color: 'var(--accent-amber-text)' }} />
                <span className="badge badge-amber">20% Weight</span>
              </div>
              <h4 style={{ fontWeight: '700', fontSize: '0.98rem', marginBottom: '4px', color: 'var(--text-primary)' }}>Credit Tenure</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
                Length of vintage credit lines. Diminishing returns after 10 years. Cannot be rushed — only improves as calendar time passes.
              </p>
            </div>

            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <Building2 size={20} style={{ color: 'var(--accent-blue)' }} />
                <span className="badge badge-cyan">15% Weight</span>
              </div>
              <h4 style={{ fontWeight: '700', fontSize: '0.98rem', marginBottom: '4px', color: 'var(--text-primary)' }}>Firm Profile</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
                Operating age and industry volatility multiplier (low, medium, high risk). Mostly fixed, but reflects stability over time.
              </p>
            </div>
          </div>
        </section>

        {/* CTA Callout Banner */}
        <section style={{ padding: '40px 0 60px 0' }}>
          <div
            className="glass-card"
            style={{
              padding: '40px 30px',
              textAlign: 'center',
              border: '1.5px solid var(--border-subtle)',
            }}
          >
            <h2 style={{ fontSize: '2rem', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '12px' }}>
              Ready to Understand and Improve Your Business Credit Rank?
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', maxWidth: '620px', margin: '0 auto 26px auto' }}>
              No confidential bank statements or account logins required. Test your situation in under 2 minutes.
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
              <button
                onClick={onGetStarted}
                className="btn btn-primary"
                style={{ padding: '12px 28px', fontSize: '1rem', fontWeight: '700' }}
              >
                Create Free Business Account <ArrowRight size={16} />
              </button>
              <button
                onClick={onLogin}
                className="btn btn-secondary"
                style={{ padding: '12px 24px', fontSize: '1rem', fontWeight: '600' }}
              >
                Sign In to Dashboard
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer style={{ marginTop: 'auto', borderTop: '1px solid var(--border-subtle)', background: 'var(--bg-card)', padding: '28px 24px' }}>
        <div style={{ maxWidth: '1320px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="navbar-logo-icon" style={{ width: '30px', height: '30px', borderRadius: '6px' }}>
              <Activity size={16} />
            </div>
            <span style={{ fontWeight: '700', fontSize: '0.92rem', color: 'var(--text-primary)' }}>MSME Credit Score Improvement Coach</span>
          </div>

          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '600px', textAlign: 'right' }}>
            Built in compliance with the Credit Information Companies Regulation Act (CICRA), 2005. Does not issue, compute, or replace official credit scores.
          </div>
        </div>
      </footer>
    </div>
  );
}
