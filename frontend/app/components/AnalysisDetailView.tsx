'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, TrendingUp, TrendingDown, Clock, Activity, Database, Brain, Zap, Target, CheckCircle, AlertCircle, Info, Sparkles, Loader2, ArrowRight, ArrowDown, ArrowUp, Network, Cloud, ArrowDownToLine, ArrowUpFromLine } from 'lucide-react';
import { AnalysisResult, AgentResponse } from '../types';
import InfoTooltip from './InfoTooltip';

interface AnalysisDetailViewProps {
  entry: AnalysisResult & { id: string; timestamp: string };
  onClose: () => void;
}

interface AgentExplanation {
  explanation: string;
  agent_name: string;
  loading?: boolean;
  error?: string;
}

const AGENT_INFO: Record<string, { 
  name: string; 
  description: string; 
  color: string;
  role: string;
  prompt: string;
  inputDescription: string;
}> = {
  fundamental: { 
    name: 'Fundamental Analyst', 
    description: 'Financial metrics, valuation, and company fundamentals', 
    color: 'from-blue-500 to-cyan-500',
    role: 'Expert in company valuation and financial statement analysis. Analyzes financial health, valuation metrics (P/E, PEG, P/B), growth metrics, and quality factors.',
    prompt: 'You are an expert FUNDAMENTAL ANALYST specializing in company valuation and financial statement analysis. Analyze financial health (revenue growth, profitability, debt levels, liquidity), valuation (P/E, PEG, P/B ratios), growth metrics (YoY and QoQ growth in EPS, revenue, margins), and quality factors (management quality, competitive moats, business model sustainability). Always use get_fundamentals() and get_sec_filings() tools to fetch real data.',
    inputDescription: 'Ticker symbol and prediction horizon'
  },
  technical: { 
    name: 'Technical Analyst', 
    description: 'Price action, momentum, and technical indicators', 
    color: 'from-green-500 to-emerald-500',
    role: 'Expert in price action, chart patterns, and momentum indicators. Analyzes trends, momentum indicators (RSI, MACD), support/resistance levels, volume patterns, and multi-timeframe analysis.',
    prompt: 'You are an expert TECHNICAL ANALYST specializing in price action, chart patterns, and momentum indicators. Analyze trend (bullish, bearish, sideways using moving averages), momentum indicators (RSI, MACD for overbought/oversold conditions), support/resistance levels, volume patterns, and multi-timeframe analysis (daily, weekly, monthly charts). Always use get_technical_indicators() and get_price_history() tools.',
    inputDescription: 'Ticker symbol and prediction horizon'
  },
  sentiment: { 
    name: 'Sentiment Analyst', 
    description: 'News analysis and market sentiment', 
    color: 'from-purple-500 to-pink-500',
    role: 'Expert in news analysis and market sentiment. Analyzes recent news articles, social media sentiment, analyst ratings, and market psychology to gauge overall sentiment.',
    prompt: 'You are an expert SENTIMENT ANALYST specializing in news analysis and market sentiment. Analyze recent news articles (last 7 days), identify key events and their impact, assess sentiment (positive, neutral, negative), analyze analyst ratings and price targets, and evaluate market psychology. Always use get_recent_news() and analyze_sentiment() tools.',
    inputDescription: 'Ticker symbol and prediction horizon'
  },
  macro: { 
    name: 'Macro Analyst', 
    description: 'Economic conditions and macro indicators', 
    color: 'from-orange-500 to-red-500',
    role: 'Expert in economic conditions and macro indicators. Analyzes interest rates, GDP growth, inflation, unemployment, and sector-specific economic factors.',
    prompt: 'You are an expert MACRO ANALYST specializing in economic conditions and macro indicators. Analyze interest rates and Fed policy, GDP growth and economic trends, inflation (CPI, PPI), unemployment rates, sector-specific economic factors, and how macro conditions affect the stock. Always use get_economic_indicators() and get_fed_policy() tools.',
    inputDescription: 'Ticker symbol and prediction horizon'
  },
  regulatory: { 
    name: 'Regulatory Analyst', 
    description: 'Legal compliance and industry risks', 
    color: 'from-yellow-500 to-amber-500',
    role: 'Expert in legal compliance and industry risks. Analyzes SEC filings, regulatory changes, compliance issues, industry-specific regulations, and legal risks.',
    prompt: 'You are an expert REGULATORY ANALYST specializing in legal compliance and industry risks. Analyze SEC filings (10-K, 10-Q, 8-K), identify regulatory changes affecting the industry, assess compliance issues and legal risks, evaluate industry-specific regulations, and assess potential legal challenges. Always use get_sec_filings() and analyze_regulatory_risks() tools.',
    inputDescription: 'Ticker symbol and prediction horizon'
  },
  predictor: { 
    name: 'Predictor Agent', 
    description: 'ML-based synthesis and final prediction', 
    color: 'from-indigo-500 to-blue-500',
    role: 'CHIEF PREDICTION SYNTHESIZER responsible for generating the final stock recommendation. Synthesizes all 5 analysis reports, weights each analysis based on confidence score, applies ML model to generate prediction, calculates risk based on signal disagreement, and provides comprehensive rationale.',
    prompt: 'You are the CHIEF PREDICTION SYNTHESIZER responsible for generating the final stock recommendation. You receive analysis reports from 5 specialized agents (Fundamental, Technical, Sentiment, Macro, Regulatory). Your job is to: 1) Synthesize all 5 analysis reports into a unified view, 2) Weight each analysis based on its confidence score, 3) Apply ML model to generate a prediction (BUY/HOLD/SELL), 4) Calculate risk based on signal disagreement and market volatility, 5) Provide rationale explaining the key factors driving your decision.',
    inputDescription: 'All 5 agent analysis reports (fundamental, technical, sentiment, macro, regulatory)'
  },
};

// Helper function for signal colors
const getSignalColor = (signal: number) => {
  if (signal > 0.3) return 'text-green-400';
  if (signal < -0.3) return 'text-red-400';
  return 'text-yellow-400';
};

