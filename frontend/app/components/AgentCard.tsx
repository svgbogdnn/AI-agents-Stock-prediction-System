'use client';

import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Loader2, TrendingUp, TrendingDown, Minus, Activity, Database, Shield } from 'lucide-react';
import { AgentStatus } from '../types';

interface AgentCardProps {
  agent: AgentStatus;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  delay: number;
  onViewDetails?: () => void;
}

// Helper function to format snake_case to Title Case
const formatLabel = (key: string): string => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Data source to badge mapping
const dataSourceInfo: Record<string, { icon: any; label: string; color: string; verified: boolean }> = {
  'Polygon.io API': { icon: Activity, label: 'Polygon.io', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30', verified: true },
  'FRED API (St. Louis Fed)': { icon: Database, label: 'FRED', color: 'bg-green-500/10 text-green-400 border-green-500/30', verified: true },
  'NewsAPI.org + Polygon.io': { icon: Database, label: 'NewsAPI', color: 'bg-purple-500/10 text-purple-400 border-purple-500/30', verified: true },
  'SEC Edgar': { icon: Shield, label: 'SEC Edgar', color: 'bg-orange-500/10 text-orange-400 border-orange-500/30', verified: true },
};

export default function AgentCard({ agent, icon: Icon, color, delay, onViewDetails }: AgentCardProps) {

  const getStatusIcon = () => {
    switch (agent.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'working':
        return <Loader2 className="w-5 h-5 text-yellow-400 animate-spin" />;
      default:
        return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };

  const getSignalIcon = () => {
    if (!agent.signal) return null;
    if (agent.signal > 0.3) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (agent.signal < -0.3) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-yellow-400" />;
  };

  const getSignalColor = () => {
    if (!agent.signal) return 'text-gray-400';
    if (agent.signal > 0.3) return 'text-green-400';
    if (agent.signal < -0.3) return 'text-red-400';
    return 'text-yellow-400';
  };

  const getConfidenceLevel = () => {
    if (!agent.confidence) return 'Unknown';
    if (agent.confidence >= 75) return 'High';
    if (agent.confidence >= 60) return 'Moderate';
    return 'Low';
  };

  const getConfidenceColor = () => {
    if (!agent.confidence) return 'text-gray-400';
    if (agent.confidence >= 75) return 'text-green-400';
    if (agent.confidence >= 60) return 'text-yellow-400';
    return 'text-orange-400';
  };

  // Get data source badge info (from keyMetrics if available)
  const dataSource = agent.keyMetrics?.data_source as string | undefined;
  const sourceBadge = dataSource ? dataSourceInfo[dataSource] : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`
        glass rounded-2xl p-6 relative overflow-hidden
        hover:shadow-glow transition-all duration-500
        ${agent.status === 'working' ? 'shadow-yellow-500/20 animate-glow' : ''}
        ${agent.status === 'completed' ? 'shadow-green-500/20' : ''}
        ${agent.status === 'error' ? 'shadow-red-500/20' : ''}
      `}
    >
      {/* Background Gradient */}
      <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-br ${color} opacity-5 rounded-full blur-3xl`} />
      
      {/* Header */}
      <div className="relative">
        <div className="flex items-start justify-between mb-5">
          <div className="flex items-center gap-3 flex-1">
            <div className={`p-3 rounded-xl bg-gradient-to-br ${color} bg-opacity-10 shadow-lg`}>
              <Icon className="w-7 h-7 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-white text-lg">{agent.name}</h3>
              <div className="flex items-center gap-2 mt-1.5">
                {getStatusIcon()}
                <span className="text-xs text-slate-400 capitalize font-semibold tracking-wide">{agent.status}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Data Source Badge */}
        {agent.status === 'completed' && sourceBadge && (
          <div className="mb-4 flex items-center gap-2">
            <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${sourceBadge.color}`}>
              <sourceBadge.icon className="w-3.5 h-3.5" />
              <span>{sourceBadge.label}</span>
              {sourceBadge.verified && (
                <CheckCircle className="w-3 h-3 text-green-400" />
              )}
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {agent.status === 'working' && (
          <div className="mb-5">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-400">Analyzing...</span>
              <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded">{agent.progress}%</span>
            </div>
            <div className="relative h-2 bg-slate-900/80 rounded-full overflow-hidden border border-slate-800/50">
              <motion.div
                className={`absolute inset-y-0 left-0 bg-gradient-to-r ${color} rounded-full`}
                initial={{ width: 0 }}
                animate={{ width: `${agent.progress}%` }}
                transition={{ duration: 0.5 }}
              />
              <motion.div
                className="absolute inset-y-0 left-0 bg-white/30 rounded-full"
                initial={{ x: '-100%' }}
                animate={{ x: '200%' }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                style={{ width: '30%' }}
              />
            </div>
          </div>
        )}

        {/* Results */}
        {agent.status === 'completed' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-3"
          >
            {/* Signal & Confidence */}
            <div className="grid grid-cols-2 gap-3">
              <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
                <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Signal</div>
                <div className={`flex items-center gap-1.5 font-bold text-lg ${getSignalColor()}`}>
                  {getSignalIcon()}
                  <span>{agent.signal ? agent.signal.toFixed(2) : 'N/A'}</span>
                </div>
              </div>
              <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
                <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Confidence</div>
                <div className="font-bold text-lg text-blue-400">
                  {agent.confidence ? `${agent.confidence.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
            </div>

            {/* Summary */}
            {agent.summary && (
              <div className="glass-dark rounded-xl p-4">
                <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Analysis</div>
                <p className="text-sm text-slate-300 line-clamp-2 leading-relaxed">{agent.summary}</p>
              </div>
            )}

            {/* View Details Button */}
            <motion.button
              onClick={onViewDetails}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`w-full glass-dark px-4 py-3 rounded-xl font-semibold text-sm hover:bg-gradient-to-r ${color} hover:bg-opacity-10 transition-all border border-slate-700/50 hover:border-slate-600/50 flex items-center justify-center gap-2`}
            >
              <Activity className="w-4 h-4" />
              View Detailed Analysis
            </motion.button>
          </motion.div>
        )}

        {/* Error State */}
        {agent.status === 'error' && (
          <div className="glass-dark rounded-xl p-4 border border-red-500/30 bg-red-500/5">
            <div className="text-sm font-semibold text-red-400">
              {agent.error || 'Analysis failed'}
            </div>
          </div>
        )}

        {/* Working Animation */}
        {agent.status === 'working' && (
          <motion.div
            className="flex items-center gap-3 text-sm font-medium"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className={`w-2 h-2 rounded-full bg-gradient-to-r ${color}`}
                  animate={{ 
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    delay: i * 0.15
                  }}
                />
              ))}
            </div>
            <span className="text-slate-400">Fetching data & analyzing...</span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
