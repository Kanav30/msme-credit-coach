import React from 'react';
import { Flame, Plus, RotateCcw, Trash2, Calendar, CheckCircle2 } from 'lucide-react';

export default function StreakTracker({
  streakWeeks = 0,
  actions = [],
  onOpenLogModal,
  onResetHistory,
  onDeleteAction,
}) {
  const hasStreak = streakWeeks > 0;

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div
            style={{
              width: '52px',
              height: '52px',
              borderRadius: '14px',
              background: hasStreak ? 'var(--accent-pink-bg)' : 'var(--bg-card-subtle)',
              border: hasStreak ? '1px solid var(--accent-pink-border)' : '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: hasStreak ? 'var(--shadow-pink-glow)' : 'none',
            }}
          >
            <Flame
              size={28}
              style={{
                color: hasStreak ? 'var(--accent-pink)' : 'var(--text-muted)',
              }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: 'var(--text-primary)' }}>Self-Logging Habit Streak</h3>
              {hasStreak && <span className="badge badge-pink">{streakWeeks} Week Active</span>}
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
              Bureaus update monthly — tracking weekly actions builds habit discipline that feeds your hypothetical trajectory.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {actions.length > 0 && (
            <button
              onClick={onResetHistory}
              className="btn btn-secondary btn-sm"
              title="Reset logged test actions"
              style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}
            >
              <RotateCcw size={13} /> Clear Logs
            </button>
          )}

          <button
            onClick={() => onOpenLogModal()}
            className="btn btn-primary"
            style={{ fontSize: '0.85rem' }}
          >
            <Plus size={15} /> Log Action
          </button>
        </div>
      </div>

      {/* Streak Counter Bar */}
      <div
        style={{
          background: 'var(--bg-card-subtle)',
          borderRadius: '10px',
          padding: '14px 18px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '20px',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Current Active Streak
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: hasStreak ? 'var(--accent-pink)' : 'var(--text-primary)', lineHeight: '1.1' }}>
              {streakWeeks} <span style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-muted)' }}>consecutive weeks</span>
            </div>
          </div>

          <div style={{ height: '32px', width: '1px', background: 'var(--border-subtle)' }} />

          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>
              Total Logged Actions
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--text-primary)', lineHeight: '1.1' }}>
              {actions.length} <span style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-muted)' }}>self-reported actions</span>
            </div>
          </div>
        </div>

        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', maxWidth: '320px', textAlign: 'right' }}>
          {hasStreak
            ? '🔥 Streak active! Keep logging once per calendar week to feed the trajectory simulator.'
            : 'No actions logged this week. Record an action above to start your streak.'}
        </div>
      </div>

      {/* Action History List */}
      <div>
        <h4 style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Recent Action History
        </h4>

        {actions.length === 0 ? (
          <div
            style={{
              padding: '24px',
              textAlign: 'center',
              background: 'var(--bg-card-subtle)',
              borderRadius: '10px',
              border: '1px dashed var(--border-subtle)',
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
            }}
          >
            No actions recorded yet. Click <strong>"+ Log Action"</strong> above to record a credit improvement (e.g. paying down a credit limit or activating autopay).
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto' }}>
            {actions.map((act) => {
              const dt = new Date(act.logged_at);
              const dateStr = dt.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
              const factorName = (act.factor || '').replace('_', ' ');

              return (
                <div
                  key={act.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    background: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-subtle)',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                    <CheckCircle2 size={16} style={{ color: '#34D399', flexShrink: 0 }} />
                    <div style={{ minWidth: 0 }}>
                      <div
                        style={{
                          fontSize: '0.86rem',
                          fontWeight: '600',
                          color: 'var(--text-primary)',
                          whiteSpace: 'nowrap',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {act.description}
                      </div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        <span style={{ textTransform: 'capitalize', fontWeight: '600', color: 'var(--accent-pink)' }}>{factorName}</span>
                        <span>•</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <Calendar size={11} /> {dateStr}
                        </span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => onDeleteAction(act.id)}
                    className="btn btn-secondary btn-sm"
                    style={{ padding: '4px 6px', color: 'var(--accent-rose-text)', borderColor: 'transparent', background: 'transparent' }}
                    title="Remove action"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
