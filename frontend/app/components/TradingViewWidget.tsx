'use client';

import { useEffect, useRef, memo } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity } from 'lucide-react';

interface TradingViewWidgetProps {
  ticker: string;
  theme?: 'light' | 'dark';
}

function TradingViewWidget({ ticker, theme = 'dark' }: TradingViewWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !ticker) return;

    // Clear previous widget
    containerRef.current.innerHTML = '';

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: `NASDAQ:${ticker}`,
      interval: 'D',
      timezone: 'Etc/UTC',
      theme: theme,
      style: '1',
      locale: 'en',
      enable_publishing: false,
      backgroundColor: theme === 'dark' ? 'rgba(15, 23, 42, 0.8)' : 'rgba(255, 255, 255, 0.8)',
      gridColor: theme === 'dark' ? 'rgba(71, 85, 105, 0.2)' : 'rgba(0, 0, 0, 0.1)',
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: 'tradingview_widget',
      studies: [
        'STD;SMA',
        'STD;EMA',
        'STD;RSI',
        'STD;MACD',
      ],
      hide_side_toolbar: false,
      allow_symbol_change: false,
      details: true,
      hotlist: true,
      calendar: true,
      support_host: 'https://www.tradingview.com',
    });

    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [ticker, theme]);

  if (!ticker) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass rounded-3xl p-6 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            <h3 className="text-xl font-bold text-white">Live Chart Analysis</h3>
          </div>
          <p className="text-slate-400 text-sm">
            Real-time data for <span className="text-cyan-400 font-bold">{ticker}</span>
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span className="text-cyan-400 text-xs font-semibold">TradingView</span>
        </div>
      </div>

      {/* TradingView Chart Container */}
      <div className="relative rounded-2xl overflow-hidden bg-slate-950/50 border border-slate-800/50">
        <div 
          className="tradingview-widget-container" 
          style={{ height: '500px', width: '100%' }}
        >
          <div 
            id="tradingview_widget" 
            ref={containerRef}
            style={{ height: '100%', width: '100%' }}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-slate-800/50 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Live Market Data
          </span>
          <span>Updated continuously</span>
        </div>
        <a 
          href={`https://www.tradingview.com/symbols/NASDAQ-${ticker}/`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          View on TradingView →
        </a>
      </div>
    </motion.div>
  );
}

export default memo(TradingViewWidget);

