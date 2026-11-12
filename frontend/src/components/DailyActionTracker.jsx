import React, { useState } from 'react';
import {
  Flame,
  Plus,
  RotateCcw,
  Trash2,
  Calendar,
  CheckCircle2,
  Circle,
  Sparkles,
  TrendingUp,
  ShieldCheck,
  Zap,
  Filter,
  Check,
} from 'lucide-react';

const DAILY_HABITS = [
  {
    id: 'habit-1',
    title: 'Monitor Overdraft / Credit Limit Balances',
    description: 'Ensure utilization stays safely below the 60% healthy ceiling before month-end bureau snapshots.',
    factor: 'credit_utilization',
    impact: 'Fastest score lever (+10-25 pts)',
  },
  {
    id: 'habit-2',
    title: 'Verify Account Balance for Upcoming NACH Mandates',
    description: 'Confirm sufficient funds 48 hours before loan EMI or credit card auto-debits to avoid return charges and 30-day DPD flags.',
    factor: 'payment_history',
    impact: 'Prevents 20-pt automatic delinquency penalty',
  },
  {
    id: 'habit-3',
    title: 'Settle Trade Payables & Invoices On-Time',
    description: 'Prioritize institutional suppliers who report payment conduct to commercial credit bureaus.',
    factor: 'payment_history',
    impact: 'Protects commercial trade credit history',
  },
  {
    id: 'habit-4',
    title: 'Sweep Surplus Daily Collections to CC/OD Account',
    description: 'Parking excess daily customer collections in your credit line lowers daily interest costs and keeps utilization low.',
    factor: 'credit_utilization',
    impact: 'Immediate utilization reduction',
  },
  {
    id: 'habit-5',
    title: 'Audit Bureau Statement for Inaccurate DPD Tags',
    description: 'Flag incorrectly reported overdue amounts or delayed settlements directly to CIBIL commercial dispute desk.',
    factor: 'firm_profile',
    impact: 'Can remove erroneous 30/60 DPD flags',
  },
];

const PRESET_ACTIONS = [
  { factor: 'credit_utilization', label: 'Paid ₹50,000 to overdraft balance', speed: 'Fast' },
  { factor: 'credit_utilization', label: 'Requested credit limit increase from ₹10L to ₹15L', speed: 'Fast' },
  { factor: 'payment_history', label: 'Verified NACH auto-debit for monthly term loan EMI', speed: 'Medium' },
  { factor: 'payment_history', label: 'Disputed outdated 30-day delinquency with CIBIL', speed: 'Medium' },
  { factor: 'payment_history', label: 'Paid vendor raw-material invoice within 30-day terms', speed: 'Medium' },
  { factor: 'firm_profile', label: 'Onboarded 2 new corporate buyers to diversify revenue', speed: 'Gradual' },
];

const getTodayIST = () => {
  try {
    return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date());
  } catch (_) {
    const now = new Date();
    const istDate = new Date(now.getTime() + 5.5 * 60 * 60 * 1000);
    return istDate.toISOString().split('T')[0];
  }
};

