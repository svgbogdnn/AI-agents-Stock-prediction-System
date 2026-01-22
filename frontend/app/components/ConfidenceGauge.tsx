'use client';

import { motion } from 'framer-motion';

interface ConfidenceGaugeProps {
  confidence: number;
  label?: string;
}

export default function ConfidenceGauge({ confidence, label = 'Overall Confidence' }: ConfidenceGaugeProps) {
  const percentage = Math.min(100, Math.max(0, confidence));
  const rotation = (percentage / 100) * 180 - 90; // -90 to +90 degrees

  const getColor = () => {
    if (percentage >= 75) return { stroke: '#4ade80', glow: '#4ade80' }; // green
    if (percentage >= 60) return { stroke: '#fbbf24', glow: '#fbbf24' }; // yellow
    return { stroke: '#f87171', glow: '#f87171' }; // red
  };

  const colors = getColor();

  return (
    <div className="glass rounded-xl p-6">
      <h3 className="text-lg font-bold text-white mb-4 text-center">{label}</h3>
      <div className="relative w-full max-w-sm mx-auto">
        {/* SVG Gauge */}
        <svg viewBox="0 0 200 120" className="w-full">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="rgba(100, 116, 139, 0.2)"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((tick) => {
            const angle = (tick / 100) * 180 - 90;
            const rad = (angle * Math.PI) / 180;
            const x1 = 100 + 70 * Math.cos(rad);
            const y1 = 100 + 70 * Math.sin(rad);
            const x2 = 100 + 85 * Math.cos(rad);
            const y2 = 100 + 85 * Math.sin(rad);
            return (
              <g key={tick}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="rgba(148, 163, 184, 0.4)"
                  strokeWidth="2"
                />
                <text
                  x={100 + 95 * Math.cos(rad)}
                  y={100 + 95 * Math.sin(rad)}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  className="text-[10px] fill-slate-500 font-semibold"
                >
                  {tick}
                </text>
              </g>
            );
          })}

          {/* Colored arc (progress) */}
          <motion.path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={colors.stroke}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray="251.2" // Approximate circumference of semicircle
            strokeDashoffset={251.2 * (1 - percentage / 100)}
            initial={{ strokeDashoffset: 251.2 }}
            animate={{ strokeDashoffset: 251.2 * (1 - percentage / 100) }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            style={{
              filter: `drop-shadow(0 0 8px ${colors.glow})`,
            }}
          />

          {/* Needle */}
          <motion.g
            initial={{ rotate: -90 }}
            animate={{ rotate: rotation }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            style={{ transformOrigin: '100px 100px' }}
          >
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="35"
              stroke="#cbd5e1"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill="#cbd5e1" />
            <circle cx="100" cy="100" r="3" fill="#1e293b" />
          </motion.g>
        </svg>

        {/* Value display */}
        <motion.div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div className="text-4xl font-bold" style={{ color: colors.stroke }}>
            {percentage.toFixed(1)}%
          </div>
          <div className="text-sm text-slate-400 mt-1">
            {percentage >= 75 ? 'High' : percentage >= 60 ? 'Moderate' : 'Low'} Confidence
          </div>
        </motion.div>
      </div>

      {/* Interpretation */}
      <div className="mt-8 space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">Reliability</span>
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((bar) => (
              <motion.div
                key={bar}
                className="w-8 h-2 rounded-full bg-slate-800"
                initial={{ scaleX: 0 }}
                animate={{
                  scaleX: bar <= (percentage / 20) ? 1 : 0,
                  backgroundColor: bar <= (percentage / 20) ? colors.stroke : 'rgb(30, 41, 59)'
                }}
                transition={{ delay: bar * 0.1 + 0.8, duration: 0.3 }}
                style={{ transformOrigin: 'left' }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

