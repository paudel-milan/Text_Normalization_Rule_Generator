import React, { useState } from 'react';

const RulePreview = ({ rules }) => {
  const [activeTab, setActiveTab] = useState('regex');

  if (!rules) {
    return (
      <div className="card rule-preview-card" id="rule-preview">
        <div className="card-header">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
          </svg>
          <h3>Rule Preview</h3>
        </div>
        <div className="empty-state">
          <p>Generate rules to see the preview</p>
        </div>
      </div>
    );
  }

  const { regex, dfa, ssml } = rules;

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="card rule-preview-card" id="rule-preview">
      <div className="card-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
        </svg>
        <h3>Rule Preview</h3>
        <span className="status-badge success">{rules.language} / {rules.category}</span>
      </div>

      <div className="tab-bar">
        {['regex', 'ssml', 'dfa'].map((tab) => (
          <button
            key={tab}
            className={`tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'regex' && (
          <div className="preview-section">
            <div className="preview-label">
              <span>Generated Pattern</span>
              <button className="copy-btn" onClick={() => copyToClipboard(regex.pattern)} title="Copy">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
              </button>
            </div>
            <pre className="code-block regex-highlight">{regex.pattern}</pre>
            <div className="validity-indicator">
              {regex.valid ? (
                <span className="valid">✓ Valid regex pattern</span>
              ) : (
                <span className="invalid">✗ Invalid: {regex.error}</span>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ssml' && (
          <div className="preview-section">
            <div className="preview-label">
              <span>SSML Template</span>
              <button className="copy-btn" onClick={() => copyToClipboard(ssml.full_template)} title="Copy">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
              </button>
            </div>
            <pre className="code-block ssml-highlight">{ssml.full_template}</pre>
            <div className="ssml-meta">
              <span className="meta-tag">interpret-as: {ssml.interpret_as}</span>
              {Object.entries(ssml.attributes || {}).map(([k, v]) => (
                <span key={k} className="meta-tag">{k}: {v}</span>
              ))}
            </div>
            <div className="preview-label" style={{ marginTop: '1rem' }}>
              <span>Example Output</span>
            </div>
            <pre className="code-block example-highlight">{ssml.example}</pre>
          </div>
        )}

        {activeTab === 'dfa' && (
          <div className="preview-section">
            <div className="preview-label">
              <span>DFA Structure ({dfa.state_count} states)</span>
              <button className="copy-btn" onClick={() => copyToClipboard(JSON.stringify(dfa, null, 2))} title="Copy JSON">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>
              </button>
            </div>
            <pre className="code-block json-highlight">{JSON.stringify(dfa, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default RulePreview;
