'use client';

import { motion } from 'framer-motion';
import { Brain, Sparkles, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { OrchestratorStatus } from '../types';

interface OrchestratorCardProps {
  ticker: string;
  status: OrchestratorStatus;
}

export default function OrchestratorCard({ ticker, status }: OrchestratorCardProps) {
  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle className="w-8 h-8 text-green-400" />;
      case 'error':
        return <XCircle className="w-8 h-8 text-red-400" />;
      case 'idle':
        return <Brain className="w-8 h-8 text-gray-400" />;
      default:
        return <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'shadow-green-500/20';
      case 'error':
        return 'shadow-red-500/20';
      case 'idle':
        return 'shadow-slate-500/20';
      default:
        return 'shadow-blue-500/30';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`glass rounded-3xl p-8 ${getStatusColor()}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          {getStatusIcon()}
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2 text-white">
              Strategist Orchestrator
              <Sparkles className="w-5 h-5 text-blue-400" />
            </h2>
            <p className="text-slate-400 text-sm mt-1.5 font-medium">Coordinator Pattern • Hub-and-Spoke Architecture</p>
          </div>
        </div>
        <div className="text-right">
          <div className="px-4 py-2 rounded-xl bg-blue-500/10 border border-blue-500/30">
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">{ticker}</div>
            <div className="text-xs text-slate-500 mt-1 font-semibold">Target Stock</div>
          </div>
        </div>
      </div>

      {/* Status Message */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-lg text-white font-semibold">{status.message}</p>
          <span className="text-sm font-bold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full">{status.progress}%</span>
        </div>
        
        {/* Progress Bar */}
        <div className="relative h-3 bg-slate-900/80 rounded-full overflow-hidden border border-slate-800/50">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-600 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${status.progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
          {status.status === 'analyzing' && (
            <motion.div
              className="absolute inset-y-0 left-0 bg-gradient-to-r from-transparent via-white/40 to-transparent rounded-full"
              initial={{ x: '-100%' }}
              animate={{ x: '200%' }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
              style={{ width: '50%' }}
            />
          )}
        </div>
      </div>

      {/* Status Details */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
          <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Protocol</div>
          <div className="text-base font-bold text-blue-400">A2A v0.3.0</div>
        </div>
        <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
          <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Transport</div>
          <div className="text-base font-bold text-cyan-400">JSONRPC</div>
        </div>
        <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
          <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">Active Agents</div>
          <div className="text-base font-bold text-purple-400">6 Specialists</div>
        </div>
        <div className="glass-dark rounded-xl p-4 hover:bg-slate-800/60 transition-colors">
          <div className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wider">LLM Model</div>
          <div className="text-base font-bold text-green-400">Gemini 2.0</div>
        </div>
      </div>

      {/* Activity Indicator */}
      {(status.status === 'analyzing' || status.status === 'synthesizing') && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-6 flex items-center gap-3 text-sm font-medium"
        >
          <div className="flex gap-1.5">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2.5 h-2.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                animate={{ 
                  scale: [1, 1.5, 1],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
          <span className="text-blue-300">Coordinating parallel agent execution...</span>
        </motion.div>
      )}
    </motion.div>
  );
}

