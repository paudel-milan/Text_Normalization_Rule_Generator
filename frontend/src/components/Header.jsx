import React from 'react';

const Header = () => {
  return (
    <header className="app-header" id="app-header">
      <div className="header-content">
        <div className="header-brand">
          <div className="header-logo">
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="36" y2="36">
                  <stop offset="0%" stopColor="#60a5fa" />
                  <stop offset="100%" stopColor="#a78bfa" />
                </linearGradient>
              </defs>
              <rect rx="8" width="36" height="36" fill="url(#logo-grad)" opacity="0.15" />
              <text x="18" y="24" textAnchor="middle" fill="url(#logo-grad)" fontSize="18" fontWeight="700" fontFamily="monospace">TN</text>
            </svg>
          </div>
          <div>
            <h1 className="header-title">Text Normalization Rule Engine</h1>
            <p className="header-subtitle">DFA + SSML + Regex Generation for TTS Systems</p>
          </div>
        </div>
        <div className="header-badge">
          <span className="badge">Samsung PRISM</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
