import React, { useState, useEffect } from 'react';
import { Sliders, Play, CheckCircle2, RotateCcw, Target, ShieldCheck } from 'lucide-react';
import { api } from '../api';
import TrajectoryChart from './TrajectoryChart';

export default function WhatIfSandbox({ currentProfile, ownerId, onProfileSaved }) {
  const [profile, setProfile] = useState({
    on_time_payment_pct: currentProfile?.on_time_payment_pct ?? 0.80,
    has_recent_delinquency: currentProfile?.has_recent_delinquency ?? true,
    credit_utilization: currentProfile?.credit_utilization ?? 0.78,
    credit_tenure_years: currentProfile?.credit_tenure_years ?? 3.0,
    business_age_years: currentProfile?.business_age_years ?? 6.0,
    industry_risk_category: currentProfile?.industry_risk_category ?? 'medium',
    target_rank: currentProfile?.target_rank ?? 3,
  });

  const [effortUtilization, setEffortUtilization] = useState(true);
  const [effortPayment, setEffortPayment] = useState(true);
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync with currentProfile when changed externally
  useEffect(() => {
    if (currentProfile) {
      setProfile({
        on_time_payment_pct: currentProfile.on_time_payment_pct ?? 0.80,
        has_recent_delinquency: currentProfile.has_recent_delinquency ?? true,
        credit_utilization: currentProfile.credit_utilization ?? 0.78,
        credit_tenure_years: currentProfile.credit_tenure_years ?? 3.0,
        business_age_years: currentProfile.business_age_years ?? 6.0,
        industry_risk_category: currentProfile.industry_risk_category ?? 'medium',
        target_rank: currentProfile.target_rank ?? 3,
      });
    }
  }, [currentProfile]);

  // Run simulation whenever any hypothetical input, slider, or toggle changes
  useEffect(() => {
    let isCancelled = false;
    async function runSim() {
      setLoading(true);
      try {
        const monthlyEffort = {
          credit_utilization: effortUtilization,
          payment_history: effortPayment,
        };
        const res = await api.simulateWhatIf(
          ownerId,
          monthlyEffort,
          profile.target_rank,
          24,
          {
            on_time_payment_pct: profile.on_time_payment_pct,
            has_recent_delinquency: profile.has_recent_delinquency,
            credit_utilization: profile.credit_utilization,
            credit_tenure_years: profile.credit_tenure_years,
            business_age_years: profile.business_age_years,
            industry_risk_category: profile.industry_risk_category,
          }
        );
        if (!isCancelled) {
          setSimResult(res);
        }
      } catch (err) {
        console.error('What-if sim error:', err);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }

    const timer = setTimeout(runSim, 150);
    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [
    ownerId,
    profile.target_rank,
    profile.credit_utilization,
    profile.on_time_payment_pct,
    profile.has_recent_delinquency,
    profile.credit_tenure_years,
    profile.business_age_years,
    profile.industry_risk_category,
    effortUtilization,
    effortPayment,
  ]);

  const handleResetToCurrent = () => {
    if (currentProfile) {
      setProfile({
        on_time_payment_pct: currentProfile.on_time_payment_pct ?? 0.80,
        has_recent_delinquency: currentProfile.has_recent_delinquency ?? true,
        credit_utilization: currentProfile.credit_utilization ?? 0.78,
        credit_tenure_years: currentProfile.credit_tenure_years ?? 3.0,
        business_age_years: currentProfile.business_age_years ?? 6.0,
        industry_risk_category: currentProfile.industry_risk_category ?? 'medium',
        target_rank: currentProfile.target_rank ?? 3,
      });
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Header card */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-pink">Interactive Simulator</span>
              <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--text-primary)' }}>What-If Scenario Sandbox</h2>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Experiment with hypothetical inputs in real time. Projections update automatically and never alter your official or saved profile.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span
              className="badge badge-neutral"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.78rem',
                padding: '6px 12px',
                color: 'var(--text-secondary)',
              }}
            >
              <ShieldCheck size={14} style={{ color: '#34D399' }} /> Non-Destructive: Saved Profile Preserved
            </span>
            <button onClick={handleResetToCurrent} className="btn btn-secondary btn-sm">
              <RotateCcw size={14} /> Reset to Baseline
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Controls vs Live Trajectory */}
      <div className="grid-2">
        {/* Controls Column */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', color: 'var(--text-primary)' }}>
            Adjust Baseline Credit Inputs
          </h3>

          {/* Utilization Slider */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label className="form-label" style={{ margin: 0 }}>Credit Utilization Ratio</label>
              <span style={{ fontWeight: '700', color: profile.credit_utilization > 0.75 ? '#FB7185' : '#34D399' }}>
                {Math.round(profile.credit_utilization * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.10"
              max="1.0"
              step="0.02"
              value={profile.credit_utilization}
              onChange={(e) => setProfile({ ...profile, credit_utilization: parseFloat(e.target.value) })}
              className="custom-slider"
              style={{ width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              <span>10% (Ideal)</span>
              <span>60% (Healthy Ceiling)</span>
              <span>100% (Maxed)</span>
            </div>
          </div>

          {/* On-Time Payment Percentage */}
          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <label className="form-label" style={{ margin: 0 }}>On-Time Payment History (12 Mos)</label>
              <span style={{ fontWeight: '700', color: profile.on_time_payment_pct >= 0.95 ? '#34D399' : '#FBBF24' }}>
                {Math.round(profile.on_time_payment_pct * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0.50"
              max="1.0"
              step="0.01"
              value={profile.on_time_payment_pct}
              onChange={(e) => setProfile({ ...profile, on_time_payment_pct: parseFloat(e.target.value) })}
              className="custom-slider"
              style={{ width: '100%' }}
            />
          </div>

          {/* Recent Delinquency Toggle */}
          <div className="form-group" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card-subtle)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontWeight: '600', fontSize: '0.85rem', color: 'var(--text-primary)' }}>Late Payment in Last 90 Days?</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Causes an immediate 20-point drop in payment factor</div>
            </div>
            <button
              type="button"
              onClick={() => setProfile({ ...profile, has_recent_delinquency: !profile.has_recent_delinquency })}
              className={`btn btn-sm ${profile.has_recent_delinquency ? 'btn-danger' : 'btn-primary'}`}
            >
              {profile.has_recent_delinquency ? 'Yes (Delinquent)' : 'No (Clean)'}
            </button>
          </div>

          {/* Credit Tenure & Business Age */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div className="form-group">
              <label className="form-label">Credit Line Tenure (Years)</label>
              <input
                type="number"
                min="0.5"
                max="25"
                step="0.5"
                value={profile.credit_tenure_years}
                onChange={(e) => setProfile({ ...profile, credit_tenure_years: parseFloat(e.target.value) || 1 })}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Business Operating Age (Years)</label>
              <input
                type="number"
                min="0.5"
                max="30"
                step="0.5"
                value={profile.business_age_years}
                onChange={(e) => setProfile({ ...profile, business_age_years: parseFloat(e.target.value) || 1 })}
                className="form-input"
              />
            </div>
          </div>

          {/* Target Rank Selection */}
          <div className="form-group">
            <label className="form-label">Target Loan Eligibility Rank</label>
            <select
              value={profile.target_rank}
              onChange={(e) => setProfile({ ...profile, target_rank: parseInt(e.target.value) })}
              className="form-select"
            >
              <option value="1">CMR-1 (Super Prime / Lowest Borrowing Spread)</option>
              <option value="2">CMR-2 (Prime Commercial Tier)</option>
              <option value="3">CMR-3 (Standard Bank Lending Threshold - Recommended)</option>
              <option value="4">CMR-4 (NBFC Collateralized Loan Tier)</option>
              <option value="5">CMR-5 (Monitored Tier)</option>
            </select>
          </div>

          {/* Simulated Monthly Discipline Toggles */}
          <div style={{ marginTop: '18px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '10px' }}>
              Simulated Monthly Discipline Levers:
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.84rem', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <input
                  type="checkbox"
                  checked={effortUtilization}
                  onChange={(e) => setEffortUtilization(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent-pink)' }}
                />
                <span><strong style={{ color: 'var(--text-primary)' }}>Active Balance Paydown: </strong>Simulate 8% monthly utilization drops</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.84rem', cursor: 'pointer', color: 'var(--text-secondary)' }}>
                <input
                  type="checkbox"
                  checked={effortPayment}
                  onChange={(e) => setEffortPayment(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent-pink)' }}
                />
                <span><strong style={{ color: 'var(--text-primary)' }}>100% On-Time Discipline: </strong>Simulate clean payments & age out delinquency in 3 mos</span>
              </label>
            </div>
          </div>
        </div>

        {/* Live Simulation Output */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {simResult && (
            <TrajectoryChart
              predictionData={{
                simulator_prediction: simResult.simulator_prediction,
                assumed_effort_pattern: {
                  credit_utilization: effortUtilization,
                  payment_history: effortPayment,
                },
                regression_model_6_month_estimate: simResult.regression_model_6_month_estimate,
              }}
              targetRank={profile.target_rank}
            />
          )}

          {/* Key Simulation Insights Callout */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '10px', color: 'var(--text-primary)' }}>
              Simulation Mechanics Explained
            </h4>
            <ul style={{ paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              <li>
                <strong style={{ color: 'var(--accent-pink)' }}>Utilization is the fastest lever: </strong>Reducing balance by 8% monthly yields immediate rank improvements within 1 to 2 billing cycles.
              </li>
              <li>
                <strong style={{ color: '#FBBF24' }}>Payment history (40% weight) limits upside: </strong>If payment delinquency is not resolved, even reaching 30% utilization will cap rank at CMR-4 or 5.
              </li>
              <li>
                <strong style={{ color: '#38BDF8' }}>Tenure and age advance naturally: </strong>Every simulated month ticks tenure and operating age by +1/12th of a year automatically.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
