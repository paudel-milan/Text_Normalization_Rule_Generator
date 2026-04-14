import React, { useState } from 'react';
import Header from './components/Header';
import ConfigPanel from './components/ConfigPanel';
import RulePreview from './components/RulePreview';
import Sandbox from './components/Sandbox';
import DfaVisualizer from './components/DfaVisualizer';
import ExportPanel from './components/ExportPanel';

const App = () => {
  const [rules, setRules] = useState(null);
  const [config, setConfig] = useState({ locale: '', category: '' });

  return (
    <div className="app-wrapper" id="app-root">
      <Header />

      <main className="main-grid">
        <section className="left-col">
          <ConfigPanel
            onRulesGenerated={setRules}
            onConfigChange={setConfig}
          />
          <Sandbox config={config} rules={rules} />
        </section>

        <section className="right-col">
          <RulePreview rules={rules} />
          <DfaVisualizer rules={rules} config={config} />
          <ExportPanel config={config} rules={rules} />
        </section>
      </main>

      <footer className="app-footer">
        <p>TTS Text Normalization Rule Engine • Samsung PRISM • {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
};

export default App;