export default function DailyActionTracker({
  streakWeeks = 0,
  actions = [],
  ownerId = 'default',
  onOpenLogModal,
  onResetHistory,
  onDeleteAction,
  onQuickLogAction,
}) {
  const [selectedFactor, setSelectedFactor] = useState('all');
  const todayIST = getTodayIST();
  const storageKey = `daily_habits_${ownerId}_${todayIST}`;

  const [completedHabits, setCompletedHabits] = useState(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (_) {
      return {};
    }
  });

  // Re-sync local checklist when active account switches
  React.useEffect(() => {
    try {
      const stored = localStorage.getItem(`daily_habits_${ownerId}_${todayIST}`);
      setCompletedHabits(stored ? JSON.parse(stored) : {});
    } catch (_) {
      setCompletedHabits({});
    }
  }, [ownerId, todayIST]);

  const toggleHabit = (habitId) => {
    const updated = { ...completedHabits, [habitId]: !completedHabits[habitId] };
    setCompletedHabits(updated);
    try {
      localStorage.setItem(`daily_habits_${ownerId}_${todayIST}`, JSON.stringify(updated));
    } catch (_) {}
  };

  const filteredActions = selectedFactor === 'all'
    ? actions
    : actions.filter((a) => a.factor === selectedFactor);

  const hasStreak = streakWeeks > 0;
  const completedCount = Object.values(completedHabits).filter(Boolean).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner: Streak & Habit Consistency */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div
              style={{
                width: '58px',
                height: '58px',
                borderRadius: '16px',
                background: hasStreak ? 'var(--accent-pink-bg)' : 'var(--bg-card-subtle)',
                border: hasStreak ? '1.5px solid var(--accent-pink-border)' : '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: hasStreak ? 'var(--shadow-pink-glow)' : 'none',
              }}
            >
              <Flame
                size={32}
                style={{
                  color: hasStreak ? 'var(--accent-pink)' : 'var(--text-muted)',
                }}
              />
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                  Daily Habits & Score Improvement Logs
                </h2>
                {hasStreak && (
                  <span className="badge badge-pink" style={{ fontSize: '0.75rem' }}>
                    🔥 {streakWeeks} Week Streak
                  </span>
                )}
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Bureaus record monthly snapshots. Consistent borrower habits support steady credit health progression toward target loan tiers.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {actions.length > 0 && (
              <button
                onClick={onResetHistory}
                className="btn btn-secondary btn-sm"
                title="Clear test actions"
                style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}
              >
                <RotateCcw size={13} /> Reset Test Logs
              </button>
            )}

            <button
              onClick={() => onOpenLogModal()}
              className="btn btn-primary"
              style={{ fontSize: '0.88rem' }}
            >
              <Plus size={16} /> Log Custom Action
            </button>
          </div>
        </div>

        {/* 3 Metric Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginTop: '20px' }}>
          <div style={{ background: 'var(--bg-card-subtle)', padding: '14px 16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Active Streak</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: hasStreak ? 'var(--accent-pink)' : 'var(--text-primary)', lineHeight: '1.2' }}>
              {streakWeeks} <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)' }}>consecutive wks</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Logs recorded each calendar week</div>
          </div>

          <div style={{ background: 'var(--bg-card-subtle)', padding: '14px 16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Today's Habit Checklist</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: completedCount >= 3 ? '#34D399' : 'var(--accent-pink)', lineHeight: '1.2' }}>
              {completedCount} / {DAILY_HABITS.length} <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)' }}>done</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{completedCount === DAILY_HABITS.length ? 'All daily hygiene checks complete!' : 'Complete daily checks below'}</div>
          </div>

          <div style={{ background: 'var(--bg-card-subtle)', padding: '14px 16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Self-Reported Actions</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--text-primary)', lineHeight: '1.2' }}>
              {actions.length} <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)' }}>logged</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '2px' }}>Self-reported entries (unverified by bureau)</div>
          </div>
        </div>
      </div>

      {/* Main Grid: Daily Habits Checklist vs 1-Click Quick Logger */}
      <div className="grid-2">
        {/* Daily Credit Hygiene Checklist */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={18} style={{ color: 'var(--accent-pink)' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                Daily Credit Health Checklist
              </h3>
            </div>
            <span className="badge badge-pink" style={{ fontSize: '0.68rem' }}>
              IST: {new Date().toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata', month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Check off daily tasks to build disciplined borrower habits that protect your business credit score:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {DAILY_HABITS.map((habit) => {
              const isChecked = !!completedHabits[habit.id];
              return (
                <div
                  key={habit.id}
                  onClick={() => toggleHabit(habit.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '12px',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    background: isChecked ? 'rgba(16, 185, 129, 0.12)' : 'var(--bg-card-subtle)',
                    border: `1px solid ${isChecked ? 'rgba(16, 185, 129, 0.35)' : 'var(--border-subtle)'}`,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <div style={{ marginTop: '2px', color: isChecked ? '#34D399' : 'var(--text-muted)' }}>
                    {isChecked ? <CheckCircle2 size={18} fill="rgba(16, 185, 129, 0.25)" /> : <Circle size={18} />}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: '700', fontSize: '0.86rem', color: isChecked ? '#34D399' : 'var(--text-primary)', textDecoration: isChecked ? 'line-through' : 'none' }}>
                        {habit.title}
                      </span>
                      <span className="badge badge-pink" style={{ fontSize: '0.62rem' }}>
                        {habit.impact}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.74rem', color: isChecked ? 'var(--text-muted)' : 'var(--text-secondary)', marginTop: '3px', lineHeight: '1.4' }}>
                      {habit.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 1-Click Fast Action Logger */}
        <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <Zap size={18} style={{ color: 'var(--accent-pink)' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
              1-Click Action Logger
            </h3>
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Record an action taken toward credit improvement. Entries are self-reported and not independently verified by credit bureaus:
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
            {PRESET_ACTIONS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onQuickLogAction ? onQuickLogAction(preset.factor, preset.label) : onOpenLogModal(preset.factor)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'var(--bg-card-subtle)',
                  border: '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                  fontSize: '0.82rem',
                }}
                className="btn-secondary"
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Plus size={15} style={{ color: 'var(--accent-pink)' }} />
                  <span style={{ fontWeight: '600', color: 'var(--text-primary)' }}>{preset.label}</span>
                </div>
                <span className={`badge ${preset.speed === 'Fast' ? 'badge-pink' : 'badge-neutral'}`} style={{ fontSize: '0.65rem' }}>
                  {preset.speed} Lever
                </span>
              </button>
            ))}
          </div>

          <div style={{ marginTop: 'auto', background: 'var(--bg-card-subtle)', padding: '12px 14px', borderRadius: '8px', border: '1px solid var(--border-subtle)', fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
            <strong style={{ color: 'var(--accent-pink)' }}>Hypothetical Projection Mechanism: </strong>
            Logging self-reported actions signals active effort in the hypothetical trajectory simulator. Official CIBIL/CMR ranks are determined solely by credit bureaus upon monthly lender reporting.
          </div>
        </div>
      </div>

      {/* Action History Log Table / Timeline */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--text-primary)' }}>
              Self-Reported Action History Log
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Self-reported log of credit improvement steps recorded by this business (unverified by credit bureaus).
            </p>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {['all', 'credit_utilization', 'payment_history', 'credit_tenure', 'firm_profile'].map((cat) => {
              const isActive = selectedFactor === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedFactor(cat)}
                  style={{
                    padding: '5px 12px',
                    fontSize: '0.74rem',
                    borderRadius: '6px',
                    border: `1px solid ${isActive ? 'var(--accent-pink)' : 'var(--border-subtle)'}`,
                    background: isActive ? 'var(--accent-pink)' : 'var(--bg-card-subtle)',
                    color: isActive ? '#FFFFFF' : 'var(--text-secondary)',
                    boxShadow: isActive ? 'var(--shadow-pink-glow)' : 'none',
                    fontWeight: '600',
                    cursor: 'pointer',
                    textTransform: 'capitalize',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {cat.replace('_', ' ')}
                </button>
              );
            })}
          </div>
        </div>

        {filteredActions.length === 0 ? (
          <div
            style={{
              padding: '32px 20px',
              textAlign: 'center',
              background: 'var(--bg-card-subtle)',
              borderRadius: '8px',
              border: '1px dashed var(--border-subtle)',
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
            }}
          >
            No actions recorded {selectedFactor !== 'all' ? `under ${selectedFactor.replace('_', ' ')}` : 'yet'}.
            Use the <strong>1-Click Fast Action Logger</strong> above to start tracking your credit habits!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredActions.map((act) => {
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
                    padding: '12px 16px',
                    borderRadius: '8px',
                    background: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-subtle)',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'var(--accent-pink-bg)', color: 'var(--accent-pink)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <Check size={15} />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                        {act.description}
                      </div>
                      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        <span style={{ textTransform: 'capitalize', fontWeight: '600', color: 'var(--accent-pink)' }}>
                          {factorName}
                        </span>
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
                    title="Delete log entry"
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
