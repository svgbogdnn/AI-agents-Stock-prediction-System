'use client';

import { motion } from 'framer-motion';
import { AnalysisResult } from '../types';

interface AgentRadarChartProps {
  result: AnalysisResult;
}

export default function AgentRadarChart({ result }: AgentRadarChartProps) {
  const agents = [
    { name: 'Fundamental', key: 'fundamental' },
    { name: 'Technical', key: 'technical' },
    { name: 'Sentiment', key: 'sentiment' },
    { name: 'Macro', key: 'macro' },
    { name: 'Regulatory', key: 'regulatory' },
  ];

  // Get signals and normalize to 0-100 scale
  const signals = agents.map(agent => {
    const report = result.analysis_reports[agent.key];
    if (!report) return 50;
    // Convert from -1 to +1 range to 0-100 range
    return ((report.directional_signal + 1) * 50);
  });

  // Calculate radar chart points
  const centerX = 200;
  const centerY = 200;
  const maxRadius = 120;
  const angleStep = (Math.PI * 2) / agents.length;

  const points = signals.map((signal, index) => {
    const angle = angleStep * index - Math.PI / 2; // Start from top
    const radius = (signal / 100) * maxRadius;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    return { x, y, signal, angle };
  });

  // Create path for the filled polygon
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

  // Create label positions with more padding
  const labels = agents.map((agent, index) => {
    const angle = angleStep * index - Math.PI / 2;
    const labelRadius = maxRadius + 60; // Increased from 30 to 60 for more space
    const x = centerX + labelRadius * Math.cos(angle);
    const y = centerY + labelRadius * Math.sin(angle);
    return { ...agent, x, y, signal: signals[index] };
  });

  return (
    <div className="glass rounded-xl p-6">
      <h3 className="text-lg font-bold text-white mb-4">Agent Signal Radar</h3>
      <svg viewBox="0 0 400 400" className="w-full max-w-md mx-auto">
        {/* Background circles */}
        {[25, 50, 75, 100].map((percent) => (
          <circle
            key={percent}
            cx={centerX}
            cy={centerY}
            r={(percent / 100) * maxRadius}
            fill="none"
            stroke="rgba(100, 116, 139, 0.2)"
            strokeWidth="1"
          />
        ))}

        {/* Grid lines */}
        {agents.map((_, index) => {
          const angle = angleStep * index - Math.PI / 2;
          const x2 = centerX + maxRadius * Math.cos(angle);
          const y2 = centerY + maxRadius * Math.sin(angle);
          return (
            <line
              key={index}
              x1={centerX}
              y1={centerY}
              x2={x2}
              y2={y2}
              stroke="rgba(100, 116, 139, 0.2)"
              strokeWidth="1"
            />
          );
        })}

        {/* Data polygon */}
        <motion.path
          d={pathD}
          fill="rgba(59, 130, 246, 0.2)"
          stroke="rgba(59, 130, 246, 0.8)"
          strokeWidth="2"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ transformOrigin: `${centerX}px ${centerY}px` }}
        />

        {/* Data points */}
        {points.map((point, index) => (
          <motion.g key={index}>
            <motion.circle
              cx={point.x}
              cy={point.y}
              r="4"
              fill="rgb(59, 130, 246)"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 + 0.3, duration: 0.3 }}
            />
            <motion.circle
              cx={point.x}
              cy={point.y}
              r="8"
              fill="none"
              stroke="rgb(59, 130, 246)"
              strokeWidth="2"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 0.5 }}
              transition={{ delay: index * 0.1 + 0.5, duration: 0.5 }}
            />
          </motion.g>
        ))}

        {/* Labels */}
        {labels.map((label, index) => {
          const getColor = (signal: number) => {
            if (signal > 60) return '#4ade80'; // green
            if (signal < 40) return '#f87171'; // red
            return '#fbbf24'; // yellow
          };

          return (
            <text
              key={index}
              x={label.x}
              y={label.y}
              textAnchor="middle"
              dominantBaseline="middle"
              className="text-xs font-semibold fill-slate-300"
            >
              <tspan x={label.x} dy="-0.6em">{label.name}</tspan>
              <tspan 
                x={label.x} 
                dy="1.2em" 
                className="font-bold text-sm"
                style={{ fill: getColor(label.signal) }}
              >
                {((label.signal - 50) / 50).toFixed(2)}
              </tspan>
            </text>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-6 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-400" />
          <span>Bullish (&gt;0.2)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-400" />
          <span>Neutral</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-400" />
          <span>Bearish (&lt;-0.2)</span>
        </div>
      </div>
    </div>
  );
}

