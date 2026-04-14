import React, { useState } from 'react';
import { normalizeText } from '../api/client';

const Sandbox = ({ config, rules }) => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNormalize = async () => {
    if (!input.trim() || !config?.locale || !config?.category) return;
    setLoading(true);
    setError('');
    try {
      const res = await normalizeText(config.locale, config.category, input);
      setResult(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const getPlaceholder = () => {
    const placeholders = {
      currency: 'e.g., मेरे पास ₹५०० है',
      cardinal: 'e.g., कुल ५०० लोग आए',
      ordinal: 'e.g., वह ५वां खिलाड़ी है',
      date: 'e.g., आज १५/०८/२०२३ है',
      time: 'e.g., मीटिंग ५:३० पर है',
      units: 'e.g., वज़न ५ किलोग्राम है',
    };
    return placeholders[config?.category] || 'Type a sentence to normalize...';
  };

  return (
    <div className="card sandbox-card" id="sandbox">
      <div className="card-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
        </svg>
        <h3>Validation Sandbox</h3>
      </div>

      <div className="sandbox-input-row">
        <input
          type="text"
          id="sandbox-input"
          className="sandbox-input"
          placeholder={getPlaceholder()}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleNormalize()}
        />
        <button
          className="btn-success"
          onClick={handleNormalize}
          disabled={loading || !input.trim()}
          id="normalize-btn"
        >
          {loading ? <span className="spinner small" /> : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12" /></svg>
          )}
          Normalize
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <div className="sandbox-results fade-in">
          <div className="result-row">
            <span className="result-label">Original</span>
            <div className="result-value original-text">
              {renderHighlightedText(result.original, result.matches)}
            </div>
          </div>
          <div className="result-row">
            <span className="result-label">Normalized</span>
            <div className="result-value normalized-text">{result.normalized}</div>
          </div>
          <div className="result-row">
            <span className="result-label">SSML Output</span>
            <pre className="result-value ssml-output">{result.ssml_output}</pre>
          </div>
          {result.pattern_used && (
            <div className="result-row">
              <span className="result-label">Pattern</span>
              <code className="result-value pattern-used">{result.pattern_used}</code>
            </div>
          )}
          <div className="result-row">
            <span className="result-label">Matches</span>
            <span className="result-value match-count">
              {result.matches.length} match{result.matches.length !== 1 ? 'es' : ''} found
            </span>
          </div>
          {result.matches.map((m, i) => (
            <div key={i} className="match-detail">
              <span className="match-text">"{m.matched_text}"</span>
              <span className="match-arrow">→</span>
              <span className="match-normalized">"{m.normalized_form}"</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

function renderHighlightedText(text, matches) {
  if (!matches || matches.length === 0) return text;

  const parts = [];
  let lastIdx = 0;
  for (const m of matches) {
    const [start, end] = m.span;
    if (start > lastIdx) {
      parts.push(<span key={`t-${lastIdx}`}>{text.slice(lastIdx, start)}</span>);
    }
    parts.push(
      <mark key={`m-${start}`} className="match-highlight" title={`→ ${m.normalized_form}`}>
        {text.slice(start, end)}
      </mark>
    );
    lastIdx = end;
  }
  if (lastIdx < text.length) {
    parts.push(<span key={`t-${lastIdx}`}>{text.slice(lastIdx)}</span>);
  }
  return parts;
}

export default Sandbox;
