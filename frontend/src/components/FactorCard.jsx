import React, { useState } from 'react';
import {
  CreditCard,
  Clock,
  Activity,
  Building2,
  Zap,
  PlusCircle,
  CheckCircle2,
  AlertTriangle,
  Target,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

const FACTOR_ICONS = {
  payment_history: Activity,
  credit_utilization: CreditCard,
  credit_tenure: Clock,
  firm_profile: Building2,
};

const FACTOR_LABELS = {
  payment_history: 'Payment History',
  credit_utilization: 'Credit Utilization',
  credit_tenure: 'Credit Tenure',
  firm_profile: 'Firm Profile',
};

// Concrete, actionable improvement strategies designed specifically for Indian MSMEs
const FACTOR_ACTION_STRATEGIES = {
  payment_history: {
    quickWin: 'Enable automated NACH / ECS mandates 48 hours prior to due dates and confirm bank float balance.',
    milestone: 'Complete 3 consecutive clean 30-day payment cycles to age out recent DPD flags and recover up to 20 pts.',
    mistakeToAvoid: 'Never leave small card balances or disputed late fees unpaid; commercial bureaus flag any overdue amount regardless of size.',
  },
  credit_utilization: {
    quickWin: 'Sweep daily collection inflows into CC/OD accounts to keep utilization strictly under the 60% healthy threshold.',
    milestone: 'Request a formal limit enhancement from your relationship bank (e.g., from ₹10L to ₹15L) to instantly cut your utilization ratio without borrowing.',
    mistakeToAvoid: 'Never max out revolving credit lines right before month-end bureau snapshots, even if you intend to clear it the next day.',
  },
  credit_tenure: {
    quickWin: 'Audit active bureau facilities to verify your oldest commercial credit account is actively reporting healthy status.',
    milestone: 'Keep long-standing credit facilities open by routing at least 1 routine supplier payment or utility bill through them each quarter.',
    mistakeToAvoid: 'DO NOT close your oldest credit facility or overdraft line! Closing it destroys your vintage history and immediately spikes overall utilization.',
  },
  firm_profile: {
    quickWin: 'Verify that trade name, GSTIN, and company promoter PAN details are 100% matched across all active bank sanction records.',
    milestone: 'Maintain 100% on-time GSTR-3B filings and build verified relationships with institutional suppliers who report to commercial bureaus.',
    mistakeToAvoid: 'Avoid frequent, abrupt shifts in registered bank accounts or corporate addresses immediately prior to loan applications.',
  },
};

export default function FactorCard({
  factor,
  onLogActionClick,
  onQuickLogAction,
  isTopPriority = false,
}) {
  const [showDetailedTips, setShowDetailedTips] = useState(isTopPriority);
  const Icon = FACTOR_ICONS[factor.factor] || Activity;
  const label = FACTOR_LABELS[factor.factor] || factor.factor.replace('_', ' ');
  const strategy = FACTOR_ACTION_STRATEGIES[factor.factor] || {
    quickWin: factor.recommendation || 'Maintain positive payment consistency.',
    milestone: 'Maintain uninterrupted clean conduct over the next 90 days.',
    mistakeToAvoid: 'Avoid applying for multiple loan facilities concurrently.',
  };

  const hasScore = factor.current_sub_score !== null && factor.current_sub_score !== undefined;

  // Color coding based on score
  let scoreColor = '#34D399';
  let badgeType = 'badge-emerald';
  let statusText = 'Healthy';

  if (!hasScore) {
    scoreColor = 'var(--text-muted)';
    badgeType = 'badge-neutral';
    statusText = 'Pending Data';
  } else if (factor.current_sub_score < 50) {
    scoreColor = '#FB7185';
    badgeType = 'badge-rose';
    statusText = 'Needs Urgent Action';
  } else if (factor.current_sub_score < 75) {
    scoreColor = '#FBBF24';
    badgeType = 'badge-amber';
    statusText = 'Moderate';
  }

  const isFast = factor.improvement_speed?.toLowerCase().includes('fast');
  const isMedium = factor.improvement_speed?.toLowerCase().includes('medium');

  return (
    <div
      className="glass-card"
      style={{
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative',
        border: isTopPriority ? '1.5px solid var(--accent-pink)' : undefined,
      }}
    >
      {isTopPriority && (
        <div
          style={{
            position: 'absolute',
            top: '-10px',
            right: '16px',
            background: 'var(--accent-pink)',
            color: '#FFFFFF',
            padding: '2px 10px',
            borderRadius: '12px',
            fontSize: '0.68rem',
            fontWeight: '700',
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            boxShadow: 'var(--shadow-pink-glow)',
          }}
        >
          <Zap size={11} fill="white" /> Top Priority Action
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: scoreColor,
            }}
          >
            <Icon size={19} />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', lineHeight: '1.2', color: 'var(--text-primary)' }}>{label}</h3>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
              CMR Weight: <strong style={{ color: 'var(--accent-pink)' }}>{Math.round((factor.weight || 0) * 100)}%</strong>
            </span>
          </div>
        </div>

        <span className={`badge ${badgeType}`} style={{ fontSize: '0.68rem' }}>
          {statusText}
        </span>
      </div>

      {/* Score and Progress Bar */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
          <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
            Factor Sub-Score
          </span>
          <span style={{ fontSize: '1.15rem', fontWeight: '800', color: hasScore ? scoreColor : 'var(--text-secondary)' }}>
            {hasScore ? Math.round(factor.current_sub_score) : '--'}
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '500' }}>/100</span>
          </span>
        </div>

        <div className="progress-bar-bg">
          <div
            className="progress-bar-fill"
            style={{
              width: hasScore ? `${Math.max(4, Math.min(100, factor.current_sub_score))}%` : '0%',
              backgroundColor: scoreColor,
            }}
          />
        </div>
      </div>

      {/* Priority & Speed Metrics */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px',
          background: 'var(--bg-card-subtle)',
          padding: '10px',
          borderRadius: '8px',
          marginBottom: '14px',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.74rem',
        }}
      >
        <div>
          <div style={{ color: 'var(--text-muted)' }}>Headroom Potential</div>
          <div style={{ fontWeight: '700', color: 'var(--text-primary)', fontSize: '0.85rem' }}>
            {hasScore ? `+${Math.round(factor.improvement_headroom || 0)} pts` : '-- pts'}
          </div>
        </div>

        <div>
          <div style={{ color: 'var(--text-muted)' }}>Response Speed</div>
          <div
            style={{
              fontWeight: '700',
              color: isFast ? 'var(--accent-pink)' : isMedium ? '#FBBF24' : 'var(--text-secondary)',
              fontSize: '0.85rem',
            }}
          >
            {isFast ? '⚡ Fast (~1 mo)' : isMedium ? '⏳ Medium (~3 mos)' : '🐢 Slow (gradual)'}
          </div>
        </div>
      </div>

      {/* Structured Multi-Step Improvement Tips */}
      <div style={{ marginBottom: '14px' }}>
        <div
          style={{
            background: 'var(--bg-card-subtle)',
            borderLeft: `3px solid ${scoreColor}`,
            padding: '10px 12px',
            borderRadius: '0 6px 6px 0',
            fontSize: '0.8rem',
            lineHeight: '1.45',
            color: 'var(--text-primary)',
            marginBottom: '8px',
          }}
        >
          <strong style={{ color: 'var(--accent-pink)' }}>Immediate Focus: </strong>
          {factor.recommendation || strategy.quickWin}
        </div>

        {/* Action Strategy Accordion Button */}
        <button
          onClick={() => setShowDetailedTips(!showDetailedTips)}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
            padding: '6px 10px',
            fontSize: '0.74rem',
            fontWeight: '600',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <span>{showDetailedTips ? 'Hide Structured Playbook' : 'View Actionable Tips & Playbook'}</span>
          {showDetailedTips ? <ChevronUp size={14} style={{ color: 'var(--accent-pink)' }} /> : <ChevronDown size={14} />}
        </button>

        {showDetailedTips && (
          <div
            style={{
              marginTop: '8px',
              padding: '10px',
              background: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              fontSize: '0.76rem',
              animation: 'fadeIn 0.15s ease-out',
            }}
          >
            {/* 7-Day Quick Win */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
              <Zap size={14} style={{ color: '#34D399', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ color: '#34D399' }}>7-Day Quick Win: </strong>
                <span style={{ color: 'var(--text-secondary)' }}>{strategy.quickWin}</span>
              </div>
            </div>

            {/* 30-90 Day Milestone */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
              <Target size={14} style={{ color: 'var(--accent-pink)', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ color: 'var(--accent-pink)' }}>30–90 Day Target: </strong>
                <span style={{ color: 'var(--text-secondary)' }}>{strategy.milestone}</span>
              </div>
            </div>

            {/* Mistake to Avoid */}
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
              <AlertTriangle size={14} style={{ color: '#FB7185', flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ color: '#FB7185' }}>Mistake to Avoid: </strong>
                <span style={{ color: 'var(--text-secondary)' }}>{strategy.mistakeToAvoid}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action CTA */}
      <div style={{ marginTop: 'auto', display: 'flex', gap: '6px' }}>
        <button
          onClick={() => onLogActionClick(factor.factor)}
          className="btn btn-secondary btn-sm"
          style={{ flex: 1, justifyContent: 'center' }}
        >
          <PlusCircle size={14} /> Log Action
        </button>

        {onQuickLogAction && (
          <button
            onClick={() => onQuickLogAction(factor.factor, strategy.quickWin)}
            className="btn btn-primary btn-sm"
            style={{ padding: '6px 10px', fontSize: '0.75rem' }}
            title="1-Click Record this Quick Win"
          >
            <CheckCircle2 size={13} />
          </button>
        )}
      </div>
    </div>
  );
}
