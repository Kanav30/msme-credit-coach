import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import AuthPage from './components/AuthPage';
import CibilReportTab from './components/CibilReportTab';
import ScoreGauge from './components/ScoreGauge';
import FactorCard from './components/FactorCard';
import StreakTracker from './components/StreakTracker';
import TrajectoryChart from './components/TrajectoryChart';
import AlternateDataCard from './components/AlternateDataCard';
import DailyActionTracker from './components/DailyActionTracker';
import WhatIfSandbox from './components/WhatIfSandbox';
import LogActionModal from './components/LogActionModal';
import { api } from './api';
import { Info, Sparkles, AlertCircle, HelpCircle, ChevronDown, ChevronUp, FileText, ArrowRight } from 'lucide-react';

export default function App() {
  // Navigation View State: 'landing' | 'auth' | 'app'
  const [currentView, setCurrentView] = useState(() => {
    const hash = window.location.hash;
    if (hash === '#app' || hash === '#dashboard') return 'app';
    if (hash === '#auth' || hash === '#login' || hash === '#signup') return 'auth';
    return 'landing';
  });

  const [authMode, setAuthMode] = useState('signup'); // 'login' or 'signup'

  // Active Authenticated User (saved in localStorage)
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const stored = localStorage.getItem('msme_coach_user');
      return stored ? JSON.parse(stored) : null;
    } catch (_) {
      return null;
    }
  });

  const [activeTab, setActiveTab] = useState('owner');
  const [currentOwnerId, setCurrentOwnerId] = useState(() => {
    return currentUser?.owner_id || 'guest-msme';
  });

  const [profiles, setProfiles] = useState([]);
  const [currentProfile, setCurrentProfile] = useState(null);
  const [diagnostic, setDiagnostic] = useState(null);
  const [actionPlan, setActionPlan] = useState(null);
  const [streakData, setStreakData] = useState({ streak_weeks: 0 });
  const [actions, setActions] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modals
  const [logModalOpen, setLogModalOpen] = useState(false);
  const [defaultLogFactor, setDefaultLogFactor] = useState('credit_utilization');

  // FAQ accordion state
  const [expandedFaq, setExpandedFaq] = useState(null);

  // Notification Toast
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Sync hash with view
  useEffect(() => {
    if (currentView === 'landing') window.location.hash = 'overview';
    else if (currentView === 'auth') window.location.hash = authMode;
    else if (currentView === 'app') window.location.hash = activeTab;
  }, [currentView, authMode, activeTab]);

  // Load profile list and active profile data
  const loadData = useCallback(async (ownerId) => {
    setLoading(true);
    setError(null);
    try {
      try {
        await api.checkHealth();
        setBackendOnline(true);
      } catch (_) {
        setBackendOnline(false);
      }

      const profsRes = await api.getProfiles();
      setProfiles(profsRes.profiles || []);

      const active = profsRes.profiles?.find((p) => p.owner_id === ownerId) || {
        owner_id: ownerId,
        name: currentUser?.business_name || 'My Business',
        target_rank: currentUser?.target_rank || 3,
        estimated_cmr_rank: null,
        overall_score: null,
      };
      setCurrentProfile(active);

      const [diagRes, planRes, streakRes, histRes, predRes] = await Promise.all([
        api.getDiagnostic(ownerId),
        api.getActionPlan(ownerId),
        api.getStreak(ownerId),
        api.getLogHistory(ownerId),
        api.getPrediction(ownerId),
      ]);

      setDiagnostic(diagRes);
      setActionPlan(planRes);
      setStreakData(streakRes);
      setActions(histRes.actions || []);
      setPrediction(predRes);
      setBackendOnline(true);
    } catch (err) {
      console.error('Data load error:', err);
      setError(err.message);
      setBackendOnline(false);
    } finally {
      setLoading(false);
    }
  }, [currentUser]);

  useEffect(() => {
    if (currentView === 'app') {
      loadData(currentOwnerId);
    }
  }, [currentView, currentOwnerId, loadData]);

  // Handle Authentication Success
  const handleAuthSuccess = (userData) => {
    setCurrentUser(userData);
    localStorage.setItem('msme_coach_user', JSON.stringify(userData));
    setCurrentOwnerId(userData.owner_id);
    setCurrentView('app');
    showToast(`Welcome, ${userData.full_name || userData.business_name}!`);
  };

  // Handle Sign Out
  const handleSignOut = () => {
    setCurrentUser(null);
    localStorage.removeItem('msme_coach_user');
    setCurrentOwnerId('guest-msme');
    setCurrentView('landing');
    showToast('Signed out successfully.');
  };

  // Handle Action Logging
  const handleLogAction = async (factor, description) => {
    try {
      await api.logAction(currentOwnerId, factor, description);
      showToast(`Action logged for ${factor.replace('_', ' ')}! Streak and trajectory updated.`);
      await loadData(currentOwnerId);
    } catch (err) {
      alert(`Error logging action: ${err.message}`);
    }
  };

  // Handle Single Action Deletion
  const handleDeleteAction = async (actionId) => {
    if (!window.confirm('Delete this action record?')) return;
    try {
      await api.deleteAction(actionId);
      showToast('Action record removed.');
      await loadData(currentOwnerId);
    } catch (err) {
      alert(`Error deleting action: ${err.message}`);
    }
  };

  // Handle History Reset
  const handleResetHistory = async () => {
    if (!window.confirm('Clear all logged actions for this business? This will reset the streak counter.')) return;
    try {
      await api.resetLogHistory(currentOwnerId);
      showToast('Logged history reset for this profile.');
      await loadData(currentOwnerId);
    } catch (err) {
      alert(`Error resetting history: ${err.message}`);
    }
  };

  // Handle Complete Data Reset (Clean Slate)
  const handleResetAllData = async () => {
    if (!window.confirm('Reset this business to clean placeholder state (clear any scores, uploaded reports, and habit logs)?')) return;
    try {
      await api.resetProfile(currentOwnerId);
      await api.resetLogHistory(currentOwnerId);
      showToast('Reset to clean placeholders. Awaiting CIBIL report.');
      await loadData(currentOwnerId);
    } catch (err) {
      alert(`Error resetting: ${err.message}`);
    }
  };

  const handleOpenLogModal = (factor = 'credit_utilization') => {
    setDefaultLogFactor(factor);
    setLogModalOpen(true);
  };

  if (currentView === 'landing') {
    return (
      <LandingPage
        onGetStarted={() => {
          setAuthMode('signup');
          setCurrentView('auth');
        }}
        onLogin={() => {
          setAuthMode('login');
          setCurrentView('auth');
        }}
      />
    );
  }

  if (currentView === 'auth') {
    return (
      <AuthPage
        initialMode={authMode}
        onSuccess={handleAuthSuccess}
        onBackToLanding={() => setCurrentView('landing')}
      />
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-page)' }}>
      {/* Toast Notification */}
      {toastMessage && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            background: 'var(--bg-card)',
            border: '1px solid var(--accent-pink)',
            boxShadow: 'var(--shadow-pink-glow)',
            padding: '12px 18px',
            borderRadius: '8px',
            color: 'var(--text-primary)',
            fontSize: '0.85rem',
            fontWeight: '600',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            animation: 'slideUp 0.2s ease-out',
          }}
        >
          <Sparkles size={15} style={{ color: 'var(--accent-pink)' }} /> {toastMessage}
        </div>
      )}

      {/* Navbar with Return to Home & Sign Out */}
      <Navbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        currentProfile={currentProfile}
        currentUser={currentUser}
        backendOnline={backendOnline}
        onNavigateLanding={() => setCurrentView('landing')}
        onSignOut={handleSignOut}
        onResetAllData={handleResetAllData}
      />

      <main className="app-container">
        {/* Compliance & Bureau Role Banner */}
        <div className="compliance-banner">
          <Info size={18} style={{ color: '#D97706', flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Legally Compliant Coaching Model (CICRA 2005): </strong>
            Only RBI-licensed Credit Information Companies (CIBIL, Experian, Equifax, CRIF) calculate official credit scores.
            This coach never replaces or issues a bureau score — it transparently diagnoses your official <strong>CIBIL MSME Rank (CMR 1 to 10)</strong>,
            prioritizes high-leverage improvement habits, and predicts when you'll reach loan eligibility.
          </div>
        </div>

        {error && (
          <div
            style={{
              background: '#FEE2E2',
              border: '1px solid #FECACA',
              borderRadius: '8px',
              padding: '14px 18px',
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              color: '#991B1B',
            }}
          >
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <div>
              <div style={{ fontWeight: '700', fontSize: '0.88rem' }}>Backend Connection Notice</div>
              <div style={{ fontSize: '0.82rem' }}>{error}</div>
            </div>
          </div>
        )}

        {/* Tab 1: MSME Owner Coach View */}
        {activeTab === 'owner' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Quick Link to CIBIL PDF Ingestion Tab */}
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '10px',
                padding: '12px 18px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '10px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <FileText size={18} style={{ color: 'var(--accent-pink)' }} />
                <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: '600' }}>
                  Have an official TransUnion CIBIL CIR report? Auto-populate your diagnostic card from PDF:
                </span>
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button
                  onClick={() => setActiveTab('daily-logs')}
                  className="btn btn-secondary btn-sm"
                  style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-pink)', borderColor: 'var(--accent-pink-border)' }}
                >
                  ⚡ Daily Habit Logs <ArrowRight size={13} />
                </button>
                <button
                  onClick={() => setActiveTab('cibil')}
                  className="btn btn-secondary btn-sm"
                  style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-primary)' }}
                >
                  Upload CIBIL PDF <ArrowRight size={13} />
                </button>
              </div>
            </div>

            {/* Top Row: Score Meter & Habit Tracker */}
            <div className="grid-2">
              <ScoreGauge
                rank={diagnostic?.estimated_cmr_rank ?? currentProfile?.estimated_cmr_rank ?? null}
                overallScore={diagnostic?.overall_score ?? currentProfile?.overall_score ?? null}
                targetRank={actionPlan?.target_rank || currentProfile?.target_rank || 3}
              />

              <StreakTracker
                streakWeeks={streakData.streak_weeks}
                actions={actions}
                onOpenLogModal={handleOpenLogModal}
                onResetHistory={handleResetHistory}
                onDeleteAction={handleDeleteAction}
              />
            </div>

            {/* Middle Section: Prioritized Factor Diagnostics */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                    Transparent Factor Diagnostics & Action Plan
                  </h2>
                  <p style={{ fontSize: '0.8rem', color: '#78716C' }}>
                    Ranked by <strong>Actionable Priority</strong> (Score Headroom weighted by realistic improvement speed), not raw theoretical gap.
                  </p>
                </div>

                <button onClick={() => handleOpenLogModal('credit_utilization')} className="btn btn-primary btn-sm">
                  + Record Action Taken
                </button>
              </div>

              <div className="grid-4">
                {(actionPlan?.prioritized_factors || []).map((factor, idx) => (
                  <FactorCard
                    key={factor.factor}
                    factor={factor}
                    onLogActionClick={handleOpenLogModal}
                    onQuickLogAction={handleLogAction}
                    isTopPriority={idx === 0}
                  />
                ))}
              </div>
            </div>

            {/* Bottom Row: Trajectory Chart & Alternate Signals */}
            <div className="grid-2">
              <TrajectoryChart
                predictionData={prediction}
                targetRank={actionPlan?.target_rank || currentProfile?.target_rank || 3}
              />

              <AlternateDataCard
                ownerId={currentOwnerId}
                initialGst={currentProfile?.gst_filing_regularity || 0.8}
                initialUpi={currentProfile?.upi_inflow_stability || 0.8}
              />
            </div>

            {/* Practical Credit Coach Q&A */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <HelpCircle size={18} style={{ color: 'var(--accent-pink)' }} />
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                  Common Credit Coaching Questions for MSMEs
                </h3>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {[
                  {
                    q: "Why did a recent late payment hurt my CMR rank so much?",
                    a: "Payment history accounts for ~40% of the CMR calculation. Even a single 30-day delinquency triggers an automatic 20-point factor drop. Once you log 3 consecutive months of on-time payments, recent delinquency status clears and your rank recovers quickly."
                  },
                  {
                    q: "What is the quickest way to close the gap to CMR-3?",
                    a: "Credit utilization (25% weight) is your fastest lever. Paying down card or working capital balances to drop utilization below 60% can improve your rank in a single monthly billing cycle. Alternatively, asking your bank for a credit limit extension immediately lowers your utilization ratio without spending cash."
                  },
                  {
                    q: "Does closing an old loan account improve my credit score?",
                    a: "No, in fact it often hurts! Credit tenure accounts for ~20% of your rank. Closing your oldest account shortens your average credit history and reduces your overall available limit, increasing utilization."
                  },
                ].map((item, idx) => {
                  const isOpen = expandedFaq === idx;
                  return (
                    <div
                      key={idx}
                      style={{
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '8px',
                        background: 'var(--bg-card-subtle)',
                        overflow: 'hidden',
                      }}
                    >
                      <button
                        onClick={() => setExpandedFaq(isOpen ? null : idx)}
                        style={{
                          width: '100%',
                          textAlign: 'left',
                          padding: '12px 14px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          background: 'transparent',
                          border: 'none',
                          cursor: 'pointer',
                          fontWeight: '600',
                          fontSize: '0.86rem',
                          color: 'var(--text-primary)',
                        }}
                      >
                        <span>{item.q}</span>
                        {isOpen ? <ChevronUp size={16} style={{ color: 'var(--accent-pink)' }} /> : <ChevronDown size={16} />}
                      </button>
                      {isOpen && (
                        <div style={{ padding: '0 14px 12px 14px', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                          {item.a}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: CIBIL Report PDF Upload & Samples */}
        {activeTab === 'cibil' && (
          <CibilReportTab
            ownerId={currentOwnerId}
            currentProfile={currentProfile}
            onProfileUpdated={() => loadData(currentOwnerId)}
            onNavigateToCoach={() => setActiveTab('owner')}
          />
        )}

        {/* Tab 3: Daily Habits & Logs */}
        {activeTab === 'daily-logs' && (
          <DailyActionTracker
            streakWeeks={streakData.streak_weeks}
            actions={actions}
            onOpenLogModal={handleOpenLogModal}
            onResetHistory={handleResetHistory}
            onDeleteAction={handleDeleteAction}
            onQuickLogAction={handleLogAction}
          />
        )}

        {/* Tab 4: What-If Sandbox */}
        {activeTab === 'sandbox' && (
          <WhatIfSandbox
            currentProfile={currentProfile}
            ownerId={currentOwnerId}
            onProfileSaved={() => loadData(currentOwnerId)}
          />
        )}
      </main>

      {/* Log Action Modal */}
      <LogActionModal
        isOpen={logModalOpen}
        onClose={() => setLogModalOpen(false)}
        onSubmit={handleLogAction}
        defaultFactor={defaultLogFactor}
      />
    </div>
  );
}
