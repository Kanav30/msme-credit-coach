import React from 'react';
import { X, Building2, ArrowRight } from 'lucide-react';

export default function BusinessSwitcherModal({
  isOpen,
  onClose,
  profiles = [],
  currentOwnerId,
  onSelectProfile,
}) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '680px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <span className="badge badge-pink" style={{ marginBottom: '4px' }}>Realistic Test Archetypes</span>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--text-primary)' }}>Switch MSME Business Profile</h2>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary btn-sm"
            style={{ borderRadius: '50%', width: '32px', height: '32px', padding: 0 }}
          >
            <X size={16} />
          </button>
        </div>

        <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Select an active MSME profile or upload a new CIBIL CIR report to evaluate your business:
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {profiles.length === 0 ? (
            <div
              style={{
                padding: '24px',
                textAlign: 'center',
                background: 'var(--bg-card-subtle)',
                borderRadius: '8px',
                border: '1px dashed var(--border-subtle)',
                color: 'var(--text-muted)',
                fontSize: '0.86rem',
              }}
            >
              <Building2 size={28} style={{ color: 'var(--accent-pink)', margin: '0 auto 10px auto', display: 'block' }} />
              <div>No additional saved profiles.</div>
              <div style={{ fontSize: '0.78rem', marginTop: '4px', color: 'var(--text-secondary)' }}>
                Upload your TransUnion CIBIL CIR report in the <strong>CIBIL Report</strong> tab to populate this dashboard.
              </div>
            </div>
          ) : (
            profiles.map((p) => {
            const isSelected = p.owner_id === currentOwnerId;
            const rank = p.estimated_cmr_rank;
            const rankBadge = rank <= 3 ? 'badge-emerald' : rank <= 6 ? 'badge-amber' : 'badge-rose';

            return (
              <div
                key={p.owner_id}
                onClick={() => {
                  onSelectProfile(p.owner_id);
                  onClose();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 16px',
                  borderRadius: '10px',
                  background: isSelected ? 'var(--bg-card-hover)' : 'var(--bg-card-subtle)',
                  border: isSelected ? '1.5px solid var(--accent-pink)' : '1px solid var(--border-subtle)',
                  boxShadow: isSelected ? 'var(--shadow-pink-glow)' : 'none',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
                className="glass-card"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      width: '38px',
                      height: '38px',
                      borderRadius: '8px',
                      background: isSelected ? 'var(--accent-pink)' : 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: isSelected ? '#FFFFFF' : 'var(--text-muted)',
                    }}
                  >
                    <Building2 size={20} />
                  </div>

                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <h4 style={{ fontSize: '0.96rem', fontWeight: '700', color: 'var(--text-primary)' }}>{p.name}</h4>
                      {isSelected && (
                        <span className="badge badge-pink" style={{ fontSize: '0.62rem', background: 'var(--accent-pink)', color: '#FFFFFF' }}>Active</span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                      {p.archetype}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                      {p.industry_name} • Age: {p.business_age_years} yrs • Tenure: {p.credit_tenure_years} yrs
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div>
                    <span className={`badge ${rankBadge}`}>{rank ? `CMR-${rank}` : 'Unranked'}</span>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                      Target: CMR-{p.target_rank}
                    </div>
                  </div>
                  <ArrowRight size={16} style={{ color: isSelected ? 'var(--accent-pink)' : 'var(--text-muted)' }} />
                </div>
              </div>
            );
          }))}
        </div>
      </div>
    </div>
  );
}
