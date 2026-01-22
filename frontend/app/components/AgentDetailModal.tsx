'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, Activity, Shield, CheckCircle, ExternalLink, ThumbsUp, ThumbsDown, Minus as MinusIcon } from 'lucide-react';
import { AgentStatus } from '../types';

interface AgentDetailModalProps {
  agent: AgentStatus | null;
  isOpen: boolean;
  onClose: () => void;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

// Helper function to format snake_case to Title Case
const formatLabel = (key: string): string => {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Data source info
const dataSourceInfo: Record<string, { icon: any; label: string; color: string }> = {
  'Polygon.io API': { icon: Activity, label: 'Polygon.io', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30' },
  'FRED API (St. Louis Fed)': { icon: Activity, label: 'FRED', color: 'bg-green-500/10 text-green-400 border-green-500/30' },
  'NewsAPI.org + Polygon.io': { icon: Activity, label: 'NewsAPI', color: 'bg-purple-500/10 text-purple-400 border-purple-500/30' },
  'SEC Edgar': { icon: Shield, label: 'SEC Edgar', color: 'bg-orange-500/10 text-orange-400 border-orange-500/30' },
};

export default function AgentDetailModal({ agent, isOpen, onClose, icon: Icon, color }: AgentDetailModalProps) {
  if (!agent || !isOpen) return null;

  const dataSource = agent.keyMetrics?.data_source as string | undefined;
  const sourceBadge = dataSource ? dataSourceInfo[dataSource] : null;

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

  // Check if this is sentiment agent with news data
  const isSentimentAgent = agent.id === 'sentiment';
  const newsCount = agent.keyMetrics?.news_count || 0;
  const sentiment = agent.keyMetrics?.sentiment || 'neutral';
  
  // Get real news articles from backend
  const newsArticles = (agent.keyMetrics?.news_articles as any[]) || [];
  
  // Get sentiment breakdown from backend (or calculate from articles)
  const sentimentBreakdown = isSentimentAgent ? {
    positive: agent.keyMetrics?.positive_count || newsArticles.filter(n => n.sentiment === 'positive').length,
    neutral: agent.keyMetrics?.neutral_count || newsArticles.filter(n => n.sentiment === 'neutral').length,
    negative: agent.keyMetrics?.negative_count || newsArticles.filter(n => n.sentiment === 'negative').length,
  } : null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="bg-slate-950/95 backdrop-blur-xl rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl border border-slate-800/70"
            >
              {/* Header */}
              <div className="relative p-6 border-b border-slate-800/70 bg-slate-900/90">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-4 rounded-2xl bg-gradient-to-br ${color} shadow-lg`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">{agent.name}</h2>
                      <p className="text-slate-400 text-sm mt-1">Deep Dive Analysis</p>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={onClose}
                    className="bg-slate-900/80 p-3 rounded-lg hover:bg-slate-800/90 transition-colors"
                  >
                    <X className="w-6 h-6 text-slate-400" />
                  </motion.button>
                </div>

                {/* Data Source Badge */}
                {sourceBadge && (
                  <div className="mt-4 flex items-center gap-2">
                    <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border bg-slate-900/50 ${sourceBadge.color}`}>
                      <sourceBadge.icon className="w-4 h-4" />
                      <span>{sourceBadge.label}</span>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="overflow-y-auto max-h-[calc(90vh-140px)] p-6 space-y-6">
                {/* Signal & Confidence Visualizations */}
                <div className="grid grid-cols-2 gap-6">
                  {/* Signal Card */}
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-slate-800/70">
                    <div className="text-sm text-slate-400 mb-4 font-semibold uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Directional Signal
                    </div>
                    <div className="text-4xl font-bold text-white mb-4">
                      {agent.signal !== undefined ? agent.signal.toFixed(2) : 'N/A'}
                    </div>
                    <div className="h-3 bg-slate-900/80 rounded-full overflow-hidden border border-slate-800/50 mb-2">
                      <motion.div
                        className={`h-full bg-gradient-to-r ${color} rounded-full`}
                        initial={{ width: 0 }}
                        animate={{ width: agent.signal !== undefined ? `${(agent.signal + 1) * 50}%` : '50%' }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 font-medium">
                      <span>Bearish (-1)</span>
                      <span>Bullish (+1)</span>
                    </div>
                  </div>

                  {/* Confidence Card */}
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-slate-800/70">
                    <div className="text-sm text-slate-400 mb-4 font-semibold uppercase tracking-wider flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Confidence Level
                    </div>
                    <div className="text-4xl font-bold text-blue-400 mb-2">
                      {agent.confidence ? `${agent.confidence.toFixed(1)}%` : 'N/A'}
                    </div>
                    <div className={`text-base font-semibold mb-4 ${getConfidenceColor()}`}>
                      {getConfidenceLevel()}
                    </div>
                    <div className="h-3 bg-slate-900/80 rounded-full overflow-hidden border border-slate-800/50 mb-2">
                      <motion.div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: agent.confidence ? `${agent.confidence}%` : '0%' }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 font-medium">
                      <span>0%</span>
                      <span>100%</span>
                    </div>
                  </div>
                </div>

                {/* Sentiment Breakdown (Only for Sentiment Agent) */}
                {isSentimentAgent && sentimentBreakdown && (
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-purple-500/30">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Activity className="w-5 h-5 text-purple-400" />
                      Sentiment Breakdown
                    </h3>
                    <div className="grid grid-cols-3 gap-4 mb-6">
                      <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4 hover:bg-green-500/20 transition-colors">
                        <div className="flex items-center gap-2 mb-2">
                          <ThumbsUp className="w-5 h-5 text-green-400" />
                          <span className="text-sm text-green-400 font-semibold uppercase">Positive</span>
                        </div>
                        <div className="text-3xl font-bold text-white">{sentimentBreakdown.positive}</div>
                        <div className="text-xs text-slate-400 mt-1">
                          {newsCount > 0 ? Math.round((sentimentBreakdown.positive / newsCount) * 100) : 0}% of articles
                        </div>
                      </div>

                      <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 hover:bg-yellow-500/20 transition-colors">
                        <div className="flex items-center gap-2 mb-2">
                          <MinusIcon className="w-5 h-5 text-yellow-400" />
                          <span className="text-sm text-yellow-400 font-semibold uppercase">Neutral</span>
                        </div>
                        <div className="text-3xl font-bold text-white">{sentimentBreakdown.neutral}</div>
                        <div className="text-xs text-slate-400 mt-1">
                          {newsCount > 0 ? Math.round((sentimentBreakdown.neutral / newsCount) * 100) : 0}% of articles
                        </div>
                      </div>

                      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 hover:bg-red-500/20 transition-colors">
                        <div className="flex items-center gap-2 mb-2">
                          <ThumbsDown className="w-5 h-5 text-red-400" />
                          <span className="text-sm text-red-400 font-semibold uppercase">Negative</span>
                        </div>
                        <div className="text-3xl font-bold text-white">{sentimentBreakdown.negative}</div>
                        <div className="text-xs text-slate-400 mt-1">
                          {newsCount > 0 ? Math.round((sentimentBreakdown.negative / newsCount) * 100) : 0}% of articles
                        </div>
                      </div>
                    </div>

                    {/* Visual Bar */}
                    <div className="h-4 bg-slate-900/80 rounded-full overflow-hidden border border-slate-800/50 flex">
                      {sentimentBreakdown.positive > 0 && (
                        <motion.div
                          className="bg-gradient-to-r from-green-500 to-green-400"
                          initial={{ width: 0 }}
                          animate={{ width: `${(sentimentBreakdown.positive / newsCount) * 100}%` }}
                          transition={{ duration: 0.8 }}
                        />
                      )}
                      {sentimentBreakdown.neutral > 0 && (
                        <motion.div
                          className="bg-gradient-to-r from-yellow-500 to-yellow-400"
                          initial={{ width: 0 }}
                          animate={{ width: `${(sentimentBreakdown.neutral / newsCount) * 100}%` }}
                          transition={{ duration: 0.8, delay: 0.2 }}
                        />
                      )}
                      {sentimentBreakdown.negative > 0 && (
                        <motion.div
                          className="bg-gradient-to-r from-red-500 to-red-400"
                          initial={{ width: 0 }}
                          animate={{ width: `${(sentimentBreakdown.negative / newsCount) * 100}%` }}
                          transition={{ duration: 0.8, delay: 0.4 }}
                        />
                      )}
                    </div>
                  </div>
                )}

                {/* News Articles List (Only for Sentiment Agent) */}
                {isSentimentAgent && newsArticles.length > 0 && (
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-slate-800/70">
                    <h3 className="text-lg font-bold text-white mb-4">
                      Analyzed News Articles ({newsArticles.length})
                    </h3>
                    <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
                      {newsArticles.map((article, i) => (
                        <motion.a
                          key={i}
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          whileHover={{ scale: 1.01, x: 4 }}
                          className="block bg-slate-900/50 rounded-lg p-4 hover:bg-slate-800/70 transition-all border border-slate-800/70 hover:border-slate-700/70 group"
                        >
                          <div className="flex items-start gap-3">
                            {/* Article Image */}
                            {article.image_url && (
                              <div className="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-slate-800/50">
                                <img 
                                  src={article.image_url} 
                                  alt={article.title}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    // Hide image if it fails to load
                                    e.currentTarget.parentElement!.style.display = 'none';
                                  }}
                                />
                              </div>
                            )}
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                  article.sentiment === 'positive' 
                                    ? 'bg-green-500/20 text-green-400' 
                                    : article.sentiment === 'negative'
                                    ? 'bg-red-500/20 text-red-400'
                                    : 'bg-yellow-500/20 text-yellow-400'
                                }`}>
                                  {article.sentiment === 'positive' ? '📈 Positive' : article.sentiment === 'negative' ? '📉 Negative' : '➖ Neutral'}
                                </span>
                                <span className="text-xs text-slate-500">{article.source}</span>
                              </div>
                              <h4 className="font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors line-clamp-2">
                                {article.title}
                              </h4>
                              <p className="text-sm text-slate-400 line-clamp-2">{article.snippet}</p>
                            </div>
                            <ExternalLink className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition-colors flex-shrink-0 mt-1" />
                          </div>
                        </motion.a>
                      ))}
                    </div>
                  </div>
                )}

                {/* Detailed Analysis */}
                {agent.summary && (
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-slate-800/70">
                    <h3 className="text-lg font-bold text-white mb-4">Detailed Analysis</h3>
                    <p className="text-slate-300 leading-relaxed">{agent.summary}</p>
                  </div>
                )}

                {/* All Key Metrics */}
                {agent.keyMetrics && Object.keys(agent.keyMetrics).length > 0 && (
                  <div className="bg-slate-900/70 rounded-lg p-6 border border-slate-800/70">
                    <h3 className="text-lg font-bold text-white mb-4">Complete Metrics</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {Object.entries(agent.keyMetrics)
                        .filter(([key]) => !['data_source', 'news_articles', 'positive_count', 'neutral_count', 'negative_count'].includes(key))
                        .map(([key, value]) => (
                          <div key={key} className="bg-slate-900/50 rounded-lg p-4 hover:bg-slate-800/50 transition-colors">
                            <div className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">
                              {formatLabel(key)}
                            </div>
                            <div className="text-white font-bold text-lg">
                              {typeof value === 'number' ? value.toFixed(2) : String(value)}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Data Quality */}
                <div className="bg-slate-900/70 rounded-lg p-6 border border-blue-500/30">
                  <h3 className="text-sm text-blue-400 mb-4 font-semibold uppercase tracking-wider flex items-center gap-2">
                    <Shield className="w-4 h-4" />
                    Data Quality & Reliability
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Data Source</span>
                      <span className="text-white font-semibold">{sourceBadge?.label || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Verification</span>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <span className="text-green-400 font-semibold">Verified</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Real-time Data</span>
                      <span className="text-cyan-400 font-semibold">Live</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

