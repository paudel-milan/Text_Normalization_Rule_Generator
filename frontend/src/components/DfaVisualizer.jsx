import React, { useRef, useEffect, useState } from 'react';
import { simulateDfa } from '../api/client';

const DfaVisualizer = ({ rules, config }) => {
  const canvasRef = useRef(null);
  const [simInput, setSimInput] = useState('');
  const [simResult, setSimResult] = useState(null);
  const [simStep, setSimStep] = useState(-1);
  const [animating, setAnimating] = useState(false);

  const dfa = rules?.dfa;

  useEffect(() => {
    if (!dfa || !canvasRef.current) return;
    drawDfa(canvasRef.current, dfa, simResult, simStep);
  }, [dfa, simResult, simStep]);

  const handleSimulate = async () => {
    if (!simInput || !config?.locale || !config?.category) return;
    try {
      const res = await simulateDfa(config.locale, config.category, simInput);
      setSimResult(res);
      setSimStep(-1);
      animateSteps(res.steps);
    } catch (e) {
      console.error(e);
    }
  };

  const animateSteps = (steps) => {
    setAnimating(true);
    let i = -1;
    const interval = setInterval(() => {
      i++;
      if (i >= steps.length) {
        clearInterval(interval);
        setAnimating(false);
        return;
      }
      setSimStep(i);
    }, 600);
  };

  if (!dfa) {
    return (
      <div className="card dfa-viz-card" id="dfa-visualizer">
        <div className="card-header">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="18" cy="18" r="3" /><circle cx="6" cy="6" r="3" /><path d="M13 6h3a2 2 0 0 1 2 2v7" /><path d="M11 18H8a2 2 0 0 1-2-2V9" />
          </svg>
          <h3>DFA Visualizer</h3>
        </div>
        <div className="empty-state"><p>Generate rules to visualize the DFA</p></div>
      </div>
    );
  }

  return (
    <div className="card dfa-viz-card" id="dfa-visualizer">
      <div className="card-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="18" cy="18" r="3" /><circle cx="6" cy="6" r="3" /><path d="M13 6h3a2 2 0 0 1 2 2v7" /><path d="M11 18H8a2 2 0 0 1-2-2V9" />
        </svg>
        <h3>DFA Visualizer</h3>
        <span className="status-badge info">{dfa.state_count} states</span>
      </div>

      <canvas
        ref={canvasRef}
        width={700}
        height={350}
        className="dfa-canvas"
        id="dfa-canvas"
      />

      <div className="sim-controls">
        <input
          type="text"
          id="sim-input"
          className="sim-input"
          placeholder="Enter string to simulate (e.g., ₹500)"
          value={simInput}
          onChange={(e) => setSimInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSimulate()}
        />
        <button className="btn-accent" onClick={handleSimulate} disabled={animating || !simInput}>
          {animating ? <span className="spinner small" /> : '▶'} Simulate
        </button>
      </div>

      {simResult && (
        <div className={`sim-result ${simResult.accepted ? 'accepted' : 'rejected'}`}>
          <span className="sim-verdict">
            {simResult.accepted ? '✓ ACCEPTED' : '✗ REJECTED'}
          </span>
          <span className="sim-final">Final state: {simResult.final_state}</span>
        </div>
      )}
    </div>
  );
};

// ======================================================================
// Canvas drawing
// ======================================================================

