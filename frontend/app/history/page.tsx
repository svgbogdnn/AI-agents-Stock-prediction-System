'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, TrendingUp, TrendingDown, Calendar, Trash2, BarChart2, Award } from 'lucide-react';
import { AnalysisResult } from '../types';
import AnalysisDetailView from '../components/AnalysisDetailView';
import CapabilityChecklist from '../components/CapabilityChecklist';

interface HistoryEntry extends AnalysisResult {
  timestamp: string;
  id: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [filter, setFilter] = useState<'all' | 'BUY' | 'SELL' | 'HOLD'>('all');
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
  const [showChecklist, setShowChecklist] = useState(false);

  useEffect(() => {
    // Load history from localStorage
    const stored = localStorage.getItem('analysis_history');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setHistory(parsed.sort((a: HistoryEntry, b: HistoryEntry) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ));
      } catch (error) {
        console.error('Failed to load history:', error);
      }
    }
  }, []);

  const clearHistory = () => {
    if (confirm('Are you sure you want to clear all history?')) {
      localStorage.removeItem('analysis_history');
      setHistory([]);
    }
  };

  const deleteEntry = (id: string) => {
    const newHistory = history.filter(h => h.id !== id);
    setHistory(newHistory);
    localStorage.setItem('analysis_history', JSON.stringify(newHistory));
  };

  const filteredHistory = filter === 'all' 
    ? history 
    : history.filter(h => h.recommendation === filter);

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'BUY': return 'text-green-400 bg-green-500/20 border-green-500/50';
      case 'SELL': return 'text-red-400 bg-red-500/20 border-red-500/50';
      default: return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50';
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const stats = {
    total: history.length,
    buy: history.filter(h => h.recommendation === 'BUY').length,
    sell: history.filter(h => h.recommendation === 'SELL').length,
    hold: history.filter(h => h.recommendation === 'HOLD').length,
    avgConfidence: history.length > 0 
      ? (history.reduce((sum, h) => sum + h.confidence, 0) / history.length).toFixed(1)
      : 0,
  };

  return (
    <main className="min-h-screen p-4 md:p-8 relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <div className="flex items-center gap-4 mb-3">
                <Clock className="w-10 h-10 text-purple-500" />
                <h1 className="text-5xl md:text-6xl font-bold gradient-text">
                  Analysis History
                </h1>
              </div>
              <p className="text-slate-400 text-lg">
                Track your past predictions and accuracy. Click on a ticker to view detailed analysis.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowChecklist(!showChecklist)}
                className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 rounded-lg transition-colors text-yellow-400"
              >
                <Award className="w-4 h-4" />
                {showChecklist ? 'Hide' : 'Show'} Checklist
              </button>
              {history.length > 0 && (
                <button
                  onClick={clearHistory}
                  className="flex items-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors text-red-400"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </button>
              )}
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="glass rounded-xl p-4">
              <div className="text-slate-400 text-sm mb-1">Total</div>
              <div className="text-2xl font-bold text-white">{stats.total}</div>
            </div>
            <div className="glass rounded-xl p-4 border-green-500/30">
              <div className="text-slate-400 text-sm mb-1">Buy Signals</div>
              <div className="text-2xl font-bold text-green-400">{stats.buy}</div>
            </div>
            <div className="glass rounded-xl p-4 border-red-500/30">
              <div className="text-slate-400 text-sm mb-1">Sell Signals</div>
              <div className="text-2xl font-bold text-red-400">{stats.sell}</div>
            </div>
            <div className="glass rounded-xl p-4 border-yellow-500/30">
              <div className="text-slate-400 text-sm mb-1">Hold Signals</div>
              <div className="text-2xl font-bold text-yellow-400">{stats.hold}</div>
            </div>
            <div className="glass rounded-xl p-4 border-blue-500/30">
              <div className="text-slate-400 text-sm mb-1">Avg Confidence</div>
              <div className="text-2xl font-bold text-blue-400">{stats.avgConfidence}%</div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-2">
            {(['all', 'BUY', 'SELL', 'HOLD'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  filter === f
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                    : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50'
                }`}
              >
                {f === 'all' ? 'All' : f}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Capability Checklist */}
        {showChecklist && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <CapabilityChecklist />
          </motion.div>
        )}

        {/* History List */}
        {filteredHistory.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass rounded-2xl p-12 text-center"
          >
            <BarChart2 className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-400 mb-2">
              No analysis history yet
            </h3>
            <p className="text-slate-500 mb-6">
              Start analyzing stocks to build your history
            </p>
            <a
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 rounded-lg font-semibold transition-all"
            >
              Analyze Stocks
            </a>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {filteredHistory.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass rounded-xl p-6 hover:bg-slate-800/40 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <button
                        onClick={() => setSelectedEntry(entry)}
                        className="text-2xl font-bold text-white hover:text-blue-400 transition-colors cursor-pointer"
                      >
                        {entry.ticker}
                      </button>
                      <div className={`px-3 py-1 rounded-lg border font-semibold text-sm ${getRecommendationColor(entry.recommendation)}`}>
                        {entry.recommendation}
                      </div>
                      <div className="flex items-center gap-1 text-slate-500 text-sm">
                        <Calendar className="w-4 h-4" />
                        {formatDate(entry.timestamp)}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Signal</div>
                        <div className={`font-bold flex items-center gap-1 ${entry.weighted_signal > 0 ? 'text-green-400' : entry.weighted_signal < 0 ? 'text-red-400' : 'text-yellow-400'}`}>
                          {entry.weighted_signal > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                          {entry.weighted_signal > 0 ? '+' : ''}{entry.weighted_signal.toFixed(2)}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Confidence</div>
                        <div className="font-bold text-blue-400">{entry.confidence}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Risk</div>
                        <div className={`font-bold ${entry.risk_level === 'LOW' ? 'text-green-400' : entry.risk_level === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`}>
                          {entry.risk_level}
                        </div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-500 mb-1">Time</div>
                        <div className="font-bold text-slate-300">{entry.elapsed_seconds}s</div>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => deleteEntry(entry.id)}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-slate-500 hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center mt-12"
        >
          <a
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-colors text-slate-300"
          >
            ← Back to Dashboard
          </a>
        </motion.div>
      </div>

      {/* Detail View Modal */}
      {selectedEntry && (
        <AnalysisDetailView
          entry={selectedEntry}
          onClose={() => setSelectedEntry(null)}
        />
      )}
    </main>
  );
}

