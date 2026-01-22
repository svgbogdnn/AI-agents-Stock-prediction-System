'use client';

import { motion } from 'framer-motion';
import { Sparkles, TrendingUp, Shield, Clock, RotateCcw, ChevronDown } from 'lucide-react';
import { AnalysisResult } from '../types';
import { useState } from 'react';
import AgentRadarChart from './AgentRadarChart';
import ConfidenceGauge from './ConfidenceGauge';

interface ResultsPanelProps {
  result: AnalysisResult;
  onReset: () => void;
}

// Helper function to format snake_case to Title Case
const formatLabel = (key: string): string => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper function to format rationale text
const formatRationale = (text: string) => {
  // Remove diamond icons (◆)
  let cleanText = text.replace(/◆\s*/g, '');
  
  // Split into lines and format
  const lines: JSX.Element[] = [];
  
  // Split by agent sections (looking for patterns like "Fundamental:", "Technical:", etc.)
  const agentSections = cleanText.split(/\n\n|\n(?=[A-Z][a-z]+:)/);
  
  agentSections.forEach((section, idx) => {
    const trimmed = section.trim();
    if (!trimmed) return;
    
    // Check if this is a checkmark list section
    if (trimmed.includes('✅')) {
      // Split by checkmarks and create separate lines
      const items = trimmed.split('✅').filter(s => s.trim());
      items.forEach((item, i) => {
        lines.push(
          <div key={`${idx}-check-${i}`} className="flex items-start gap-2">
            <span className="text-green-400 mt-0.5">✅</span>
            <span className="text-slate-300">{item.trim()}</span>
          </div>
        );
      });
    } else if (trimmed.match(/^(Fundamental|Technical|Sentiment|Macro|Regulatory):/)) {
      // Agent section header
      const [label, ...rest] = trimmed.split(':');
      lines.push(
        <div key={`${idx}-section`} className="mt-3">
          <span className="font-bold text-blue-400">{label}:</span>
          <span className="text-slate-300"> {rest.join(':').trim()}</span>
        </div>
      );
    } else if (trimmed.startsWith('Weighted Signal:') || trimmed.startsWith('Average Confidence:')) {
      // Summary metrics
      lines.push(
        <div key={`${idx}-metric`} className="mt-3 font-semibold text-slate-300">
          {trimmed}
        </div>
      );
    } else {
      // Regular paragraph
      lines.push(
        <p key={`${idx}-para`} className="text-slate-300">
          {trimmed}
        </p>
      );
    }
  });
  
  return lines.length > 0 ? lines : (
    <p className="text-slate-300">{cleanText}</p>
  );
};

