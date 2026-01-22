'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { FaLightbulb } from 'react-icons/fa';
import { Loader2, Sparkles, AlertCircle } from 'lucide-react';

interface InvestorAdvisorCardProps {
  advice: string | null;
  isGenerating: boolean;
  error?: string | null;
  ticker: string;
}

export default function InvestorAdvisorCard({ advice, isGenerating, error, ticker }: InvestorAdvisorCardProps) {
  if (!isGenerating && !advice && !error) return null;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.5 }}
        className="glass rounded-3xl p-8 mt-6 shadow-glow"
      >
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg shadow-amber-500/30">
            <FaLightbulb className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              Investor Advisor
              <Sparkles className="w-6 h-6 text-amber-400" />
            </h2>
            <p className="text-slate-400 text-sm mt-1 font-medium">
              AI-Powered Investment Insights for {ticker}
            </p>
          </div>
        </div>

        {/* Content */}
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-12 h-12 text-amber-400 animate-spin mb-4" />
            <p className="text-slate-300 text-lg font-semibold">Generating personalized investor insights...</p>
            <p className="text-slate-500 text-sm mt-2">Analyzing all agent reports with Gemini AI</p>
            
            {/* Loading Animation */}
            <div className="flex gap-2 mt-6">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-3 h-3 rounded-full bg-gradient-to-r from-amber-500 to-orange-500"
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
          </div>
        ) : error ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-dark rounded-2xl p-6 border border-red-500/30"
          >
            <div className="flex items-start gap-4">
              <AlertCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-2">Unable to Generate Advice</h3>
                <p className="text-slate-300 leading-relaxed mb-3">{error}</p>
                <p className="text-slate-500 text-sm">
                  The analysis results are still available above. This may be due to API rate limits or temporary issues.
                </p>
              </div>
            </div>
          </motion.div>
        ) : advice ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            {/* AI Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/10 border border-amber-500/30 mb-4">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span className="text-sm font-semibold text-amber-400">Gemini AI Analysis</span>
            </div>

            {/* Advice Content */}
            <div className="glass-dark rounded-2xl p-6 border border-slate-800/50">
              <div className="prose prose-invert max-w-none">
                {advice.split('\n\n').map((block, idx) => {
                  const trimmed = block.trim();
                  
                  // Heading (starts with ##)
                  if (trimmed.startsWith('##')) {
                    return (
                      <h3 key={idx} className="text-xl font-bold text-white mt-6 mb-3 flex items-center gap-2">
                        <span className="text-amber-400">→</span>
                        {trimmed.replace('##', '').trim()}
                      </h3>
                    );
                  }
                  
                  // Check if it's a bullet list (multiple lines starting with - or •)
                  if (trimmed.includes('\n') && trimmed.split('\n').some(line => line.trim().startsWith('-') || line.trim().startsWith('•'))) {
                    return (
                      <div key={idx} className="space-y-3 my-4">
                        {trimmed.split('\n').filter(line => line.trim()).map((line, i) => {
                          const cleanLine = line.replace(/^[•-]\s*/, '').trim();
                          // Parse bold text **text**
                          const parts = cleanLine.split(/(\*\*.*?\*\*)/g);
                          return (
                            <div key={i} className="flex items-start gap-3">
                              <span className="text-amber-400 mt-1 flex-shrink-0">•</span>
                              <p className="text-slate-300 leading-relaxed">
                                {parts.map((part, j) => {
                                  if (part.startsWith('**') && part.endsWith('**')) {
                                    return <strong key={j} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
                                  }
                                  return <span key={j}>{part}</span>;
                                })}
                              </p>
                            </div>
                          );
                        })}
                      </div>
                    );
                  }
                  
                  // Check if it's a numbered list
                  if (/^\d+\./.test(trimmed)) {
                    const items = trimmed.split(/\n(?=\d+\.)/);
                    return (
                      <ol key={idx} className="space-y-2 my-4 ml-4">
                        {items.map((item, i) => {
                          const text = item.replace(/^\d+\.\s*/, '').trim();
                          return (
                            <li key={i} className="text-slate-300 leading-relaxed list-decimal ml-4">
                              {text}
                            </li>
                          );
                        })}
                      </ol>
                    );
                  }
                  
                  // Regular paragraph with bold parsing
                  const parts = trimmed.split(/(\*\*.*?\*\*)/g);
                  return (
                    <p key={idx} className="text-slate-300 leading-relaxed mb-4">
                      {parts.map((part, j) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                          return <strong key={j} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
                        }
                        return <span key={j}>{part}</span>;
                      })}
                    </p>
                  );
                })}
              </div>
            </div>

            {/* Footer Note */}
            <div className="mt-6 pt-4 border-t border-slate-800/50">
              <p className="text-xs text-slate-500 text-center">
                ⚠️ This advice is generated by AI and should not be considered as financial advice. 
                Always conduct your own research and consult with financial professionals.
              </p>
            </div>
          </motion.div>
        ) : null}
      </motion.div>
    </AnimatePresence>
  );
}

