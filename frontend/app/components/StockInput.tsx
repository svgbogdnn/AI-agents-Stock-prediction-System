'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, TrendingUp } from 'lucide-react';

interface StockInputProps {
  onAnalyze: (ticker: string) => void;
  isLoading: boolean;
}

export default function StockInput({ onAnalyze, isLoading }: StockInputProps) {
  const [input, setInput] = useState('');
  const [focused, setFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onAnalyze(input.trim().toUpperCase());
    }
  };

  const popularStocks = ['GOOGL', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto mb-12"
    >
      <div className="glass rounded-3xl p-8 hover:shadow-glow transition-all duration-500">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Input Field */}
          <div className="relative">
            <div className={`
              relative rounded-2xl transition-all duration-300
              ${focused ? 'ring-2 ring-purple-500/50' : ''}
            `}>
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className={`w-6 h-6 transition-colors ${focused ? 'text-purple-400' : 'text-gray-400'}`} />
              </div>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value.toUpperCase())}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                placeholder="Enter stock ticker (e.g., GOOGL)"
                className="
                  w-full pl-14 pr-4 py-5
                  bg-slate-950/80 border border-slate-700/50
                  rounded-2xl text-white placeholder-slate-500
                  focus:outline-none focus:border-blue-500/50 focus:bg-slate-900/90
                  focus:shadow-glow-sm
                  transition-all duration-300 text-lg font-medium
                  tracking-wide
                "
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Submit Button */}
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            type="submit"
            disabled={!input.trim() || isLoading}
            className="
              relative w-full py-5 px-6 rounded-2xl overflow-hidden
              bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500
              hover:from-blue-500 hover:via-blue-400 hover:to-cyan-400
              disabled:from-slate-800 disabled:to-slate-700
              disabled:cursor-not-allowed
              text-white font-bold text-lg
              shadow-lg shadow-blue-500/30
              hover:shadow-blue-500/50
              transition-all duration-300
              flex items-center justify-center gap-3
              group
            "
          >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent group-hover:translate-x-full transition-transform duration-1000" />
            <TrendingUp className="w-5 h-5 relative z-10" />
            <span className="relative z-10">Analyze Stock with AI Agents</span>
          </motion.button>

          {/* Popular Stocks */}
          <div className="space-y-3">
            <p className="text-sm text-slate-500 text-center font-medium">Or try popular stocks:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {popularStocks.map((stock) => (
                <motion.button
                  key={stock}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  type="button"
                  onClick={() => setInput(stock)}
                  className="
                    px-5 py-2.5 rounded-xl
                    bg-slate-800/50 hover:bg-slate-700/70
                    border border-slate-700/50 hover:border-blue-500/50
                    text-sm font-semibold text-slate-300 hover:text-white
                    transition-all duration-300
                    hover:shadow-glow-sm
                  "
                  disabled={isLoading}
                >
                  {stock}
                </motion.button>
              ))}
            </div>
          </div>
        </form>

        {/* Features */}
        <div className="mt-8 pt-6 border-t border-slate-800/50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center group">
              <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-300">🚀</div>
              <div className="text-xs font-semibold text-slate-400">6 Specialist Agents</div>
            </div>
            <div className="text-center group">
              <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-300">⚡</div>
              <div className="text-xs font-semibold text-slate-400">Real-time Analysis</div>
            </div>
            <div className="text-center group">
              <div className="text-3xl mb-2 group-hover:scale-110 transition-transform duration-300">🎯</div>
              <div className="text-xs font-semibold text-slate-400">A2A Protocol v0.3.0</div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

