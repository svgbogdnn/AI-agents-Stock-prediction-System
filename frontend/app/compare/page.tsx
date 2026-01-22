'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Plus, X, BarChart3, Activity } from 'lucide-react';
import { AnalysisResult } from '../types';

export default function ComparePage() {
  const [tickers, setTickers] = useState<string[]>(['']);
  const [results, setResults] = useState<(AnalysisResult | null)[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const addTicker = () => {
    if (tickers.length < 3) {
      setTickers([...tickers, '']);
    }
  };

  const removeTicker = (index: number) => {
    setTickers(tickers.filter((_, i) => i !== index));
    setResults(results.filter((_, i) => i !== index));
  };

  const updateTicker = (index: number, value: string) => {
    const newTickers = [...tickers];
    newTickers[index] = value.toUpperCase();
    setTickers(newTickers);
  };

  const analyzeAll = async () => {
    setIsAnalyzing(true);
    const newResults: (AnalysisResult | null)[] = [];

    for (const ticker of tickers) {
      if (!ticker) {
        newResults.push(null);
        continue;
      }

      try {
        const response = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ticker, horizon: 'next_quarter' }),
        });

        if (response.ok) {
          const data = await response.json();
          newResults.push(data);
        } else {
          newResults.push(null);
        }
      } catch (error) {
        newResults.push(null);
      }
    }

    setResults(newResults);
    setIsAnalyzing(false);
  };

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'BUY': return 'text-green-400 bg-green-500/20 border-green-500/50';
      case 'SELL': return 'text-red-400 bg-red-500/20 border-red-500/50';
      default: return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50';
    }
  };

  return (
    <main className="min-h-screen p-4 md:p-8 relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-4 mb-5">
            <BarChart3 className="w-10 h-10 text-blue-500" />
            <h1 className="text-5xl md:text-6xl font-bold gradient-text">
              Stock Comparison
            </h1>
          </div>
          <p className="text-slate-400 text-lg">
            Analyze up to 3 stocks side-by-side
          </p>
        </motion.div>

        {/* Ticker Inputs */}
        <div className="glass rounded-2xl p-6 mb-8">
          <div className="space-y-4">
            {tickers.map((ticker, index) => (
              <div key={index} className="flex gap-3">
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => updateTicker(index, e.target.value)}
                  placeholder={`Stock ${index + 1} (e.g., AAPL)`}
                  className="flex-1 bg-slate-900/70 border border-slate-700/50 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  maxLength={5}
                />
                {tickers.length > 1 && (
                  <button
                    onClick={() => removeTicker(index)}
                    className="p-3 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5 text-red-400" />
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="flex gap-3 mt-4">
            {tickers.length < 3 && (
              <button
                onClick={addTicker}
                className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-colors text-slate-300"
              >
                <Plus className="w-4 h-4" />
                Add Stock
              </button>
            )}
            <button
              onClick={analyzeAll}
              disabled={isAnalyzing || tickers.every(t => !t)}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold transition-all"
            >
              <Activity className="w-5 h-5" />
              {isAnalyzing ? 'Analyzing...' : 'Compare Stocks'}
            </button>
          </div>
        </div>

        {/* Comparison Results */}
        <AnimatePresence>
          {results.some(r => r !== null) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {results.map((result, index) => (
                result && (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="glass rounded-2xl p-6"
                  >
                    {/* Ticker Header */}
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-2xl font-bold text-white">{result.ticker}</h2>
                      <div className={`px-3 py-1 rounded-lg border font-semibold text-sm ${getRecommendationColor(result.recommendation)}`}>
                        {result.recommendation}
                      </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">Signal</span>
                        <span className={`font-bold ${result.weighted_signal > 0 ? 'text-green-400' : result.weighted_signal < 0 ? 'text-red-400' : 'text-yellow-400'}`}>
                          {result.weighted_signal > 0 ? '+' : ''}{result.weighted_signal.toFixed(2)}
                        </span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">Confidence</span>
                        <span className="font-bold text-blue-400">{result.confidence}%</span>
                      </div>

                      <div className="flex justify-between items-center">
                        <span className="text-slate-400 text-sm">Risk Level</span>
                        <span className={`font-bold ${result.risk_level === 'LOW' ? 'text-green-400' : result.risk_level === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`}>
                          {result.risk_level}
                        </span>
                      </div>

                      {/* Signal Bar */}
                      <div className="pt-3">
                        <div className="h-3 bg-slate-900 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${result.weighted_signal > 0 ? 'bg-gradient-to-r from-green-500 to-green-400' : 'bg-gradient-to-r from-red-500 to-red-400'}`}
                            style={{ width: `${Math.abs(result.weighted_signal) * 100}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              ))}
            </motion.div>
          )}
        </AnimatePresence>

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
    </main>
  );
}

