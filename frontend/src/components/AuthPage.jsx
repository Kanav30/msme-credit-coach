import React, { useState } from 'react';
import { Activity, ArrowRight, ShieldCheck, ArrowLeft, Lock, Mail, Phone, Building2, User, Zap, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function AuthPage({
  initialMode = 'login', // 'login' or 'signup'
  onSuccess,
  onBackToLanding,
  onDemoLogin,
}) {
  const [mode, setMode] = useState(initialMode); // 'login' or 'signup'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form State
  const [fullName, setFullName] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [loginIdentifier, setLoginIdentifier] = useState(''); // single field on login: phone OR email
  const [password, setPassword] = useState('');
  const [targetRank, setTargetRank] = useState(3);
  const [industryCategory, setIndustryCategory] = useState('medium');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'signup') {
        if (!fullName.trim() || !businessName.trim() || !phone.trim() || !email.trim() || !password.trim()) {
          throw new Error('Please fill in all required fields (Name, Business, Mobile, Email, and Password).');
        }
        const res = await api.signup({
          full_name: fullName.trim(),
          business_name: businessName.trim(),
          phone: phone.trim(),
          email: email.trim(),
          password: password.trim(),
          target_rank: Number(targetRank) || 3,
          industry_category: industryCategory,
        });
        if (res.user) {
          onSuccess(res.user);
        }
      } else {
        if (!loginIdentifier.trim() || !password.trim()) {
          throw new Error('Please enter your mobile number or email address, and your password.');
        }
        const res = await api.login({
          email_or_phone: loginIdentifier.trim(),
          password: password.trim(),
        });
        if (res.user) {
          onSuccess(res.user);
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.demoLogin('demo-owner-1');
      if (res.user) {
        onSuccess(res.user);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--bg-page)' }}>
      {/* Top Navbar */}
      <header className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand" style={{ cursor: 'pointer' }} onClick={onBackToLanding}>
            <div className="navbar-logo-icon">
              <Activity size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="navbar-title">MSME Credit Coach</span>
                <span className="badge badge-pink" style={{ fontSize: '0.65rem' }}>CMR-Focused</span>
              </div>
              <div className="navbar-subtitle">CIBIL MSME Rank Diagnostic & Action Roadmap</div>
            </div>
          </div>

          <button
            onClick={onBackToLanding}
            className="btn btn-secondary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <ArrowLeft size={14} /> Back to Overview
          </button>
        </div>
      </header>

      <main className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, padding: '40px 16px' }}>
        <div
          className="glass-card"
          style={{
            width: '100%',
            maxWidth: '480px',
            padding: '32px',
            boxShadow: 'var(--shadow-modal)',
            background: 'var(--bg-card)',
          }}
        >
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '22px' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: '800', color: 'var(--text-primary)' }}>
              {mode === 'signup' ? 'Create Business Account' : 'Welcome Back'}
            </h2>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {mode === 'signup'
                ? 'Get your transparent CIBIL MSME Rank diagnostic and action plan'
                : 'Access your credit score habit streak and trajectory projections'}
            </p>
          </div>

          {/* Error Banner */}
          {error && (
            <div
              style={{
                background: '#FEE2E2',
                border: '1px solid #FECACA',
                borderRadius: '8px',
                padding: '10px 14px',
                marginBottom: '16px',
                fontSize: '0.82rem',
                color: '#991B1B',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <div>{error}</div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            {mode === 'signup' && (
              <>
                <div className="form-group">
                  <label className="form-label">Promoter / Owner Full Name</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="e.g. Rajesh Kumar"
                      className="form-input"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Business / Trade Name</label>
                  <input
                    type="text"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    placeholder="e.g. Acme Precision Tools Pvt Ltd"
                    className="form-input"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Mobile Number (+91)</label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="e.g. 9876543210"
                      className="form-input"
                      required
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="e.g. owner@business.com"
                    className="form-input"
                    required
                  />
                </div>
              </>
            )}

            {mode === 'login' && (
              <div className="form-group">
                <label className="form-label">Mobile Number or Email Address</label>
                <input
                  type="text"
                  value={loginIdentifier}
                  onChange={(e) => setLoginIdentifier(e.target.value)}
                  placeholder="e.g. 9876543210 or owner@business.com"
                  className="form-input"
                  required
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="form-input"
                required
              />
              {mode === 'signup' && (
                <div style={{ fontSize: '0.73rem', color: 'var(--text-muted)', marginTop: '5px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <Lock size={12} style={{ color: 'var(--accent-pink)', flexShrink: 0 }} />
                  <span>This password connects to both your phone and email. You can sign in using either!</span>
                </div>
              )}
            </div>

            {mode === 'signup' && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label className="form-label">Target Loan Rank</label>
                  <select
                    value={targetRank}
                    onChange={(e) => setTargetRank(parseInt(e.target.value))}
                    className="form-select"
                  >
                    <option value="2">CMR-2 (Super Prime)</option>
                    <option value="3">CMR-3 (Bank Threshold)</option>
                    <option value="4">CMR-4 (NBFC Collateral)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Industry Risk Tier</label>
                  <select
                    value={industryCategory}
                    onChange={(e) => setIndustryCategory(e.target.value)}
                    className="form-select"
                  >
                    <option value="low">Low (Stable Mfg / FMCG)</option>
                    <option value="medium">Medium (Trading / Services)</option>
                    <option value="high">High (Commodity / Volatile)</option>
                  </select>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '10px', padding: '11px', fontSize: '0.92rem' }}
            >
              {loading
                ? 'Processing...'
                : mode === 'signup'
                ? 'Create Account & Open Dashboard'
                : 'Sign In to Dashboard'}
            </button>
          </form>

          {/* Toggle Login / Signup */}
          <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            {mode === 'signup' ? (
              <>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('login'); setError(null); }}
                  style={{ background: 'none', border: 'none', color: 'var(--accent-pink)', fontWeight: '700', cursor: 'pointer', padding: 0 }}
                >
                  Sign In
                </button>
              </>
            ) : (
              <>
                New to the MSME Credit Coach?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('signup'); setError(null); }}
                  style={{ background: 'none', border: 'none', color: 'var(--accent-pink)', fontWeight: '700', cursor: 'pointer', padding: 0 }}
                >
                  Create Free Account
                </button>
              </>
            )}
          </div>

          {/* Compliance Assurance */}
          <div style={{ marginTop: '22px', borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', textAlign: 'center', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            <ShieldCheck size={14} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom', color: 'var(--accent-pink)' }} />
            Zero bureau passwords or sensitive tax documents required.
          </div>
        </div>
      </main>
    </div>
  );
}
