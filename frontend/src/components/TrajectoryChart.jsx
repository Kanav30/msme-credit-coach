import React, { useState } from 'react';
import { TrendingUp, CheckCircle, Target, HelpCircle } from 'lucide-react';

export default function TrajectoryChart({ predictionData, targetRank = 3 }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!predictionData) {
    return (
      <div className="glass-card" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading trajectory projection...
      </div>
    );
  }

  const simulator = predictionData.simulator_prediction || {};
  const trajectory = simulator.trajectory || [];
  const targetReached = simulator.target_reached;
  const monthsToTarget = simulator.months_to_target;
  const effort = predictionData.assumed_effort_pattern || {};
  const mlEstimate = predictionData.regression_model_6_month_estimate || {};

  // Chart Dimensions
  const width = 680;
  const height = 240;
  const padLeft = 45;
  const padRight = 30;
  const padTop = 25;
  const padBottom = 35;

  const chartW = width - padLeft - padRight;
  const chartH = height - padTop - padBottom;

  // X scale: months (0 to max month)
  const maxMonth = Math.max(1, trajectory.length > 0 ? trajectory[trajectory.length - 1].month : 12);
  const getX = (month) => padLeft + (month / maxMonth) * chartW;

  // Y scale: CMR rank from 10 (bottom) to 1 (top)
  const getY = (rank) => padTop + ((rank - 1) / 9) * chartH;

  // Generate points
  const points = trajectory.map((pt) => ({
    x: getX(pt.month),
    y: getY(pt.estimated_cmr_rank),
    ...pt,
  }));

  const pathD = points.length > 0
    ? `M ${points.map((p) => `${p.x} ${p.y}`).join(' L ')}`
    : '';

  const areaD = points.length > 0
    ? `M ${points[0].x} ${padTop + chartH} L ${points.map((p) => `${p.x} ${p.y}`).join(' L ')} L ${points[points.length - 1].x} ${padTop + chartH} Z`
    : '';

  const targetY = getY(targetRank);

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-pink">Deterministic Simulator</span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--text-primary)' }}>Projected CMR Rank Trajectory</h3>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '3px' }}>
            Projects rank progression based on factors you have actually logged effort toward.
          </p>
        </div>

        <div>
          {trajectory.length === 0 ? (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'var(--bg-card-subtle)',
                border: '1px solid var(--border-subtle)',
                padding: '6px 14px',
                borderRadius: '8px',
              }}
            >
              <Target size={18} style={{ color: 'var(--accent-pink)' }} />
              <div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Forecast Status</div>
                <div style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                  Awaiting Report / Habit Logs
                </div>
              </div>
            </div>
          ) : targetReached ? (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'rgba(16, 185, 129, 0.16)',
                border: '1px solid rgba(16, 185, 129, 0.35)',
                padding: '6px 14px',
                borderRadius: '8px',
              }}
            >
              <CheckCircle size={18} style={{ color: '#34D399' }} />
              <div>
                <div style={{ fontSize: '0.68rem', color: '#34D399', textTransform: 'uppercase', fontWeight: '600' }}>Target Reached In</div>
                <div style={{ fontSize: '1rem', fontWeight: '800', color: '#34D399' }}>
                  Approx. {monthsToTarget} Months
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'rgba(245, 158, 11, 0.16)',
                border: '1px solid rgba(245, 158, 11, 0.35)',
                padding: '6px 14px',
                borderRadius: '8px',
              }}
            >
              <Target size={18} style={{ color: 'var(--accent-pink)' }} />
              <div>
                <div style={{ fontSize: '0.68rem', color: '#FBBF24', textTransform: 'uppercase', fontWeight: '600' }}>Forecast Horizon</div>
                <div style={{ fontSize: '0.9rem', fontWeight: '700', color: '#FBBF24' }}>
                  Target not reached within 24 mos
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Effort Assumed Pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', fontSize: '0.78rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
        <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>Simulator Active Levers:</span>
        <span
          className={`badge ${effort.credit_utilization ? 'badge-pink' : 'badge-neutral'}`}
          style={{ fontSize: '0.72rem' }}
        >
          Utilization Effort: {effort.credit_utilization ? 'Active (Logging)' : 'Inactive'}
        </span>
        <span
          className={`badge ${effort.payment_history ? 'badge-pink' : 'badge-neutral'}`}
          style={{ fontSize: '0.72rem' }}
        >
          Payment Track: {effort.payment_history ? 'Active (Logging)' : 'Inactive'}
        </span>
      </div>

      {/* SVG Chart */}
      <div style={{ position: 'relative', width: '100%', overflowX: 'auto' }}>
        <svg
          viewBox={`0 0 ${width} ${height}`}
          style={{ width: '100%', height: 'auto', display: 'block', minWidth: '480px' }}
        >
          <defs>
            <linearGradient id="chartAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#FF3D8B" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#FF3D8B" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines and Y axis ticks */}
          {[1, 3, 5, 7, 10].map((r) => {
            const y = getY(r);
            return (
              <g key={r}>
                <line
                  x1={padLeft}
                  y1={y}
                  x2={width - padRight}
                  y2={y}
                  stroke="var(--border-subtle)"
                  strokeDasharray={r === targetRank ? '0' : '4 4'}
                  strokeWidth="1"
                />
                <text
                  x={padLeft - 8}
                  y={y + 3.5}
                  fill="var(--text-muted)"
                  fontSize="9.5"
                  fontWeight="600"
                  textAnchor="end"
                >
                  CMR {r}
                </text>
              </g>
            );
          })}

          {/* Target rank threshold line */}
          <line
            x1={padLeft}
            y1={targetY}
            x2={width - padRight}
            y2={targetY}
            stroke="var(--accent-pink)"
            strokeDasharray="6 4"
            strokeWidth="1.5"
          />
          <text
            x={width - padRight}
            y={targetY - 6}
            fill="var(--accent-pink)"
            fontSize="9.5"
            fontWeight="700"
            textAnchor="end"
          >
            Target (CMR-{targetRank})
          </text>

          {/* Empty State Notice when awaiting data */}
          {trajectory.length === 0 && (
            <g>
              <rect
                x={padLeft + 40}
                y={padTop + 45}
                width={chartW - 80}
                height={chartH - 80}
                rx="10"
                fill="var(--bg-card)"
                stroke="var(--border-subtle)"
                strokeDasharray="4 4"
              />
              <text
                x={padLeft + chartW / 2}
                y={padTop + chartH / 2 - 10}
                fill="var(--text-primary)"
                fontSize="12.5"
                fontWeight="700"
                textAnchor="middle"
              >
                No Trajectory Data Yet
              </text>
              <text
                x={padLeft + chartW / 2}
                y={padTop + chartH / 2 + 12}
                fill="var(--text-muted)"
                fontSize="10"
                textAnchor="middle"
              >
                Upload your CIBIL CIR report or log weekly actions to generate trajectory projection
              </text>
            </g>
          )}

          {/* Area fill */}
          {areaD && <path d={areaD} fill="url(#chartAreaGradient)" />}

          {/* Trajectory curve */}
          {pathD && (
            <path
              d={pathD}
              fill="none"
              stroke="var(--accent-pink)"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ filter: 'drop-shadow(0 0 8px rgba(255, 42, 133, 0.4))' }}
            />
          )}

          {/* Data Points */}
          {points.map((pt, idx) => {
            const isHovered = hoveredPoint?.month === pt.month;
            const isTargetPoint = pt.month === monthsToTarget;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredPoint(pt)}
                onMouseLeave={() => setHoveredPoint(null)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={isHovered ? 6 : isTargetPoint ? 5 : 3.5}
                  fill={isTargetPoint ? '#FFFFFF' : 'var(--accent-pink)'}
                  stroke={isTargetPoint ? 'var(--accent-pink)' : '#FFFFFF'}
                  strokeWidth={isHovered ? 2.5 : 1.5}
                  style={{ transition: 'all 0.15s ease' }}
                />

                {/* X-axis Month Label */}
                {pt.month % 3 === 0 && (
                  <text
                    x={pt.x}
                    y={padTop + chartH + 18}
                    fill="var(--text-muted)"
                    fontSize="9.5"
                    textAnchor="middle"
                  >
                    M{pt.month}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Hover Tooltip */}
        {hoveredPoint && (
          <div
            style={{
              position: 'absolute',
              left: `${(hoveredPoint.x / width) * 100}%`,
              top: `${(hoveredPoint.y / height) * 100}%`,
              transform: 'translate(-50%, -125%)',
              background: 'var(--bg-card)',
              border: '1px solid var(--accent-pink)',
              borderRadius: '8px',
              padding: '6px 12px',
              fontSize: '0.78rem',
              color: 'var(--text-primary)',
              boxShadow: 'var(--shadow-pink-glow)',
              pointerEvents: 'none',
              whiteSpace: 'nowrap',
              zIndex: 10,
            }}
          >
            <div style={{ fontWeight: '700' }}>Month {hoveredPoint.month}</div>
            <div style={{ color: 'var(--accent-pink)', fontWeight: '700' }}>Rank: CMR-{hoveredPoint.estimated_cmr_rank}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>Score: {hoveredPoint.overall_score}/100</div>
          </div>
        )}
      </div>

      {/* Simulator / ML Footnote Callout */}
      <div
        style={{
          marginTop: '14px',
          background: 'var(--bg-card-subtle)',
          padding: '10px 14px',
          borderRadius: '8px',
          border: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '8px',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
        }}
      >
        <div>
          <strong style={{ color: 'var(--text-primary)' }}>Calibrated Simulator Model: </strong>
          Reflects 8% monthly utilization drops and 3% payment improvements.
        </div>
        {mlEstimate.model_metrics && (
          <div style={{ color: 'var(--text-secondary)' }}>
            ML Surrogate Validation: <strong style={{ color: 'var(--accent-pink)' }}>R² = {mlEstimate.model_metrics.r2}</strong>
          </div>
        )}
      </div>
    </div>
  );
}