function drawDfa(canvas, dfa, simResult, currentStep) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const dpr = window.devicePixelRatio || 1;

  canvas.width = W * dpr;
  canvas.height = H * dpr;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  ctx.scale(dpr, dpr);

  ctx.clearRect(0, 0, W, H);

  const states = dfa.states || [];
  const transitions = dfa.transitions || {};
  const startState = dfa.start_state;
  const acceptStates = new Set(dfa.accept_states || []);
  const n = states.length;
  if (n === 0) return;

  // Layout: arrange states in a horizontal line or circle
  const positions = {};
  if (n <= 8) {
    // Horizontal layout
    const gap = W / (n + 1);
    states.forEach((s, i) => {
      positions[s] = { x: gap * (i + 1), y: H / 2 };
    });
  } else {
    // Circle layout
    const cx = W / 2, cy = H / 2, r = Math.min(W, H) / 2.5;
    states.forEach((s, i) => {
      const angle = (2 * Math.PI * i) / n - Math.PI / 2;
      positions[s] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
    });
  }

  const R = 28;

  // Determine active states in simulation
  const activeEdge = currentStep >= 0 && simResult?.steps?.[currentStep];
  const visitedStates = new Set();
  if (simResult?.steps && currentStep >= 0) {
    for (let i = 0; i <= currentStep; i++) {
      visitedStates.add(simResult.steps[i].state);
      if (simResult.steps[i].next_state) {
        visitedStates.add(simResult.steps[i].next_state);
      }
    }
  }

  // Draw edges
  const drawnEdges = {};
  for (const [src, edges] of Object.entries(transitions)) {
    // Group edges by target
    const byTarget = {};
    for (const [symbol, dst] of Object.entries(edges)) {
      if (!byTarget[dst]) byTarget[dst] = [];
      byTarget[dst].push(symbol);
    }

    for (const [dst, symbols] of Object.entries(byTarget)) {
      const label = symbols.map(s => truncateLabel(s)).join(', ');
      const p1 = positions[src];
      const p2 = positions[dst];
      if (!p1 || !p2) continue;

      const isActive = activeEdge && activeEdge.state === src && activeEdge.next_state === dst;

      if (src === dst) {
        // Self-loop
        drawSelfLoop(ctx, p1, R, label, isActive);
      } else {
        // Check for reverse edge
        const reverseKey = `${dst}->${src}`;
        const forwardKey = `${src}->${dst}`;
        const hasBidi = transitions[dst] && Object.values(transitions[dst]).includes(src);
        const offset = hasBidi && !drawnEdges[reverseKey] ? 12 : 0;

        drawArrow(ctx, p1, p2, R, label, isActive, offset);
        drawnEdges[forwardKey] = true;
      }
    }
  }

  // Draw start arrow
  const startPos = positions[startState];
  if (startPos) {
    ctx.save();
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(startPos.x - R - 30, startPos.y);
    ctx.lineTo(startPos.x - R - 2, startPos.y);
    ctx.stroke();
    // Arrowhead
    ctx.fillStyle = '#94a3b8';
    ctx.beginPath();
    ctx.moveTo(startPos.x - R - 2, startPos.y);
    ctx.lineTo(startPos.x - R - 10, startPos.y - 5);
    ctx.lineTo(startPos.x - R - 10, startPos.y + 5);
    ctx.fill();
    ctx.restore();
  }

  // Draw states
  for (const s of states) {
    const pos = positions[s];
    const isAccept = acceptStates.has(s);
    const isStart = s === startState;
    const isCurrent = activeEdge && (activeEdge.next_state === s || (currentStep === 0 && activeEdge.state === s));
    const isVisited = visitedStates.has(s);

    ctx.save();

    // Glow for current state
    if (isCurrent) {
      ctx.shadowColor = '#60a5fa';
      ctx.shadowBlur = 20;
    }

    // Fill
    if (isCurrent) {
      ctx.fillStyle = 'rgba(96, 165, 250, 0.3)';
    } else if (isVisited) {
      ctx.fillStyle = 'rgba(96, 165, 250, 0.1)';
    } else {
      ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
    }

    ctx.beginPath();
    ctx.arc(pos.x, pos.y, R, 0, Math.PI * 2);
    ctx.fill();

    // Border
    ctx.strokeStyle = isCurrent ? '#60a5fa' : isVisited ? '#475569' : '#334155';
    ctx.lineWidth = isCurrent ? 2.5 : 1.5;
    ctx.stroke();

    // Double circle for accept states
    if (isAccept) {
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, R - 5, 0, Math.PI * 2);
      ctx.strokeStyle = isCurrent ? '#60a5fa' : '#34d399';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    ctx.shadowBlur = 0;

    // Label
    ctx.fillStyle = isCurrent ? '#60a5fa' : '#e2e8f0';
    ctx.font = '13px "Inter", system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(s, pos.x, pos.y);

    ctx.restore();
  }
}

function drawArrow(ctx, from, to, radius, label, isActive, offset = 0) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const ux = dx / dist;
  const uy = dy / dist;

  // Perpendicular offset for bidirectional edges
  const px = -uy * offset;
  const py = ux * offset;

  const x1 = from.x + ux * radius + px;
  const y1 = from.y + uy * radius + py;
  const x2 = to.x - ux * radius + px;
  const y2 = to.y - uy * radius + py;

  ctx.save();
  ctx.strokeStyle = isActive ? '#60a5fa' : '#475569';
  ctx.lineWidth = isActive ? 2 : 1;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();

  // Arrowhead
  const angle = Math.atan2(y2 - y1, x2 - x1);
  const aLen = 8;
  ctx.fillStyle = isActive ? '#60a5fa' : '#475569';
  ctx.beginPath();
  ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - aLen * Math.cos(angle - 0.35), y2 - aLen * Math.sin(angle - 0.35));
  ctx.lineTo(x2 - aLen * Math.cos(angle + 0.35), y2 - aLen * Math.sin(angle + 0.35));
  ctx.fill();

  // Label
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  ctx.fillStyle = isActive ? '#93c5fd' : '#94a3b8';
  ctx.font = '11px "Fira Code", monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'bottom';
  ctx.fillText(label, mx - uy * 12, my + ux * 12 - 4);
  ctx.restore();
}

function drawSelfLoop(ctx, pos, radius, label, isActive) {
  ctx.save();
  const lx = pos.x;
  const ly = pos.y - radius - 20;
  ctx.strokeStyle = isActive ? '#60a5fa' : '#475569';
  ctx.lineWidth = isActive ? 2 : 1;
  ctx.beginPath();
  ctx.arc(lx, ly, 14, 0.3, Math.PI * 2 - 0.3);
  ctx.stroke();

  // Arrowhead
  ctx.fillStyle = isActive ? '#60a5fa' : '#475569';
  const ax = lx + 14 * Math.cos(0.3);
  const ay = ly + 14 * Math.sin(0.3);
  ctx.beginPath();
  ctx.moveTo(ax, ay);
  ctx.lineTo(ax + 5, ay - 5);
  ctx.lineTo(ax - 3, ay - 5);
  ctx.fill();

  // Label
  ctx.fillStyle = isActive ? '#93c5fd' : '#94a3b8';
  ctx.font = '10px "Fira Code", monospace';
  ctx.textAlign = 'center';
  ctx.fillText(label, lx, ly - 18);
  ctx.restore();
}

function truncateLabel(s) {
  if (s.length > 14) return s.slice(0, 12) + '…';
  return s;
}

export default DfaVisualizer;
