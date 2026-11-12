/**
 * API client for MSME Credit Score Coach backend.
 * Handles communication with FastAPI backend via Vite proxy or direct host.
 */

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/+$/, '');
const API_BASE = BACKEND_URL ? `${BACKEND_URL}` : '/api';
const DIRECT_BACKEND = BACKEND_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  let url = `${API_BASE}${path}`;
  let response;

  try {
    response = await fetch(url, {
      ...options,
      headers: {
        ...(options.isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(options.headers || {}),
      },
    });
  } catch (err) {
    try {
      url = `${DIRECT_BACKEND}${path}`;
      response = await fetch(url, {
        ...options,
        headers: {
          ...(options.isFormData ? {} : { 'Content-Type': 'application/json' }),
          ...(options.headers || {}),
        },
      });
    } catch (fallbackErr) {
      throw new Error(`Failed to reach backend server at ${DIRECT_BACKEND}. (${fallbackErr.message})`);
    }
  }

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Health
  checkHealth: () => request('/health'),

  // Authentication
  signup: (data) => request('/auth/signup', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  login: (data) => request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  demoLogin: (archetype = 'demo-owner-1') => request('/auth/demo-login', {
    method: 'POST',
    body: JSON.stringify({ archetype }),
  }),
  getCurrentUser: (ownerId) => request(`/auth/me/${ownerId}`),

  // CIBIL Report PDF Upload & Samples
  getCibilSamples: () => request('/cibil/samples'),
  uploadCibilReport: async (ownerId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`/cibil/upload/${ownerId}`, {
      method: 'POST',
      body: formData,
      isFormData: true,
    });
  },
  getSampleDownloadUrl: (archetypeId) => `${DIRECT_BACKEND}/cibil/download-sample/${archetypeId}`,

  // Profiles
  getProfiles: () => request('/owner/profiles'),
  getProfile: (ownerId) => request(`/owner/profile/${ownerId}`),
  resetProfile: (ownerId) => request(`/owner/reset-profile/${ownerId}`, {
    method: 'POST',
  }),
  updateProfile: (ownerId, profileData) => request(`/owner/profile/${ownerId}`, {
    method: 'PUT',
    body: JSON.stringify(profileData),
  }),

  // Diagnostic & Action Plan
  getDiagnostic: (ownerId) => request(`/owner/diagnostic/${ownerId}`),
  getActionPlan: (ownerId, targetRank) => {
    const query = targetRank !== undefined ? `?target_rank=${targetRank}` : '';
    return request(`/owner/action-plan/${ownerId}${query}`);
  },

  // Actions & Streak
  logAction: (ownerId, factor, description, loggedAt = null) => request(`/owner/log-action/${ownerId}`, {
    method: 'POST',
    body: JSON.stringify({ factor, description, logged_at: loggedAt }),
  }),
  deleteAction: (actionId) => request(`/owner/action/${actionId}`, {
    method: 'DELETE',
  }),
  getLogHistory: (ownerId) => request(`/owner/log-history/${ownerId}`),
  resetLogHistory: (ownerId) => request(`/owner/reset-history/${ownerId}`, {
    method: 'POST',
  }),
  getStreak: (ownerId) => request(`/owner/streak/${ownerId}`),

  // Trajectory Prediction & What-If
  getPrediction: (ownerId, targetRank = null, maxMonths = 24) => {
    const params = new URLSearchParams();
    if (targetRank !== null && targetRank !== undefined) params.append('target_rank', targetRank);
    if (maxMonths) params.append('max_months', maxMonths);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return request(`/owner/prediction/${ownerId}${queryString}`);
  },
  simulateWhatIf: (ownerId, monthlyEffort, targetRank = 3, maxMonths = 24) => request(`/owner/simulate-what-if/${ownerId}`, {
    method: 'POST',
    body: JSON.stringify({
      monthly_effort: monthlyEffort,
      target_rank: targetRank,
      max_months: maxMonths,
    }),
  }),

  // Alternate Data Signals
  getAlternateSignal: (ownerId, gstRegularity, upiStability) => request(`/owner/alternate-signal/${ownerId}`, {
    method: 'POST',
    body: JSON.stringify({
      gst_filing_regularity: gstRegularity,
      upi_inflow_stability: upiStability,
    }),
  }),
};