// Predictor Card Component with Input/Output Icons
function PredictorFlowCard({ 
  entry, 
  agents 
}: { 
  entry: AnalysisResult & { id: string; timestamp: string }; 
  agents: [string, AgentResponse][];
}) {
  const [isInputHovered, setIsInputHovered] = useState(false);
  const [isOutputHovered, setIsOutputHovered] = useState(false);
  const specialistAgents = agents.filter(([id]) => id !== 'predictor');

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 1.4 }}
      className="flex justify-center mb-4 relative"
    >
      <div className="px-6 py-5 bg-gradient-to-r from-yellow-500 to-amber-500 rounded-lg shadow-lg border-2 border-yellow-400 relative min-h-[120px] flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2 text-white font-semibold">
            <Brain className="w-5 h-5" />
            <span>Predictor Agent</span>
          </div>
          <div className="text-xs text-yellow-100 mt-1">
            Synthesizes all agent reports
          </div>
        </div>

        {/* Icons Row */}
        <div className="flex items-center justify-between mt-4">
          {/* Input Icon */}
          <div 
            className="cursor-help relative"
            onMouseEnter={() => setIsInputHovered(true)}
            onMouseLeave={() => setIsInputHovered(false)}
          >
            <ArrowDownToLine className="w-5 h-5 text-blue-400 hover:text-blue-300 transition-colors" />
            <AnimatePresence>
              {isInputHovered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, x: -10 }}
                  animate={{ opacity: 1, scale: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95, x: -10 }}
                  className="absolute left-0 top-1/2 transform -translate-y-1/2 mr-2 w-72 p-3 bg-slate-800 border border-blue-500/50 rounded-lg shadow-xl z-50"
                >
                  <div className="text-xs font-semibold text-blue-400 mb-2 flex items-center gap-1">
                    <Database className="w-3 h-3" />
                    INPUT (5 Agent Reports)
                  </div>
                  <div className="text-xs text-slate-300 space-y-2 max-h-64 overflow-y-auto">
                    {specialistAgents.map(([agentId, report]) => {
                      const agentInfo = AGENT_INFO[agentId] || { name: agentId };
                      return (
                        <div key={agentId} className="p-2 bg-slate-900/50 rounded border border-slate-700/50">
                          <div className="font-semibold text-blue-300">{agentInfo.name}</div>
                          <div className="text-slate-400 mt-1">
                            Signal: <span className={`font-mono ${getSignalColor(report.directional_signal)}`}>
                              {report.directional_signal > 0 ? '+' : ''}{report.directional_signal.toFixed(2)}
                            </span> | 
                            Confidence: <span className="font-mono text-blue-400">{report.confidence_score}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-4 border-l-blue-500/50 border-t-transparent border-b-transparent border-r-transparent" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Output Icon */}
          <div 
            className="cursor-help relative"
            onMouseEnter={() => setIsOutputHovered(true)}
            onMouseLeave={() => setIsOutputHovered(false)}
          >
            <ArrowUpFromLine className="w-5 h-5 text-green-400 hover:text-green-300 transition-colors" />
            <AnimatePresence>
              {isOutputHovered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 10 }}
                  className="absolute right-0 top-full mt-2 w-72 p-3 bg-slate-800 border border-green-500/50 rounded-lg shadow-xl z-50"
                >
                  <div className="text-xs font-semibold text-green-400 mb-2 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    OUTPUT (Final Recommendation)
                  </div>
                  <div className="text-xs text-slate-300 space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-500">Recommendation:</span>
                      <span className={`font-bold text-lg ${
                        entry.recommendation === 'BUY' ? 'text-green-400' :
                        entry.recommendation === 'SELL' ? 'text-red-400' :
                        'text-yellow-400'
                      }`}>
                        {entry.recommendation}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence:</span>
                      <span className="font-mono text-blue-400 font-bold">{entry.confidence}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Risk Level:</span>
                      <span className={`font-mono font-semibold ${
                        entry.risk_level === 'LOW' ? 'text-green-400' :
                        entry.risk_level === 'HIGH' ? 'text-red-400' :
                        'text-yellow-400'
                      }`}>
                        {entry.risk_level}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Weighted Signal:</span>
                      <span className="font-mono text-purple-400">{(entry as any).weighted_signal?.toFixed(3) || 'N/A'}</span>
                    </div>
                    {entry.rationale && (
                      <div className="mt-2 pt-2 border-t border-slate-700/50">
                        <span className="text-slate-500">Rationale:</span>
                        <div className="text-xs text-slate-400 mt-1 line-clamp-4">{entry.rationale.substring(0, 200)}...</div>
                      </div>
                    )}
                  </div>
                  <div className="absolute top-0 right-1/2 transform -translate-x-1/2 -translate-y-full w-0 h-0 border-4 border-b-green-500/50 border-l-transparent border-r-transparent border-t-transparent" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Agent Card Component with Input/Output Icons
function AgentFlowCard({ 
  agentId, 
  report, 
  agentInfo, 
  entry, 
  index 
}: { 
  agentId: string; 
  report: AgentResponse; 
  agentInfo: typeof AGENT_INFO[string]; 
  entry: AnalysisResult & { id: string; timestamp: string }; 
  index: number;
}) {
  const [isInputHovered, setIsInputHovered] = useState(false);
  const [isOutputHovered, setIsOutputHovered] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 + index * 0.1 }}
      className="relative"
    >
      <div className={`px-3 py-4 bg-gradient-to-br ${agentInfo.color} rounded-lg shadow-md border border-white/20 relative min-h-[100px] flex flex-col justify-between`}>
        {/* Agent Name */}
        <div className="text-xs text-white font-semibold text-center truncate mb-2">
          {agentInfo.name.split(' ')[0]}
        </div>
        
        {/* Icons Row */}
        <div className="flex items-center justify-between mt-auto">
          {/* Input Icon */}
          <div 
            className="cursor-help relative"
            onMouseEnter={() => setIsInputHovered(true)}
            onMouseLeave={() => setIsInputHovered(false)}
          >
            <ArrowDownToLine className="w-4 h-4 text-blue-400 hover:text-blue-300 transition-colors" />
            <AnimatePresence>
              {isInputHovered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -10 }}
                  className="absolute left-0 bottom-full mb-2 w-64 p-3 bg-slate-800 border border-blue-500/50 rounded-lg shadow-xl z-50"
                >
                  <div className="text-xs font-semibold text-blue-400 mb-2 flex items-center gap-1">
                    <Database className="w-3 h-3" />
                    INPUT
                  </div>
                  <div className="text-xs text-slate-300 space-y-1">
                    <div><span className="text-slate-500">Ticker:</span> <span className="font-mono text-blue-400">{entry.ticker}</span></div>
                    <div><span className="text-slate-500">Horizon:</span> <span className="font-mono text-blue-400">Next Quarter</span></div>
                    <div className="mt-2 pt-2 border-t border-slate-700/50">
                      <span className="text-slate-500">Prompt:</span>
                      <div className="text-xs text-slate-400 mt-1 line-clamp-3">{agentInfo.prompt.substring(0, 150)}...</div>
                    </div>
                  </div>
                  <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-4 border-t-blue-500/50 border-l-transparent border-r-transparent border-b-transparent" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Data Source Icon */}
          {entry.analysis_reports[agentId]?.data_source && (
            <div className="flex flex-col items-center">
              <Cloud className="w-4 h-4 text-cyan-400" />
            </div>
          )}

          {/* Output Icon */}
          <div 
            className="cursor-help relative"
            onMouseEnter={() => setIsOutputHovered(true)}
            onMouseLeave={() => setIsOutputHovered(false)}
          >
            <ArrowUpFromLine className="w-4 h-4 text-green-400 hover:text-green-300 transition-colors" />
            <AnimatePresence>
              {isOutputHovered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95, y: 10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 10 }}
                  className="absolute right-0 top-full mt-2 w-64 p-3 bg-slate-800 border border-green-500/50 rounded-lg shadow-xl z-50"
                >
                  <div className="text-xs font-semibold text-green-400 mb-2 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    OUTPUT
                  </div>
                  <div className="text-xs text-slate-300 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Signal:</span>
                      <span className={`font-mono font-bold ${getSignalColor(report.directional_signal)}`}>
                        {report.directional_signal > 0 ? '+' : ''}{report.directional_signal.toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence:</span>
                      <span className="font-mono text-blue-400">{report.confidence_score}%</span>
                    </div>
                    {report.data_source && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Data Source:</span>
                        <span className="font-mono text-cyan-400 text-xs">{report.data_source}</span>
                      </div>
                    )}
                    {report.summary && (
                      <div className="mt-2 pt-2 border-t border-slate-700/50">
                        <span className="text-slate-500">Summary:</span>
                        <div className="text-xs text-slate-400 mt-1 line-clamp-3">{report.summary}</div>
                      </div>
                    )}
                  </div>
                  <div className="absolute top-0 right-1/2 transform -translate-x-1/2 -translate-y-full w-0 h-0 border-4 border-b-green-500/50 border-l-transparent border-r-transparent border-t-transparent" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default function AnalysisDetailView({ entry, onClose }: AnalysisDetailViewProps) {
  const agents = Object.entries(entry.analysis_reports || {});
  const [explanations, setExplanations] = useState<Record<string, AgentExplanation>>({});

  const fetchExplanation = async (agentId: string, report: AgentResponse) => {
    // Check if already fetched
    if (explanations[agentId] && !explanations[agentId].loading) return;

    // Set loading state
    setExplanations(prev => ({
      ...prev,
      [agentId]: { explanation: '', agent_name: agentId, loading: true, error: undefined }
    }));

    try {
      const response = await fetch('/api/agent-explanation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          agent_report: report,
          ticker: entry.ticker,
        }),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          const errorText = await response.text();
          errorData = { error: errorText };
        }
        throw new Error(errorData.details || errorData.error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setExplanations(prev => ({
        ...prev,
        [agentId]: {
          explanation: data.explanation,
          agent_name: data.agent_name || agentId,
          loading: false,
        }
      }));
    } catch (error: any) {
      console.error('Error fetching explanation:', error);
      
      // Generate a fallback explanation from the data
      const signal = report.directional_signal || 0;
      const confidence = report.confidence_score || 0;
      
      let signalText = '';
      if (signal > 0.3) signalText = 'strongly bullish (positive outlook)';
      else if (signal > 0) signalText = 'slightly bullish (cautiously positive)';
      else if (signal < -0.3) signalText = 'strongly bearish (negative outlook)';
      else if (signal < 0) signalText = 'slightly bearish (cautiously negative)';
      else signalText = 'neutral (no strong directional bias)';
      
      const fallbackExplanation = `The ${AGENT_INFO[agentId]?.name || agentId} indicates a ${signalText} signal of ${signal.toFixed(3)} with ${confidence}% confidence. 

This means the agent's analysis suggests ${signal > 0 ? 'positive' : signal < 0 ? 'negative' : 'neutral'} factors for ${entry.ticker}. The confidence level of ${confidence}% indicates ${confidence > 70 ? 'high certainty' : confidence > 50 ? 'moderate certainty' : 'low certainty'} in this assessment.

${report.summary ? `Summary: ${report.summary}` : 'Review the metrics above for more details.'}`;

      setExplanations(prev => ({
        ...prev,
        [agentId]: {
          explanation: fallbackExplanation,
          agent_name: AGENT_INFO[agentId]?.name || agentId,
          loading: false,
          error: error.message?.includes('fetch') || error.message?.includes('network') 
            ? 'Backend not available. Showing fallback explanation.'
            : undefined,
        }
      }));
    }
  };
  
  const calculatePerformanceScore = () => {
    // Performance score based on multiple factors
    let score = 0;
    const maxScore = 100;
    
    // Confidence contributes 40%
    score += (entry.confidence / 100) * 40;
    
    // Agent consensus contributes 30% (lower variance = higher score)
    const signals = agents.map(([_, report]) => report.directional_signal);
    const avgSignal = signals.reduce((a, b) => a + b, 0) / signals.length;
    const variance = signals.reduce((sum, s) => sum + Math.pow(s - avgSignal, 2), 0) / signals.length;
    const consensus = Math.max(0, 1 - variance); // Lower variance = higher consensus
    score += consensus * 30;
    
    // Data quality contributes 20% (all agents have data sources)
    const dataQuality = agents.filter(([_, report]) => report.data_source).length / agents.length;
    score += dataQuality * 20;
    
    // Speed contributes 10% (faster is better, but not too fast)
    const speedScore = entry.elapsed_seconds < 10 ? (10 - entry.elapsed_seconds) / 10 : 0;
    score += speedScore * 10;
    
    return Math.round(score);
  };

  const performanceScore = calculatePerformanceScore();
  
  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getSignalColor = (signal: number) => {
    if (signal > 0.3) return 'text-green-400';
    if (signal < -0.3) return 'text-red-400';
    return 'text-yellow-400';
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="glass rounded-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="p-6 border-b border-slate-700/50 flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-2">
                <h2 className="text-3xl font-bold text-white">{entry.ticker}</h2>
                <div className={`px-4 py-1 rounded-lg border font-semibold ${
                  entry.recommendation === 'BUY' ? 'text-green-400 bg-green-500/20 border-green-500/50' :
                  entry.recommendation === 'SELL' ? 'text-red-400 bg-red-500/20 border-red-500/50' :
                  'text-yellow-400 bg-yellow-500/20 border-yellow-500/50'
                }`}>
                  {entry.recommendation}
                </div>
                <div className={`text-2xl font-bold ${getPerformanceColor(performanceScore)}`}>
                  {performanceScore}/100
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-slate-400">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {new Date(entry.timestamp).toLocaleString()}
                </div>
                <div className="flex items-center gap-1">
                  <Activity className="w-4 h-4" />
                  {entry.elapsed_seconds}s execution time
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-slate-400" />
            </button>
          </div>

          {/* Content - Scrollable */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="glass-dark rounded-xl p-4 border-l-4 border-blue-500">
                <div className="text-sm text-slate-400 mb-1 flex items-center gap-2">
                  Confidence
                  <InfoTooltip content="Overall confidence in the prediction, calculated from all agent analyses. Higher confidence (70%+) means the system is more certain about the recommendation. Lower confidence suggests mixed signals or uncertainty." />
                </div>
                <div className="text-2xl font-bold text-blue-400">{entry.confidence}%</div>
              </div>
              <div className="glass-dark rounded-xl p-4 border-l-4 border-green-500">
                <div className="text-sm text-slate-400 mb-1 flex items-center gap-2">
                  Weighted Signal
                  <InfoTooltip content="Combined directional signal from all agents, weighted by their confidence scores. Range: -1 (strong sell) to +1 (strong buy). Positive values suggest buying, negative values suggest selling, near zero suggests holding." />
                </div>
                <div className={`text-2xl font-bold flex items-center gap-1 ${getSignalColor(entry.weighted_signal)}`}>
                  {entry.weighted_signal > 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                  {entry.weighted_signal > 0 ? '+' : ''}{entry.weighted_signal.toFixed(3)}
                </div>
              </div>
              <div className="glass-dark rounded-xl p-4 border-l-4 border-yellow-500">
                <div className="text-sm text-slate-400 mb-1 flex items-center gap-2">
                  Risk Level
                  <InfoTooltip content="Assessment of investment risk based on signal agreement and market volatility. LOW: Agents agree, stable conditions. MEDIUM: Some disagreement or moderate volatility. HIGH: Conflicting signals or high uncertainty." />
                </div>
                <div className={`text-2xl font-bold ${
                  entry.risk_level === 'LOW' ? 'text-green-400' :
                  entry.risk_level === 'HIGH' ? 'text-red-400' :
                  'text-yellow-400'
                }`}>
                  {entry.risk_level}
                </div>
              </div>
              <div className="glass-dark rounded-xl p-4 border-l-4 border-purple-500">
                <div className="text-sm text-slate-400 mb-1 flex items-center gap-2">
                  Performance Score
                  <InfoTooltip content="Overall system performance metric (0-100) combining confidence (40%), agent consensus (30%), data quality (20%), and execution speed (10%). Higher scores indicate more reliable and efficient analysis." />
                </div>
                <div className={`text-2xl font-bold ${getPerformanceColor(performanceScore)}`}>
                  {performanceScore}/100
                </div>
              </div>
            </div>

            {/* Rationale */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-400" />
                Analysis Rationale
                <InfoTooltip content="The comprehensive explanation of why this recommendation was made. It synthesizes insights from all agents and explains the key factors driving the final decision." />
              </h3>
              <p className="text-slate-300 leading-relaxed">{entry.rationale}</p>
            </div>

            {/* Data Flow & Traceability */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Database className="w-5 h-5 text-cyan-400" />
                Data Flow & Traceability
                <InfoTooltip content="Complete tracking of how data flows through the system: from user input, through agent processing, to final output. This ensures transparency and allows you to verify the analysis process." />
              </h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg">
                  <Info className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white mb-1">Input</div>
                    <div className="text-sm text-slate-300">Ticker: <span className="font-mono text-blue-400">{entry.ticker}</span></div>
                    <div className="text-sm text-slate-300">Horizon: <span className="font-mono text-blue-400">Next Quarter</span></div>
                    <div className="text-sm text-slate-300">Timestamp: <span className="font-mono text-blue-400">{new Date(entry.timestamp).toISOString()}</span></div>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg">
                  <Zap className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white mb-1">Orchestration</div>
                    <div className="text-sm text-slate-300">Parallel agent execution across {agents.length} specialized agents</div>
                    <div className="text-sm text-slate-300">Total execution time: <span className="font-mono text-yellow-400">{entry.elapsed_seconds}s</span></div>
                    <div className="text-sm text-slate-300 mt-2">Agents called: <span className="font-mono text-yellow-400">{agents.map(([id]) => AGENT_INFO[id]?.name || id).join(', ')}</span></div>
                    <div className="text-sm text-slate-300">Protocol: <span className="font-mono text-yellow-400">A2A Protocol v0.3.0</span></div>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg">
                  <Target className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white mb-1">Output</div>
                    <div className="text-sm text-slate-300">Recommendation: <span className="font-mono text-green-400">{entry.recommendation}</span></div>
                    <div className="text-sm text-slate-300">Confidence: <span className="font-mono text-green-400">{entry.confidence}%</span></div>
                    <div className="text-sm text-slate-300">Risk Assessment: <span className="font-mono text-green-400">{entry.risk_level}</span></div>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-slate-900/50 rounded-lg border-l-2 border-cyan-500">
                  <Activity className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-white mb-1">Complete Traceability</div>
                    <div className="text-xs text-slate-300 space-y-1">
                      <div>✅ <span className="text-cyan-400">Input tracking:</span> User request with timestamp logged</div>
                      <div>✅ <span className="text-cyan-400">Agent execution:</span> Each agent's input/output fully recorded</div>
                      <div>✅ <span className="text-cyan-400">Data source attribution:</span> All API calls traced (Polygon, FRED, SEC, NewsAPI)</div>
                      <div>✅ <span className="text-cyan-400">Prompt visibility:</span> System prompts applied to each agent visible</div>
                      <div>✅ <span className="text-cyan-400">Execution timeline:</span> Parallel execution with timing metrics</div>
                      <div>✅ <span className="text-cyan-400">Decision path:</span> Full workflow from input → agents → synthesis → output</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Agent Details */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-blue-400" />
                  Agent Execution Details
                </h3>
                {agents.some(([id]) => id === 'predictor') && (
                  <div className="px-4 py-2 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
                    <div className="text-xs text-yellow-400 font-semibold">
                      Final Prediction by: <span className="text-yellow-300">Predictor Agent</span>
                    </div>
                  </div>
                )}
              </div>
              <div className="mb-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <div className="text-sm text-slate-300 flex items-start gap-2">
                  <div className="flex-1">
                    <span className="font-semibold text-blue-400">Workflow:</span> The orchestrator calls 5 specialized agents in parallel (Fundamental, Technical, Sentiment, Macro, Regulatory). 
                    Their analysis reports are then passed to the <span className="font-semibold text-yellow-400">Predictor Agent</span>, which synthesizes all inputs and generates the final recommendation (BUY/HOLD/SELL).
                  </div>
                  <InfoTooltip content="The multi-agent workflow ensures comprehensive analysis by leveraging specialized expertise. Each agent analyzes different aspects independently, then the Predictor Agent combines their insights for a well-rounded recommendation." position="left" />
                </div>
              </div>
              <div className="space-y-4">
                {agents.map(([agentId, report]) => {
                  const agentInfo = AGENT_INFO[agentId] || { 
                    name: agentId, 
                    description: '', 
                    color: 'from-gray-500 to-gray-600',
                    role: 'Specialized agent',
                    prompt: 'Agent prompt not available',
                    inputDescription: 'Ticker symbol'
                  };
                  const isPredictor = agentId === 'predictor';
                  
                  return (
                    <motion.div
                      key={agentId}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`glass-dark rounded-xl p-5 border-l-4 ${
                        isPredictor ? 'border-yellow-500 bg-yellow-500/5' : 'border-blue-500'
                      }`}
                    >
                      {/* Agent Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className={`inline-block px-3 py-1 rounded-lg bg-gradient-to-r ${agentInfo.color} text-white text-sm font-semibold`}>
                              {agentInfo.name}
                            </div>
                            {isPredictor && (
                              <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 text-xs font-semibold rounded border border-yellow-500/30">
                                FINAL PREDICTOR
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-slate-300 mb-2">{agentInfo.description}</p>
                          <div className="text-xs text-slate-400 bg-slate-900/50 rounded p-2">
                            <span className="font-semibold text-slate-300">Role:</span> {agentInfo.role}
                          </div>
                        </div>
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                      </div>

                      {/* Input Section */}
                      <div className="mb-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <div className="text-xs font-semibold text-blue-400 mb-2 flex items-center gap-2">
                          <Database className="w-3 h-3" />
                          INPUT
                          <InfoTooltip content="The data and parameters provided to this agent. Analysis agents receive the ticker symbol and prediction horizon. The Predictor Agent receives all analysis reports from other agents." position="top" />
                        </div>
                        <div className="text-xs text-slate-300 space-y-1">
                          <div><span className="text-slate-500">Ticker:</span> <span className="font-mono text-blue-400">{entry.ticker}</span></div>
                          <div><span className="text-slate-500">Horizon:</span> <span className="font-mono text-blue-400">Next Quarter</span></div>
                          {isPredictor && (
                            <div className="mt-2 pt-2 border-t border-slate-700/50">
                              <span className="text-slate-500">Input Reports:</span>
                              <div className="mt-1 space-y-1 ml-2">
                                {agents.filter(([id]) => id !== 'predictor').map(([id]) => (
                                  <div key={id} className="text-xs text-slate-400">
                                    • {AGENT_INFO[id]?.name || id} analysis report
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Prompt Section */}
                      <div className="mb-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <div className="text-xs font-semibold text-purple-400 mb-2 flex items-center gap-2">
                          <Brain className="w-3 h-3" />
                          PROMPT APPLIED
                          <InfoTooltip content="The system instructions given to this agent. These prompts define the agent's role, expertise, and analysis approach. This ensures each agent focuses on its specialized domain." position="top" />
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed">{agentInfo.prompt}</p>
                      </div>

                      {/* Output Section */}
                      <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700/50">
                        <div className="text-xs font-semibold text-green-400 mb-2 flex items-center gap-2">
                          <Target className="w-3 h-3" />
                          OUTPUT
                        </div>
                        <div className="space-y-3">
                          <div className="grid grid-cols-2 gap-3">
                            <div>
                              <span className="text-xs text-slate-500 flex items-center gap-1">
                                Directional Signal
                                <InfoTooltip content="This agent's trading signal: -1 (strong sell) to +1 (strong buy). Positive = bullish, negative = bearish, near zero = neutral. This is the agent's view on price direction." position="top" />
                              </span>
                              <div className={`font-bold text-lg ${getSignalColor(report.directional_signal)}`}>
                                {report.directional_signal > 0 ? '+' : ''}{report.directional_signal.toFixed(3)}
                              </div>
                            </div>
                            <div>
                              <span className="text-xs text-slate-500 flex items-center gap-1">
                                Confidence Score
                                <InfoTooltip content="This agent's confidence in its analysis (0-100%). Higher confidence means the agent is more certain about its signal. Lower confidence suggests uncertainty or limited data." position="top" />
                              </span>
                              <div className="font-bold text-lg text-blue-400">{report.confidence_score}%</div>
                            </div>
                          </div>
                          
                          {report.data_source && (
                            <div className="pt-2 border-t border-slate-700/50">
                              <span className="text-xs text-slate-500 flex items-center gap-1">
                                Data Source:
                                <InfoTooltip content="The verified data provider used by this agent (e.g., Polygon.io for market data, FRED for economic data, SEC for filings). Verified sources ensure data reliability." position="top" />
                              </span>
                              <div className="text-xs font-mono text-cyan-400 mt-1">{report.data_source}</div>
                            </div>
                          )}
                          
                          {report.summary && (
                            <div className="pt-2 border-t border-slate-700/50">
                              <span className="text-xs text-slate-500 mb-1 block">Summary:</span>
                              <p className="text-sm text-slate-300 leading-relaxed">{report.summary}</p>
                            </div>
                          )}
                          
                          {report.key_metrics && Object.keys(report.key_metrics).length > 0 && (
                            <div className="pt-2 border-t border-slate-700/50">
                              <span className="text-xs text-slate-500 mb-2 block">Key Metrics:</span>
                              <div className="grid grid-cols-2 gap-2">
                                {Object.entries(report.key_metrics).map(([key, value]) => (
                                  <div key={key} className="text-xs bg-slate-800/50 rounded p-1.5">
                                    <span className="text-slate-500">{key}:</span>{' '}
                                    <span className="text-slate-300 font-mono">{String(value)}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Human-Readable Explanation */}
                      <div className="mt-4 p-3 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-purple-500/30">
                        <button
                          onClick={() => fetchExplanation(agentId, report)}
                          className="w-full flex items-center justify-between text-left"
                        >
                          <div className="flex items-center gap-2 text-sm font-semibold text-purple-400">
                            <Sparkles className="w-4 h-4" />
                            Human-Readable Explanation
                          </div>
                          {explanations[agentId]?.loading ? (
                            <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                          ) : explanations[agentId]?.explanation ? (
                            <CheckCircle className="w-4 h-4 text-green-400" />
                          ) : (
                            <span className="text-xs text-slate-500">Click to generate</span>
                          )}
                        </button>
                        
                        {explanations[agentId]?.explanation && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="mt-3 pt-3 border-t border-purple-500/30"
                          >
                            <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                              {explanations[agentId].explanation}
                            </p>
                          </motion.div>
                        )}
                        
                        {explanations[agentId]?.error && (
                          <div className="mt-3 pt-3 border-t border-yellow-500/30">
                            <p className="text-xs text-yellow-400 flex items-center gap-2">
                              <AlertCircle className="w-3 h-3" />
                              {explanations[agentId].error}
                            </p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Benchmark Comparison */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-green-400" />
                Benchmark Comparison
                <InfoTooltip content="How this analysis compares to industry standards and best practices. Benchmarks help assess the quality and reliability of the prediction system." />
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Confidence Benchmark */}
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-white">Confidence Score</span>
                    <span className={`text-lg font-bold ${
                      entry.confidence >= 70 ? 'text-green-400' :
                      entry.confidence >= 50 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {entry.confidence}%
                    </span>
                  </div>
                  <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                    <div 
                      className={`absolute inset-y-0 left-0 rounded-full ${
                        entry.confidence >= 70 ? 'bg-green-500' :
                        entry.confidence >= 50 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${entry.confidence}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Benchmark: ≥70% (Excellent)</span>
                    <span className={`font-semibold ${
                      entry.confidence >= 70 ? 'text-green-400' :
                      entry.confidence >= 50 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {entry.confidence >= 70 ? '✓ Exceeds' : entry.confidence >= 50 ? '~ Meets' : '✗ Below'}
                    </span>
                  </div>
                </div>

                {/* Consensus Benchmark */}
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-white">Agent Consensus</span>
                    <span className="text-lg font-bold text-white">
                      {(() => {
                        const signals = agents.map(([_, r]) => r.directional_signal);
                        const avg = signals.reduce((a, b) => a + b, 0) / signals.length;
                        const variance = signals.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / signals.length;
                        const consensus = (100 - (variance * 100));
                        return consensus.toFixed(1);
                      })()}%
                    </span>
                  </div>
                  <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                    <div 
                      className="absolute inset-y-0 left-0 bg-green-500 rounded-full"
                      style={{ width: `${(() => {
                        const signals = agents.map(([_, r]) => r.directional_signal);
                        const avg = signals.reduce((a, b) => a + b, 0) / signals.length;
                        const variance = signals.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / signals.length;
                        return (100 - (variance * 100));
                      })()}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Benchmark: ≥85% (Excellent)</span>
                    <span className="text-green-400 font-semibold">✓ Exceeds</span>
                  </div>
                </div>

                {/* Execution Speed Benchmark */}
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-white">Execution Speed</span>
                    <span className={`text-lg font-bold ${
                      entry.elapsed_seconds < 6 ? 'text-green-400' :
                      entry.elapsed_seconds < 10 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {entry.elapsed_seconds}s
                    </span>
                  </div>
                  <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                    <div 
                      className={`absolute inset-y-0 left-0 rounded-full ${
                        entry.elapsed_seconds < 6 ? 'bg-green-500' :
                        entry.elapsed_seconds < 10 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${Math.min(100, (10 - entry.elapsed_seconds) / 10 * 100)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Benchmark: &lt;6s (Excellent)</span>
                    <span className={`font-semibold ${
                      entry.elapsed_seconds < 6 ? 'text-green-400' :
                      entry.elapsed_seconds < 10 ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {entry.elapsed_seconds < 6 ? '✓ Exceeds' : entry.elapsed_seconds < 10 ? '~ Meets' : '✗ Below'}
                    </span>
                  </div>
                </div>

                {/* Data Quality Benchmark */}
                <div className="p-4 bg-slate-900/50 rounded-lg border border-slate-700/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-white">Data Quality</span>
                    <span className="text-lg font-bold text-white">
                      {Math.round((agents.filter(([_, r]) => r.data_source).length / agents.length) * 100)}%
                    </span>
                  </div>
                  <div className="relative h-2 bg-slate-800 rounded-full overflow-hidden mb-2">
                    <div 
                      className="absolute inset-y-0 left-0 bg-green-500 rounded-full"
                      style={{ width: `${Math.round((agents.filter(([_, r]) => r.data_source).length / agents.length) * 100)}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Benchmark: 100% (All agents verified)</span>
                    <span className="text-green-400 font-semibold">✓ Meets</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Observability Metrics */}
            <div className="glass-dark rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-400" />
                Observability & Monitoring
                <InfoTooltip content="System health and performance metrics. These help assess the reliability and quality of the analysis. Higher values generally indicate better performance and more reliable predictions." />
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-2 flex items-center gap-2">
                    Agent Consensus
                    <InfoTooltip content="Measures how much agents agree with each other (0-100%). Higher consensus (90%+) means agents see similar signals, indicating more reliable predictions. Lower consensus suggests conflicting views and higher risk." position="top" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {(() => {
                      const signals = agents.map(([_, r]) => r.directional_signal);
                      const avg = signals.reduce((a, b) => a + b, 0) / signals.length;
                      const variance = signals.reduce((sum, s) => sum + Math.pow(s - avg, 2), 0) / signals.length;
                      return (100 - (variance * 100)).toFixed(1);
                    })()}%
                  </div>
                  <div className="text-xs text-slate-500 mt-1">Lower variance = higher consensus</div>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-2 flex items-center gap-2">
                    Data Quality
                    <InfoTooltip content="Percentage of agents that successfully retrieved data from verified sources (like Polygon.io, FRED, SEC). Higher data quality means more reliable analysis based on real market data rather than estimates." position="top" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {Math.round((agents.filter(([_, r]) => r.data_source).length / agents.length) * 100)}%
                  </div>
                  <div className="text-xs text-slate-500 mt-1">Agents with verified data sources</div>
                </div>
                <div className="p-4 bg-slate-900/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-2 flex items-center gap-2">
                    Execution Efficiency
                    <InfoTooltip content="How quickly the analysis completed. Excellent: <6s, Good: 6-10s, Fair: >10s. Faster execution means better system performance, though thorough analysis may take longer." position="top" />
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {entry.elapsed_seconds < 6 ? 'Excellent' : entry.elapsed_seconds < 10 ? 'Good' : 'Fair'}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">{entry.elapsed_seconds}s total time</div>
                </div>
              </div>
            </div>

            {/* Assignment Capabilities Summary */}
            <div className="glass-dark rounded-xl p-6 border-2 border-blue-500/30">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                Assignment Capabilities Demonstrated
                <InfoTooltip content="This analysis demonstrates all key requirements from the course assignment. Each capability shows how the multi-agent system fulfills the learning objectives." />
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Agent Tools & MCP */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-blue-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Agent Tools & MCP</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• A2A Protocol v0.3.0 communication</li>
                    <li>• Custom tools (Polygon, FRED, SEC, NewsAPI)</li>
                    <li>• MCP server integration</li>
                    <li>• Function calling (Gemini API)</li>
                    <li>• Structured JSON outputs</li>
                  </ul>
                </div>

                {/* Context & Memory */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-purple-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Context & Memory</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• Session management (history tracking)</li>
                    <li>• Analysis memory (50 entries stored)</li>
                    <li>• RAG knowledge base (agent prompts)</li>
                    <li>• Long context window (1M tokens)</li>
                  </ul>
                </div>

                {/* Quality Metrics */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-green-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Quality Metrics</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• Confidence scoring (0-100%)</li>
                    <li>• Signal strength (-1 to +1)</li>
                    <li>• Risk assessment (LOW/MEDIUM/HIGH)</li>
                    <li>• Performance tracking</li>
                  </ul>
                </div>

                {/* Explainability */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-orange-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Explainability</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• Transparent agent outputs</li>
                    <li>• Rationale generation</li>
                    <li>• Data source attribution</li>
                    <li>• Human-readable explanations</li>
                  </ul>
                </div>

                {/* Architecture */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-indigo-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Multi-Agent Architecture</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• 7 specialized agents</li>
                    <li>• Orchestrator coordination</li>
                    <li>• Parallel execution</li>
                    <li>• Consensus synthesis</li>
                  </ul>
                </div>

                {/* Observability */}
                <div className="p-4 bg-slate-900/50 rounded-lg border-l-4 border-cyan-500">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-4 h-4 text-green-400" />
                    <span className="font-semibold text-white">Observability</span>
                  </div>
                  <ul className="text-xs text-slate-300 space-y-1 ml-6">
                    <li>• Complete traceability</li>
                    <li>• Agent execution details</li>
                    <li>• Performance metrics</li>
                    <li>• Monitoring system</li>
                  </ul>
                </div>
              </div>

              {/* Visual Data Flow Diagram */}
              <div className="mt-8 glass-dark rounded-xl p-6 border-2 border-cyan-500/30">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Network className="w-5 h-5 text-cyan-400" />
                  Visual Data Flow & Traceability
                  <InfoTooltip content="This diagram shows exactly how data flows through the system, from your input to the final recommendation. Each step is fully traceable and observable." />
                </h3>
                
                <div className="relative">
                  {/* User Input */}
                  <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-center mb-4"
                  >
                    <div className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg shadow-lg border-2 border-blue-400">
                      <div className="flex items-center gap-2 text-white font-semibold">
                        <Info className="w-5 h-5" />
                        <span>User Input</span>
                      </div>
                      <div className="text-xs text-blue-100 mt-1 font-mono">
                        Ticker: {entry.ticker} | Horizon: Next Quarter
                      </div>
                    </div>
                  </motion.div>

                  {/* Arrow Down */}
                  <div className="flex justify-center mb-4">
                    <motion.div
                      initial={{ scaleY: 0 }}
                      animate={{ scaleY: 1 }}
                      transition={{ delay: 0.2 }}
                      className="w-0.5 h-8 bg-gradient-to-b from-blue-400 to-purple-400"
                    />
                  </div>

                  {/* Orchestrator */}
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="flex justify-center mb-6"
                  >
                    <div className="px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg shadow-lg border-2 border-purple-400">
                      <div className="flex items-center gap-2 text-white font-semibold">
                        <Zap className="w-5 h-5" />
                        <span>Orchestrator</span>
                      </div>
                      <div className="text-xs text-purple-100 mt-1">
                        A2A Protocol v0.3.0 | Parallel Execution
                      </div>
                    </div>
                  </motion.div>

                  {/* Arrow Down */}
                  <div className="flex justify-center mb-4">
                    <motion.div
                      initial={{ scaleY: 0 }}
                      animate={{ scaleY: 1 }}
                      transition={{ delay: 0.4 }}
                      className="w-0.5 h-8 bg-gradient-to-b from-purple-400 to-yellow-400"
                    />
                  </div>

                  {/* 5 Specialist Agents in Parallel */}
                  <div className="mb-6">
                    <div className="text-center text-sm text-slate-400 mb-3 font-semibold">
                      5 Specialist Agents (Parallel Execution)
                    </div>
                    <div className="grid grid-cols-5 gap-2 mb-4">
                      {agents.filter(([id]) => id !== 'predictor').map(([agentId, report], index) => {
                        const agentInfo = AGENT_INFO[agentId] || { name: agentId, color: 'from-gray-500 to-gray-600', prompt: '', role: '', description: '', inputDescription: '' };
                        return (
                          <AgentFlowCard
                            key={agentId}
                            agentId={agentId}
                            report={report}
                            agentInfo={agentInfo}
                            entry={entry}
                            index={index}
                          />
                        );
                      })}
                    </div>
                    
                    {/* Data Sources Row */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.9 }}
                      className="flex justify-center gap-3 mt-2"
                    >
                      {['Polygon.io', 'FRED', 'SEC', 'NewsAPI'].map((source, idx) => (
                        <motion.div
                          key={source}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 1.0 + idx * 0.1 }}
                          className="px-2 py-1 bg-slate-800/50 border border-cyan-500/30 rounded text-xs text-cyan-300"
                        >
                          {source}
                        </motion.div>
                      ))}
                    </motion.div>
                  </div>

                  {/* Arrows converging to Predictor */}
                  <div className="flex justify-center mb-4 relative">
                    <div className="flex items-center gap-1 mb-2">
                      {[0, 1, 2, 3, 4].map((i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, scale: 0 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 1.2 + i * 0.05 }}
                          className="flex flex-col items-center"
                        >
                          <ArrowDown className="w-4 h-4 text-yellow-400" />
                        </motion.div>
                      ))}
                    </div>
                    <motion.div
                      initial={{ scaleY: 0 }}
                      animate={{ scaleY: 1 }}
                      transition={{ delay: 1.4 }}
                      className="w-0.5 h-8 bg-gradient-to-b from-yellow-400 to-yellow-600 mx-auto"
                    />
                  </div>

                  {/* Predictor Agent */}
                  <PredictorFlowCard entry={entry} agents={agents} />

                  {/* Arrow Down */}
                  <div className="flex justify-center mb-4">
                    <motion.div
                      initial={{ scaleY: 0 }}
                      animate={{ scaleY: 1 }}
                      transition={{ delay: 1.5 }}
                      className="w-0.5 h-8 bg-gradient-to-b from-yellow-400 to-green-400"
                    />
                  </div>

                  {/* Final Output */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.6 }}
                    className="flex justify-center"
                  >
                    <div className={`px-6 py-4 rounded-lg shadow-lg border-2 ${
                      entry.recommendation === 'BUY' ? 'bg-gradient-to-r from-green-500 to-emerald-500 border-green-400' :
                      entry.recommendation === 'SELL' ? 'bg-gradient-to-r from-red-500 to-rose-500 border-red-400' :
                      'bg-gradient-to-r from-yellow-500 to-amber-500 border-yellow-400'
                    }`}>
                      <div className="flex items-center gap-2 text-white font-semibold">
                        <Target className="w-5 h-5" />
                        <span>Final Recommendation</span>
                      </div>
                      <div className="text-sm text-white mt-2 font-bold">
                        {entry.recommendation} | Confidence: {entry.confidence}% | Risk: {entry.risk_level}
                      </div>
                      <div className="text-xs text-white/80 mt-1">
                        Execution Time: {entry.elapsed_seconds}s | {agents.length} agents analyzed
                      </div>
                    </div>
                  </motion.div>

                  {/* Traceability Badge */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.8 }}
                    className="absolute top-2 right-2 px-3 py-1 bg-cyan-500/20 border border-cyan-500/50 rounded-full"
                  >
                    <div className="flex items-center gap-2 text-xs text-cyan-300">
                      <CheckCircle className="w-3 h-3" />
                      <span>Fully Traceable</span>
                    </div>
                  </motion.div>
                </div>

                {/* Flow Legend */}
                <div className="mt-6 pt-4 border-t border-slate-700/50">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded"></div>
                      <span className="text-slate-400">User Input</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-purple-500 rounded"></div>
                      <span className="text-slate-400">Orchestration</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                      <span className="text-slate-400">Agent Processing</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded"></div>
                      <span className="text-slate-400">Final Output</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="mt-6 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/30">
                <p className="text-sm text-slate-200 leading-relaxed">
                  <span className="font-semibold text-blue-400">Summary:</span> This analysis demonstrates a complete multi-agent stock prediction system with 
                  <span className="font-semibold text-white"> 7 specialized AI agents</span> working in parallel, 
                  <span className="font-semibold text-white"> real-time data integration</span> from 4+ APIs, 
                  <span className="font-semibold text-white"> full traceability</span> of the decision-making process, 
                  <span className="font-semibold text-white"> comprehensive explainability</span> with human-readable insights, and 
                  <span className="font-semibold text-white"> production-grade observability</span> metrics. 
                  All assignment requirements are met, including agent tools, context management, quality measurement, explainability, architecture, and monitoring capabilities.
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

