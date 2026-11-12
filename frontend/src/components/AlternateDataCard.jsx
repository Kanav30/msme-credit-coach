import React, { useState, useEffect } from 'react';
import { Layers, Info, CheckCircle2, AlertTriangle } from 'lucide-react';
import { api } from '../api';

export default function AlternateDataCard({ ownerId, initialGst = 0.8, initialUpi = 0.8 }) {
  const [gst, setGst] = useState(initialGst);
  const [upi, setUpi] = useState(initialUpi);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setGst(initialGst);
    setUpi(initialUpi);
  }, [initialGst, initialUpi, ownerId]);

  useEffect(() => {
    let isCancelled = false;
    async function fetchSignal() {
      setLoading(true);
      try {
        const data = await api.getAlternateSignal(ownerId, gst, upi);
        if (!isCancelled) {
          setResult(data);
        }
      } catch (err) {
        console.error('Alternate signal error:', err);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }

    const timer = setTimeout(fetchSignal, 150);
    return () => {
      isCancelled = true;
      clearTimeout(timer);
    };
  }, [ownerId, gst, upi]);

  const score = result?.supplementary_score || Math.round((gst * 0.5 + upi * 0.5) * 100);
  const isPositive = score >= 75;
  const isModerate = score >= 50 && score < 75;

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--accent-pink)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Layers size={19} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--text-primary)' }}>Alternate Data Signals</h3>
              <span className="badge badge-pink" style={{ fontSize: '0.68rem' }}>Phase 4 Layer</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              GST & UPI early indicators — moves before monthly bureau updates
            </p>
          </div>
        </div>

        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Supplementary Score</div>
          <div style={{ fontSize: '1.4rem', fontWeight: '800', color: isPositive ? '#34D399' : isModerate ? '#FBBF24' : '#FB7185' }}>
            {score}<span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/100</span>
          </div>
        </div>
      </div>

      {/* Sliders for GST and UPI */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <label className="form-label" style={{ margin: 0 }}>GST Return Regularity (6 Mos)</label>
            <span style={{ fontWeight: '700', color: 'var(--accent-pink)', fontSize: '0.82rem' }}>{Math.round(gst * 100)}% on-time</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={gst}
            onChange={(e) => setGst(parseFloat(e.target.value))}
            className="custom-slider"
            style={{ width: '100%' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <label className="form-label" style={{ margin: 0 }}>UPI Cash Inflow Stability</label>
            <span style={{ fontWeight: '700', color: 'var(--accent-pink)', fontSize: '0.82rem' }}>{Math.round(upi * 100)}% consistency</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={upi}
            onChange={(e) => setUpi(parseFloat(e.target.value))}
            className="custom-slider"
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Trend Callout Box */}
      <div
        style={{
          background: isPositive ? 'rgba(16, 185, 129, 0.14)' : isModerate ? 'rgba(245, 158, 11, 0.14)' : 'rgba(244, 63, 94, 0.14)',
          border: `1px solid ${isPositive ? 'rgba(16, 185, 129, 0.35)' : isModerate ? 'rgba(245, 158, 11, 0.35)' : 'rgba(244, 63, 94, 0.35)'}`,
          borderRadius: '8px',
          padding: '12px 14px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '10px',
          marginBottom: '14px',
        }}
      >
        {isPositive ? (
          <CheckCircle2 size={18} style={{ color: '#34D399', flexShrink: 0, marginTop: '2px' }} />
        ) : (
          <AlertTriangle size={18} style={{ color: isModerate ? '#FBBF24' : '#FB7185', flexShrink: 0, marginTop: '2px' }} />
        )}
        <div style={{ fontSize: '0.82rem', color: isPositive ? '#34D399' : isModerate ? '#FBBF24' : '#FB7185', lineHeight: '1.4' }}>
          <strong>Trend Interpretation: </strong>
          {result?.trend_label || 'Calculated supplementary cash-flow health indicator.'}
        </div>
      </div>

      {/* Compliance Disclaimer */}
      <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
        <strong>Compliance Notice: </strong>
        Supplementary layer only. Never blended into the core CIBIL MSME Rank calculation, conforming with CICRA 2005 rules.
      </div>
    </div>
  );
}
