import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, Target, ArrowRight, FileQuestion } from 'lucide-react';

export default function ScoreGauge({ rank = null, overallScore = null, targetRank = 3, officialRank = null }) {
  const hasData = rank !== null && rank !== undefined && rank !== '--';

  // CMR Rank is 1 (Best) to 10 (Riskiest)
  const normalizedRank = hasData ? Math.max(1, Math.min(10, rank)) : null;
  const progress = hasData ? Math.max(0.04, Math.min(0.96, (10 - normalizedRank) / 9)) : 0;

  // Determine risk category and clean colors
  let riskTier = 'Awaiting CIR Report';
  let badgeClass = 'badge-neutral';
  let icon = <FileQuestion size={15} />;
  let color = 'var(--text-muted)';

  if (hasData) {
    if (normalizedRank >= 7) {
      riskTier = 'High / Distressed Risk';
      badgeClass = 'badge-rose';
      icon = <AlertOctagon size={15} />;
      color = '#B91C1C';
    } else if (normalizedRank >= 4) {
      riskTier = 'Moderate / Monitored Risk';
      badgeClass = 'badge-amber';
      icon = <AlertTriangle size={15} />;
      color = '#B45309';
    } else {
      riskTier = 'Prime / Low Risk';
      badgeClass = 'badge-emerald';
      icon = <ShieldCheck size={15} />;
      color = '#15803D';
    }
  }

  // Geometry calculations
  const cx = 160;
  const cy = 145;
  const radius = 105;
  const circumference = Math.PI * radius; // ~329.87
  const strokeDashoffset = hasData ? circumference * (1 - progress) : circumference;

  // Active indicator knob position on the arc
  const angleDeg = 180 - progress * 180;
  const angleRad = (angleDeg * Math.PI) / 180;
  const markerX = cx + radius * Math.cos(angleRad);
  const markerY = cy - radius * Math.sin(angleRad);

  // Target pin position on the arc
  const targetNorm = Math.max(1, Math.min(10, targetRank));
  const targetProgress = Math.max(0.04, Math.min(0.96, (10 - targetNorm) / 9));
  const targetAngleDeg = 180 - targetProgress * 180;
  const targetAngleRad = (targetAngleDeg * Math.PI) / 180;
  const targetX = cx + radius * Math.cos(targetAngleRad);
  const targetY = cy - radius * Math.sin(targetAngleRad);

  const rankGap = hasData ? Math.max(0, normalizedRank - targetRank) : null;

  return (
    <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px', flexWrap: 'wrap' }}>
            <span className="badge badge-pink">Coach Diagnostic Proxy</span>
            {officialRank && (
              <span className="badge badge-emerald">Bureau: CMR-{officialRank}</span>
            )}
          </div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--text-primary)' }}>CIBIL MSME Rank (CMR)</h2>
        </div>
        <span className={`badge ${badgeClass}`} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {icon}
          {riskTier}
        </span>
      </div>

      {/* SVG Radial Gauge */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '10px 0 4px 0' }}>
        <svg
          viewBox="0 0 320 185"
          style={{ width: '100%', maxWidth: '320px', height: 'auto', display: 'block', overflow: 'visible' }}
        >
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#DC2626" />
              <stop offset="35%" stopColor="#D97706" />
              <stop offset="70%" stopColor="#16A34A" />
              <stop offset="100%" stopColor="#0284C7" />
            </linearGradient>
          </defs>

          {/* Background track arc */}
          <path
            d="M 55 145 A 105 105 0 0 1 265 145"
            fill="none"
            stroke="var(--border-subtle)"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Active colored arc */}
          {hasData && (
            <path
              d="M 55 145 A 105 105 0 0 1 265 145"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="14"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            />
          )}

          {/* Target Milestone Marker on Arc */}
          <g style={{ transition: 'all 0.5s ease' }}>
            <circle
              cx={targetX}
              cy={targetY}
              r="4.5"
              fill="var(--accent-pink)"
              stroke="#FFFFFF"
              strokeWidth="2"
            />
            <line
              x1={targetX}
              y1={targetY - 10}
              x2={targetX}
              y2={targetY - 16}
              stroke="var(--accent-pink)"
              strokeWidth="1.5"
            />
            <text
              x={targetX}
              y={targetY - 19}
              fill="var(--accent-pink)"
              fontSize="9"
              textAnchor="middle"
              fontWeight="700"
            >
              Target
            </text>
          </g>

          {/* Active indicator knob */}
          {hasData && (
            <circle
              cx={markerX}
              cy={markerY}
              r="8"
              fill="#FFFFFF"
              stroke={color}
              strokeWidth="3.5"
              style={{ filter: 'drop-shadow(0 2px 6px rgba(0,0,0,0.4))', transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
            />
          )}

          {/* Center Text */}
          <text
            x="160"
            y="76"
            textAnchor="middle"
            fill="var(--text-muted)"
            fontSize="10"
            fontWeight="700"
            letterSpacing="1.2"
          >
            {hasData ? 'CURRENT RANK' : 'AWAITING DATA'}
          </text>

          <text
            x="160"
            y="114"
            textAnchor="middle"
            fill={hasData ? color : 'var(--text-secondary)'}
            fontSize="36"
            fontWeight="800"
            style={{ fontFamily: 'var(--font-heading)' }}
          >
            {hasData ? `CMR-${normalizedRank}` : '--'}
          </text>

          {/* Proxy Score pill badge */}
          <g>
            <rect
              x="86"
              y="126"
              width="148"
              height="23"
              rx="11.5"
              fill="var(--bg-card-subtle)"
              stroke="var(--border-subtle)"
              strokeWidth="1"
            />
            <text
              x="160"
              y="141.5"
              textAnchor="middle"
              fill="var(--text-secondary)"
              fontSize="10"
              fontWeight="500"
            >
              {hasData ? (
                <>Proxy Score: <tspan fill="var(--text-primary)" fontWeight="700">{overallScore}</tspan>/100</>
              ) : (
                'Upload Report to Score'
              )}
            </text>
          </g>

          {/* Bottom scale labels */}
          <text x="55" y="166" fill="#F43F5E" fontSize="10.5" textAnchor="middle" fontWeight="700">
            CMR 10
          </text>
          <text x="55" y="178" fill="var(--text-muted)" fontSize="8.5" textAnchor="middle">
            Distressed
          </text>

          <text x="160" y="172" fill="var(--text-muted)" fontSize="9" textAnchor="middle">
            Scale: 1 (Prime) — 10 (High Risk)
          </text>

          <text x="265" y="166" fill="var(--accent-pink)" fontSize="10.5" textAnchor="middle" fontWeight="700">
            CMR 1
          </text>
          <text x="265" y="178" fill="var(--text-muted)" fontSize="8.5" textAnchor="middle">
            Prime
          </text>
        </svg>
      </div>

      {/* Target & Gap Footer */}
      <div
        style={{
          marginTop: 'auto',
          paddingTop: '14px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-card-subtle)',
          borderRadius: '10px',
          padding: '12px 16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target size={18} style={{ color: 'var(--accent-pink)' }} />
          <div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Target for Loan</div>
            <div style={{ fontWeight: '700', fontSize: '0.98rem', color: 'var(--text-primary)' }}>CMR-{targetRank}</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {!hasData ? (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Status</div>
              <div style={{ fontWeight: '600', fontSize: '0.82rem', color: 'var(--accent-pink)' }}>Upload CIR to View Gap</div>
            </div>
          ) : rankGap === 0 ? (
            <span className="badge badge-emerald">Target Reached!</span>
          ) : (
            <>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Rank Gap</div>
                <div style={{ fontWeight: '700', color: 'var(--accent-pink)' }}>{rankGap} Ranks to Close</div>
              </div>
              <ArrowRight size={16} style={{ color: 'var(--accent-pink)' }} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
