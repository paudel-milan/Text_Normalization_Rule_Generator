import React from 'react';
import { getExportUrl } from '../api/client';

const ExportPanel = ({ config, rules }) => {
  if (!rules) return null;

  const { locale, category } = config;

  const exports = [
    {
      id: 'dfa',
      label: 'DFA',
      format: 'dfa',
      ext: 'JSON',
      icon: '{ }',
      color: '#60a5fa',
      desc: 'State machine structure',
    },
    {
      id: 'ssml',
      label: 'SSML',
      format: 'ssml',
      ext: 'XML',
      icon: '< />',
      color: '#a78bfa',
      desc: 'Template for TTS engine',
    },
    {
      id: 'regex',
      label: 'Regex',
      format: 'regex',
      ext: 'TXT',
      icon: '.*',
      color: '#34d399',
      desc: 'Pattern with documentation',
    },
    {
      id: 'bundle',
      label: 'Full Bundle',
      format: 'bundle',
      ext: 'ZIP',
      icon: '📦',
      color: '#f59e0b',
      desc: 'All files in one archive',
    },
  ];

  return (
    <div className="card export-panel" id="export-panel">
      <div className="card-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        <h3>Export Rules</h3>
      </div>

      <div className="export-grid">
        {exports.map((ex) => (
          <a
            key={ex.id}
            href={getExportUrl(ex.format, locale, category)}
            download
            className="export-card"
            id={`export-${ex.id}`}
            style={{ '--accent': ex.color }}
          >
            <span className="export-icon">{ex.icon}</span>
            <div className="export-info">
              <span className="export-label">{ex.label}</span>
              <span className="export-desc">{ex.desc}</span>
            </div>
            <span className="export-ext">.{ex.ext.toLowerCase()}</span>
          </a>
        ))}
      </div>
    </div>
  );
};

export default ExportPanel;