export default function ResultsPanel({ result, onReset }: ResultsPanelProps) {
  const [showDetails, setShowDetails] = useState(false);

  const getRecommendationColor = () => {
    if (result.recommendation === 'BUY') return 'from-green-500 to-emerald-400';
    if (result.recommendation === 'SELL') return 'from-red-500 to-pink-400';
    return 'from-yellow-500 to-orange-400';
  };

  const getRecommendationBg = () => {
    if (result.recommendation === 'BUY') return 'shadow-green-500/30';
    if (result.recommendation === 'SELL') return 'shadow-red-500/30';
    return 'shadow-yellow-500/30';
  };

  const getRiskColor = () => {
    if (result.risk_level === 'LOW') return 'text-green-400';
    if (result.risk_level === 'HIGH') return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Main Results Card */}
      <div className={`glass rounded-3xl p-10 ${getRecommendationBg()}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-blue-400" />
            <h2 className="text-3xl font-bold text-white">Final Prediction</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onReset}
            className="glass-dark px-5 py-3 rounded-xl flex items-center gap-2 text-sm font-semibold hover:bg-slate-700/70 transition-colors border border-slate-700/50"
          >
            <RotateCcw className="w-4 h-4" />
            New Analysis
          </motion.button>
        </div>

        {/* Recommendation */}
        <div className="mb-10">
          <div className={`inline-block px-12 py-6 rounded-3xl bg-gradient-to-r ${getRecommendationColor()} shadow-2xl relative overflow-hidden group`}>
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent group-hover:translate-x-full transition-transform duration-1000" />
            <div className="text-sm font-semibold text-white/80 mb-2 uppercase tracking-wider relative z-10">
              Recommendation for {result.ticker}
            </div>
            <div className="text-6xl font-black text-white relative z-10 tracking-tight">{result.recommendation}</div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
          <div className="glass-dark rounded-2xl p-6 hover:bg-slate-800/60 transition-all hover:shadow-glow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs mb-3 font-semibold uppercase tracking-wider">
              <TrendingUp className="w-4 h-4" />
              Confidence
            </div>
            <div className="text-4xl font-black text-blue-400">
              {result.confidence.toFixed(1)}%
            </div>
          </div>

          <div className="glass-dark rounded-2xl p-6 hover:bg-slate-800/60 transition-all hover:shadow-glow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs mb-3 font-semibold uppercase tracking-wider">
              <Shield className="w-4 h-4" />
              Risk Level
            </div>
            <div className={`text-4xl font-black ${getRiskColor()}`}>
              {result.risk_level}
            </div>
          </div>

          <div className="glass-dark rounded-2xl p-6 hover:bg-slate-800/60 transition-all hover:shadow-glow-sm">
            <div className="text-slate-500 text-xs mb-3 font-semibold uppercase tracking-wider">
              Signal Strength
            </div>
            <div className="text-4xl font-black text-purple-400">
              {result.weighted_signal >= 0 ? '+' : ''}{result.weighted_signal.toFixed(3)}
            </div>
          </div>

          <div className="glass-dark rounded-2xl p-6 hover:bg-slate-800/60 transition-all hover:shadow-glow-sm">
            <div className="flex items-center gap-2 text-slate-500 text-xs mb-3 font-semibold uppercase tracking-wider">
              <Clock className="w-4 h-4" />
              Analysis Time
            </div>
            <div className="text-4xl font-black text-cyan-400">
              {result.elapsed_seconds.toFixed(1)}s
            </div>
          </div>
        </div>

        {/* Interactive Visualizations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <AgentRadarChart result={result} />
          <ConfidenceGauge confidence={result.confidence} />
        </div>

        {/* Rationale */}
        <div className="glass-dark rounded-2xl p-6 border border-slate-800/50">
          <h3 className="text-lg font-bold mb-5 flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5 text-blue-400" />
            AI Rationale
          </h3>
          <div className="space-y-2 leading-relaxed text-base">
            {formatRationale(result.rationale || 'Based on comprehensive multi-agent analysis across fundamental, technical, sentiment, macro-economic, and regulatory dimensions.')}
          </div>
        </div>

        {/* Show Details Toggle */}
        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={() => setShowDetails(!showDetails)}
          className="w-full mt-6 glass-dark px-6 py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-slate-700/70 transition-all border border-slate-700/50 font-semibold"
        >
          <span className="text-sm">
            {showDetails ? 'Hide' : 'Show'} Detailed Agent Responses
          </span>
          <motion.div
            animate={{ rotate: showDetails ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChevronDown className="w-5 h-5" />
          </motion.div>
        </motion.button>
      </div>

      {/* Detailed Agent Responses */}
      <motion.div
        initial={false}
        animate={{
          height: showDetails ? 'auto' : 0,
          opacity: showDetails ? 1 : 0
        }}
        transition={{ duration: 0.3 }}
        className="overflow-hidden"
      >
        <div className="space-y-5">
          {Object.entries(result.analysis_reports).map(([agentId, response], index) => (
            <motion.div
              key={agentId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-7 hover:shadow-glow-sm transition-all"
            >
              <div className="flex items-start justify-between mb-5">
                <div>
                  <h4 className="font-bold text-xl capitalize text-white">{agentId.replace('_', ' ')}</h4>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-sm font-semibold text-slate-400">
                      Signal: <span className="text-blue-400">{response.directional_signal.toFixed(2)}</span>
                    </span>
                    <span className="text-sm font-semibold text-slate-400">
                      Confidence: <span className="text-cyan-400">{response.confidence_score.toFixed(1)}%</span>
                    </span>
                  </div>
                </div>
                {response.data_source && (
                  <span className="text-xs font-semibold text-slate-500 bg-slate-800/50 px-4 py-2 rounded-full border border-slate-700/50">
                    {response.data_source}
                  </span>
                )}
              </div>

              {response.summary && (
                <p className="text-sm text-slate-300 mb-5 leading-relaxed">{response.summary}</p>
              )}

              {response.key_metrics && Object.keys(response.key_metrics).length > 0 && (
                <div className="glass-dark rounded-xl p-5 border border-slate-800/50">
                  <div className="text-xs text-slate-500 mb-3 font-semibold uppercase tracking-wider">Key Metrics</div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(response.key_metrics)
                      .filter(([key, value]) => {
                        // Filter out arrays, objects, and metadata fields
                        const excludedKeys = ['news_articles', 'data_source', 'positive_count', 'neutral_count', 'negative_count'];
                        return !excludedKeys.includes(key) && typeof value !== 'object';
                      })
                      .map(([key, value]) => (
                      <div key={key}>
                        <div className="text-xs text-slate-500 mb-1 font-medium">{formatLabel(key)}</div>
                        <div className="text-sm font-bold text-white">
                          {typeof value === 'number' 
                            ? value.toFixed(2) 
                            : typeof value === 'string' && value.length > 30
                            ? value.substring(0, 30) + '...'
                            : String(value)
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}

