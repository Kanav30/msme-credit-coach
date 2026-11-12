import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Download,
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Building2,
  Clock,
  CreditCard,
  Activity,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { api } from '../api';

export default function CibilReportTab({
  ownerId,
  currentProfile,
  onProfileUpdated,
  onNavigateToCoach,
}) {
  const [samples, setSamples] = useState([]);
  const [loadingSamples, setLoadingSamples] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [parsingResult, setParsingResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [notification, setNotification] = useState(null);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  useEffect(() => {
    async function loadSamples() {
      try {
        const res = await api.getCibilSamples();
        setSamples(res.samples || []);
      } catch (err) {
        console.error('Error fetching sample reports:', err);
      } finally {
        setLoadingSamples(false);
      }
    }
    loadSamples();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        showNotification('Please select a valid PDF file (.pdf)', 'error');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        showNotification('Please drop a valid PDF file (.pdf)', 'error');
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setParsingResult(null);

    try {
      const res = await api.uploadCibilReport(ownerId, selectedFile);
      setParsingResult(res);
      showNotification('CIBIL Report successfully parsed & profile updated!');
      if (onProfileUpdated) onProfileUpdated();
    } catch (err) {
      showNotification(`Upload error: ${err.message}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSample = async (archetypeId) => {
    setUploading(true);
    setParsingResult(null);
    try {
      const res = await api.loadCibilSample(ownerId, archetypeId);
      setParsingResult(res);
      showNotification(`Loaded & parsed official CIBIL report scenario!`);
      if (onProfileUpdated) onProfileUpdated();
    } catch (err) {
      showNotification(`Error loading sample: ${err.message}`, 'error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Toast Notification */}
      {notification && (
        <div
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            background: notification.type === 'error' ? 'var(--accent-rose-bg)' : 'var(--bg-card)',
            color: 'var(--text-primary)',
            border: `1px solid ${notification.type === 'error' ? 'var(--accent-rose-border)' : 'var(--accent-pink)'}`,
            padding: '12px 18px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            fontWeight: '600',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: 'var(--shadow-pink-glow)',
          }}
        >
          {notification.type === 'error' ? <AlertTriangle size={16} style={{ color: '#FB7185' }} /> : <CheckCircle2 size={16} style={{ color: '#34D399' }} />}
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Top Header Card */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-pink">TransUnion CIBIL Ingestion</span>
              <h2 style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                Official CIBIL Report (PDF) Parser
              </h2>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Upload your official commercial credit report or test with our generated TransUnion CIBIL scenarios to auto-populate your diagnostic health card.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className="badge badge-emerald">
              <ShieldCheck size={13} /> CICRA 2005 Compliant
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Upload Zone vs Sample Scenarios */}
      <div className="grid-2">
        {/* Upload Zone */}
        <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', color: 'var(--text-primary)' }}>
            Upload CIBIL Commercial CIR
          </h3>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--accent-pink)' : 'var(--border-subtle)'}`,
              borderRadius: '12px',
              padding: '36px 20px',
              textAlign: 'center',
              background: dragActive ? 'var(--accent-pink-bg)' : 'var(--bg-card-subtle)',
              transition: 'all 0.15s ease',
              marginBottom: '16px',
              cursor: 'pointer',
            }}
            onClick={() => document.getElementById('cibil-file-input').click()}
          >
            <input
              id="cibil-file-input"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />

            <div
              style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 12px auto',
                color: 'var(--accent-pink)',
              }}
            >
              <Upload size={22} />
            </div>

            <div style={{ fontWeight: '700', fontSize: '0.92rem', color: 'var(--text-primary)', marginBottom: '4px' }}>
              {selectedFile ? selectedFile.name : 'Click to Browse or Drag & Drop CIBIL PDF'}
            </div>
            <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
              {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB selected` : 'Supports official TransUnion CIBIL Commercial CIR reports (.pdf)'}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: 'auto' }}>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="btn btn-primary"
              style={{ flex: 1, padding: '10px' }}
            >
              {uploading ? (
                <>
                  <RefreshCw size={15} className="pulse-dot" /> Parsing CIBIL Report...
                </>
              ) : (
                <>
                  <FileCheck size={16} /> Parse & Apply to Profile
                </>
              )}
            </button>

            {selectedFile && (
              <button
                onClick={() => setSelectedFile(null)}
                className="btn btn-secondary btn-sm"
                style={{ color: 'var(--text-muted)' }}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Generated Sample Scenarios Section */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                Official Sample CIBIL Reports
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Generated exactly how TransUnion CIBIL issues them. Download to inspect or load with 1 click:
              </p>
            </div>
          </div>

          {loadingSamples ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading sample reports...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '340px', overflowY: 'auto' }}>
              {samples.map((s) => (
                <div
                  key={s.archetype_id}
                  style={{
                    padding: '12px 14px',
                    borderRadius: '8px',
                    background: 'var(--bg-card-subtle)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className={`badge ${s.cmr_rank <= 3 ? 'badge-emerald' : s.cmr_rank <= 6 ? 'badge-amber' : 'badge-rose'}`} style={{ fontSize: '0.68rem' }}>
                        CMR-{s.cmr_rank}
                      </span>
                      <h4 style={{ fontSize: '0.88rem', fontWeight: '700', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {s.company_name}
                      </h4>
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                      Util: <strong style={{ color: 'var(--text-primary)' }}>{s.credit_utilization}%</strong> • Tenure: <strong style={{ color: 'var(--text-primary)' }}>{s.tenure_years} yrs</strong> • Age: <strong style={{ color: 'var(--text-primary)' }}>{s.business_age_years} yrs</strong>
                      {s.has_recent_delinquency && <span style={{ color: '#FB7185', marginLeft: '6px', fontWeight: '600' }}>[Recent 30-Day Delay]</span>}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
                    <a
                      href={api.getSampleDownloadUrl(s.archetype_id)}
                      download={s.filename}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{ padding: '6px 12px', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                      title="Download Official CIBIL PDF"
                    >
                      <Download size={14} /> Download Sample PDF
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Parsed Extraction Result Display */}
      {parsingResult && (
        <div className="glass-card" style={{ padding: '24px', border: '1.5px solid var(--accent-pink)', boxShadow: 'var(--shadow-pink-glow)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '8px', background: 'var(--accent-pink-bg)', color: 'var(--accent-pink)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CheckCircle2 size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                  Extracted CIBIL Credit Profile: {parsingResult.extracted_report_metadata.company_name}
                </h3>
                <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                  RCN: {parsingResult.extracted_report_metadata.rcn} • PAN: {parsingResult.extracted_report_metadata.pan || 'N/A'} • GSTIN: {parsingResult.extracted_report_metadata.gstin || 'N/A'}
                </div>
              </div>
            </div>

            <button
              onClick={onNavigateToCoach}
              className="btn btn-primary btn-sm"
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              View Updated Coach Dashboard <ArrowRight size={14} />
            </button>
          </div>

          {/* 4 Pillars Breakdown & Ranks as Extracted from Bureau Report */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '16px' }}>
            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Official Bureau Rank</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: (parsingResult.extracted_report_metadata.official_cmr_rank && parsingResult.extracted_report_metadata.official_cmr_rank <= 3) ? '#34D399' : 'var(--accent-pink)' }}>
                {parsingResult.extracted_report_metadata.official_cmr_rank ? `CMR-${parsingResult.extracted_report_metadata.official_cmr_rank}` : 'Unranked'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Extracted from Bureau CIR</div>
            </div>

            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Coach Diagnostic Proxy</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: parsingResult.diagnostic?.estimated_cmr_rank <= 3 ? '#34D399' : '#F59E0B' }}>
                CMR-{parsingResult.diagnostic?.estimated_cmr_rank} <span style={{ fontSize: '0.85rem', fontWeight: '600' }}>({parsingResult.diagnostic?.overall_score}/100)</span>
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Transparent 4-Pillar Score</div>
            </div>

            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Credit Utilization</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: (parsingResult.extracted_report_metadata.credit_utilization_pct && parsingResult.extracted_report_metadata.credit_utilization_pct > 75) ? '#FB7185' : '#34D399' }}>
                {parsingResult.extracted_report_metadata.credit_utilization_pct !== null && parsingResult.extracted_report_metadata.credit_utilization_pct !== undefined ? `${parsingResult.extracted_report_metadata.credit_utilization_pct}%` : 'Missing'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Total Balance / Limit</div>
            </div>

            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Repayment Conduct (DPD)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: parsingResult.extracted_report_metadata.has_recent_delinquency ? '#FB7185' : '#34D399' }}>
                {parsingResult.extracted_report_metadata.has_recent_delinquency ? 'Recent 30+ DPD' : (parsingResult.extracted_report_metadata.on_time_payment_pct ? `${parsingResult.extracted_report_metadata.on_time_payment_pct}% On-Time` : '100% On-Time')}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Scanned facility asset classification</div>
            </div>

            <div style={{ background: 'var(--bg-card-subtle)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: '600' }}>Credit Vintage</div>
              <div style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--text-primary)' }}>
                {parsingResult.extracted_report_metadata.credit_tenure_years !== null && parsingResult.extracted_report_metadata.credit_tenure_years !== undefined ? `${parsingResult.extracted_report_metadata.credit_tenure_years} yrs` : 'Missing'}
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>Oldest facility relationship</div>
            </div>
          </div>

          {/* Extracted Facilities List */}
          {parsingResult.extracted_report_metadata.facilities && parsingResult.extracted_report_metadata.facilities.length > 0 && (
            <div style={{ marginBottom: '16px', background: 'var(--bg-card-subtle)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '8px' }}>
                Extracted Credit Facilities ({parsingResult.extracted_report_metadata.facilities.length})
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {parsingResult.extracted_report_metadata.facilities.map((fac, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', padding: '6px 10px', background: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                    <div>
                      <strong style={{ color: 'var(--text-primary)' }}>{fac.facility_name}</strong>
                      <span style={{ marginLeft: '8px', color: 'var(--text-muted)' }}>Status: {fac.status || 'Active'}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                      {fac.sanctioned_amount && <span>Limit: INR {fac.sanctioned_amount.toLocaleString('en-IN')}</span>}
                      {fac.outstanding_balance && <span>Balance: INR {fac.outstanding_balance.toLocaleString('en-IN')}</span>}
                      <span className={`badge ${fac.has_recent_delinquency ? 'badge-rose' : 'badge-emerald'}`} style={{ fontSize: '0.68rem' }}>
                        {fac.has_recent_delinquency ? 'Delinquent' : 'Clean / Regular'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div style={{ background: 'rgba(16, 185, 129, 0.14)', border: '1px solid rgba(16, 185, 129, 0.35)', padding: '10px 14px', borderRadius: '6px', fontSize: '0.8rem', color: '#34D399' }}>
            <strong style={{ color: '#FFFFFF' }}>Coach Diagnostic Sync: </strong>
            Your profile has been updated with these extracted bureau figures. Your <strong>Action Plan</strong>, <strong>Habit Tracker</strong>, and <strong>Projected Trajectory Curve</strong> now reflect this official bureau state.
          </div>
        </div>
      )}
    </div>
  );
}
