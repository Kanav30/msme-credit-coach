import React from 'react';
import { Compass, Flame, Sliders, Activity, Home, LogOut, FileText, RotateCcw } from 'lucide-react';

export default function Navbar({
  activeTab,
  onTabChange,
  currentProfile,
  backendOnline = true,
  currentUser,
  onSignOut,
  onNavigateLanding,
  onResetAllData,
}) {
  const officialRank = currentProfile?.official_cmr_rank;
  const illustrativeRank = currentProfile?.illustrative_cmr_rank;
  const estimatedRank = currentProfile?.estimated_cmr_rank;
  const displayRank = officialRank || illustrativeRank || estimatedRank;
  const hasRank = displayRank !== null && displayRank !== undefined && displayRank !== '--';
  const rankBadge = !hasRank ? 'badge-neutral' : displayRank <= 3 ? 'badge-emerald' : displayRank <= 6 ? 'badge-amber' : 'badge-rose';
  const rankLabel = officialRank
    ? `Bureau CMR-${officialRank}`
    : (illustrativeRank
        ? `Illustrative CMR-${illustrativeRank}`
        : (estimatedRank ? `Proxy CMR-${estimatedRank}` : 'Unranked'));

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Brand */}
        <div className="navbar-brand" style={{ cursor: onNavigateLanding ? 'pointer' : 'default' }} onClick={onNavigateLanding}>
          <div className="navbar-logo-icon">
            <Activity size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="navbar-title">MSME Credit Coach</span>
              <span className="badge badge-pink" style={{ fontSize: '0.65rem' }}>CMR-Focused</span>
            </div>
            <div className="navbar-subtitle">
              CIBIL MSME Rank Diagnostic & Action Roadmap
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="navbar-nav">
          <button
            onClick={() => onTabChange('owner')}
            className={`nav-tab ${activeTab === 'owner' ? 'active' : ''}`}
          >
            <Compass size={15} /> Owner Coach
          </button>

          <button
            onClick={() => onTabChange('cibil')}
            className={`nav-tab ${activeTab === 'cibil' ? 'active' : ''}`}
          >
            <FileText size={15} /> CIBIL Report (PDF)
          </button>

          <button
            onClick={() => onTabChange('daily-logs')}
            className={`nav-tab ${activeTab === 'daily-logs' ? 'active' : ''}`}
          >
            <Flame size={15} style={{ color: activeTab === 'daily-logs' ? 'var(--accent-pink)' : undefined }} /> Daily Habits & Logs
          </button>

          <button
            onClick={() => onTabChange('sandbox')}
            className={`nav-tab ${activeTab === 'sandbox' ? 'active' : ''}`}
          >
            <Sliders size={15} /> What-If Sandbox
          </button>
        </nav>

        {/* Actions & Profile Switcher */}
        <div className="navbar-actions">
          {/* Live Backend Connection Indicator */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.72rem',
              color: backendOnline ? '#34D399' : '#FBBF24',
              background: backendOnline ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
              padding: '5px 9px',
              borderRadius: '20px',
              border: `1px solid ${backendOnline ? 'rgba(16, 185, 129, 0.35)' : 'rgba(245, 158, 11, 0.35)'}`,
              fontWeight: '600',
            }}
            title={backendOnline ? 'Connected to FastAPI Backend (port 8000)' : 'Connecting to Backend...'}
          >
            <span
              className="pulse-dot"
              style={{
                backgroundColor: backendOnline ? '#10B981' : '#F59E0B',
              }}
            />
            <span>{backendOnline ? 'API Live' : 'Connecting...'}</span>
          </div>

          {/* Business Profile Badge */}
          <div
            className="profile-pill"
            style={{ cursor: 'default' }}
          >
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-primary)', lineHeight: '1.2' }}>
                {currentUser?.business_name || currentProfile?.name || 'My Business'}
              </div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                Target: CMR-{currentProfile?.target_rank || 3}
              </div>
            </div>
            <span className={`badge ${rankBadge}`} style={{ fontSize: '0.68rem' }}>
              {rankLabel}
            </span>
          </div>

          {/* Reset All Data to Clean Slate */}
          {onResetAllData && (
            <button
              onClick={onResetAllData}
              className="btn btn-secondary btn-sm"
              style={{ padding: '6px 10px', color: 'var(--text-muted)' }}
              title="Reset to Clean Slate (Clear all data & scores)"
            >
              <RotateCcw size={14} />
            </button>
          )}

          {/* Home / Overview Link */}
          {onNavigateLanding && (
            <button
              onClick={onNavigateLanding}
              className="btn btn-secondary btn-sm"
              style={{ padding: '6px 10px', color: 'var(--text-secondary)' }}
              title="Return to Product Landing Page"
            >
              <Home size={14} />
            </button>
          )}

          {/* Sign Out */}
          {onSignOut && (
            <button
              onClick={onSignOut}
              className="btn btn-secondary btn-sm"
              style={{ padding: '6px 10px', color: 'var(--accent-rose-text)', borderColor: 'var(--accent-rose-border)' }}
              title="Sign Out"
            >
              <LogOut size={14} />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
