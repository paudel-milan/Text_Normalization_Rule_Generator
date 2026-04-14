/**
 * API Client — Fetch wrapper for all backend endpoints.
 */

const API_BASE = '/api';

async function request(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // For blob responses (exports)
  if (options.responseType === 'blob') {
    return response.blob();
  }

  return response.json();
}

export async function getLanguages() {
  const data = await request('/languages');
  return data.languages;
}

export async function getCategories(locale) {
  const data = await request(`/languages/${locale}/categories`);
  return data.categories;
}

export async function generateRules(locale, category) {
  return request('/generate', {
    method: 'POST',
    body: JSON.stringify({ locale, category }),
  });
}

export async function normalizeText(locale, category, text) {
  return request('/normalize', {
    method: 'POST',
    body: JSON.stringify({ locale, category, text }),
  });
}

export async function validateRules(locale, category, customTests = null) {
  return request('/validate', {
    method: 'POST',
    body: JSON.stringify({ locale, category, custom_tests: customTests }),
  });
}

export async function simulateDfa(locale, category, inputString) {
  return request('/dfa/simulate', {
    method: 'POST',
    body: JSON.stringify({ locale, category, input_string: inputString }),
  });
}

export function getExportUrl(format, locale, category) {
  return `${API_BASE}/export/${format}?locale=${encodeURIComponent(locale)}&category=${encodeURIComponent(category)}`;
}
