import React, { useState } from 'react';
import { X, Check, Sparkles, Send } from 'lucide-react';

const QUICK_PRESETS = [
  { factor: 'credit_utilization', text: 'Paid down credit limit balance by ₹50,000' },
  { factor: 'credit_utilization', text: 'Requested bank credit limit increase from ₹10L to ₹15L' },
  { factor: 'payment_history', text: 'Activated NACH autopay mandate for monthly loan EMI' },
  { factor: 'payment_history', text: 'Disputed outdated overdue entry with CIBIL Commercial Desk' },
  { factor: 'payment_history', text: 'Settled vendor invoice in full within standard 30-day terms' },
  { factor: 'firm_profile', text: 'Diversified revenue stream with two new corporate clients' },
];

export default function LogActionModal({ isOpen, onClose, onSubmit, defaultFactor = 'credit_utilization' }) {
  const [factor, setFactor] = useState(defaultFactor);
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!description.trim()) return;

    setSubmitting(true);
    try {
      await onSubmit(factor, description.trim());
      setDescription('');
      onClose();
    } catch (err) {
      alert(`Failed to log action: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectPreset = (preset) => {
    setFactor(preset.factor);
    setDescription(preset.text);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
          <div>
            <span className="badge badge-pink" style={{ marginBottom: '4px' }}>Habit & Streak Tracker</span>
            <h2 style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--text-primary)' }}>Log Score Improvement Action</h2>
          </div>
          <button
            onClick={onClose}
            className="btn btn-secondary btn-sm"
            style={{ borderRadius: '50%', width: '32px', height: '32px', padding: 0 }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Quick Presets */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
            <Sparkles size={13} style={{ color: 'var(--accent-pink)' }} /> Quick Action Presets (Click to Auto-Fill):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '7px' }}>
            {QUICK_PRESETS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectPreset(preset)}
                className="btn btn-secondary btn-sm"
                style={{
                  fontSize: '0.76rem',
                  padding: '5px 9px',
                  background: factor === preset.factor ? 'var(--accent-pink-bg)' : 'var(--bg-card-subtle)',
                  borderColor: factor === preset.factor ? 'var(--accent-pink)' : 'var(--border-subtle)',
                  color: factor === preset.factor ? '#FFFFFF' : 'var(--text-primary)',
                }}
              >
                {preset.text}
              </button>
            ))}
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">CMR Factor Targeted</label>
            <select
              value={factor}
              onChange={(e) => setFactor(e.target.value)}
              className="form-select"
            >
              <option value="credit_utilization">Credit Utilization (Fast lever: pay down balances / request limit)</option>
              <option value="payment_history">Payment History (High weight 40%: on-time payments / resolve delinquency)</option>
              <option value="credit_tenure">Credit Tenure (Medium/Long term: maintain seasoned accounts)</option>
              <option value="firm_profile">Firm Profile (Firm stability / revenue diversification)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Action Description / Details</label>
            <textarea
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Transferred ₹40,000 to overdraft account to bring total limit utilization to 54%"
              className="form-textarea"
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting || !description.trim()}
              className="btn btn-primary"
            >
              <Send size={15} /> {submitting ? 'Recording...' : 'Record & Update Streak'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
