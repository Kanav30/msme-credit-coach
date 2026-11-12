/**
 * API client for MSME Credit Score Coach backend.
 * Handles communication with FastAPI backend via Vite proxy or direct host.
 * Automatically attaches JWT authentication tokens and handles session expiration.
 */

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || '').replace(/\/+$/, '');
const API_BASE = BACKEND_URL ? `${BACKEND_URL}` : '/api';
const DIRECT_BACKEND = BACKEND_URL || 'http://127.0.0.1:8000';

const TOKEN_KEY = 'msme_coach_token';
const USER_KEY = 'msme_coach_user';

export function getAuthToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || '';
  } catch (_) {
    return '';
  }
}

export function setAuthSession(token, user) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (_) {}
}

export function clearAuthSession() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (_) {}
}

async function request(path, options = {}) {
  let url = `${API_BASE}${path}`;
  let response;

  const token = getAuthToken();
  const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};

  const requestHeaders = {
    ...(options.isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...authHeaders,
    ...(options.headers || {}),
  };

  try {
    response = await fetch(url, {
      ...options,
      headers: requestHeaders,
    });
  } catch (err) {
    try {
      url = `${DIRECT_BACKEND}${path}`;
      response = await fetch(url, {
        ...options,
        headers: requestHeaders,
      });
    } catch (fallbackErr) {
      throw new Error(`Failed to reach backend server at ${DIRECT_BACKEND}. (${fallbackErr.message})`);
    }
  }

  // If the relative endpoint hits a static host that returns 405/404, try local backend fallback if available
  if ((response.status === 405 || response.status === 404) && !url.startsWith('http')) {
    try {
      const fallbackUrl = `${DIRECT_BACKEND}${path}`;
      const fallbackRes = await fetch(fallbackUrl, {
        ...options,
        headers: requestHeaders,
      });
      if (fallbackRes.ok || [400, 401, 403, 409, 422, 429].includes(fallbackRes.status)) {
        response = fallbackRes;
      }
    } catch (_) {}
  }

  if (response.status === 401) {
    // Clear expired or invalid credentials
    clearAuthSession();
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('msme:session-expired', { detail: { path } }));
    }
  }

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } else if (response.status === 405) {
        errorDetail = 'Backend API is not reachable (HTTP 405 Method Not Allowed). The request hit the static frontend host instead of the FastAPI backend. Please ensure the backend is deployed/running and VITE_BACKEND_URL is configured in your environment.';
      } else if (response.status === 404) {
        errorDetail = `Backend endpoint ${path} not found (HTTP 404). Please ensure the backend server is running and VITE_BACKEND_URL is configured.`;
      }
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  // Session helpers
  getAuthToken,
  setAuthSession,
  clearAuthSession,
  logout: () => {
    clearAuthSession();
  },

  // Health
  checkHealth: () => request('/health'),

  // Authentication
  signup: async (data) => {
    const res = await request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (res.token && res.user) {
      setAuthSession(res.token, res.user);
    }
    return res;
  },

  login: async (data) => {
    const res = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (res.token && res.user) {
      setAuthSession(res.token, res.user);
    }
    return res;
  },

  demoLogin: async (archetype = 'demo-owner-1') => {
    const res = await request('/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ archetype }),
    });
    if (res.token && res.user) {
      setAuthSession(res.token, res.user);
    }
    return res;
  },

  getCurrentUser: (ownerId) => request(ownerId ? `/auth/me/${ownerId}` : '/auth/me'),

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
