import React, { useState, useEffect } from 'react';
import { getLanguages, getCategories, generateRules } from '../api/client';

const ConfigPanel = ({ onRulesGenerated, onConfigChange }) => {
  const [languages, setLanguages] = useState([]);
  const [categories, setCategories] = useState([]);
  const [locale, setLocale] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getLanguages()
      .then((langs) => {
        setLanguages(langs);
        if (langs.length > 0) {
          setLocale(langs[0].locale);
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!locale) return;
    getCategories(locale)
      .then((cats) => {
        setCategories(cats);
        if (cats.length > 0) {
          setCategory(cats[0]);
        }
      })
      .catch((e) => setError(e.message));
  }, [locale]);

  useEffect(() => {
    if (locale && category) {
      onConfigChange?.({ locale, category });
    }
  }, [locale, category]);

  const handleGenerate = async () => {
    if (!locale || !category) return;
    setLoading(true);
    setError('');
    try {
      const rules = await generateRules(locale, category);
      onRulesGenerated(rules);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const selectedLang = languages.find((l) => l.locale === locale);

  return (
    <div className="card config-panel" id="config-panel">
      <div className="card-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
        <h3>Configuration</h3>
      </div>

      {error && <div className="error-msg">{error}</div>}

      <div className="form-group">
        <label htmlFor="language-select">Language</label>
        <select
          id="language-select"
          value={locale}
          onChange={(e) => setLocale(e.target.value)}
        >
          {languages.map((l) => (
            <option key={l.locale} value={l.locale}>
              {l.language} ({l.locale}) — {l.script}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="category-select">Category</label>
        <div className="category-grid">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`category-chip ${category === cat ? 'active' : ''}`}
              onClick={() => setCategory(cat)}
              id={`category-${cat}`}
            >
              {getCategoryIcon(cat)}
              <span>{cat}</span>
            </button>
          ))}
        </div>
      </div>

      {selectedLang && (
        <div className="config-info">
          <span className="info-tag">{selectedLang.script}</span>
          <span className="info-tag">{selectedLang.categories.length} categories</span>
        </div>
      )}

      <button
        className="btn-primary generate-btn"
        onClick={handleGenerate}
        disabled={loading || !locale || !category}
        id="generate-btn"
      >
        {loading ? (
          <>
            <span className="spinner" />
            Generating...
          </>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Generate Rules
          </>
        )}
      </button>
    </div>
  );
};

function getCategoryIcon(cat) {
  const icons = {
    cardinal: '123',
    ordinal: '1st',
    currency: '₹',
    date: '📅',
    time: '⏰',
    units: '📏',
  };
  return <span className="cat-icon">{icons[cat] || '•'}</span>;
}

export default ConfigPanel;
