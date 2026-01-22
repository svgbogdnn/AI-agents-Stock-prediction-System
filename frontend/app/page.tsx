'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Sparkles, AlertCircle, BarChart3, Clock, Award, Bot } from 'lucide-react';
import { FaChartLine, FaChartBar, FaNewspaper, FaGlobeAmericas, FaBalanceScale, FaLightbulb } from 'react-icons/fa';
import StockInput from './components/StockInput';
import OrchestratorCard from './components/OrchestratorCard';
import AgentCard from './components/AgentCard';
import AgentDetailModal from './components/AgentDetailModal';
import ResultsPanel from './components/ResultsPanel';
import InvestorAdvisorCard from './components/InvestorAdvisorCard';
import TradingViewWidget from './components/TradingViewWidget';
import { AgentStatus, AnalysisResult, OrchestratorStatus } from './types';

const AGENTS = [
  { id: 'fundamental', name: 'Fundamental Analyst', icon: FaChartLine, color: 'from-blue-500 to-cyan-500' },
  { id: 'technical', name: 'Technical Analyst', icon: FaChartBar, color: 'from-green-500 to-emerald-500' },
  { id: 'sentiment', name: 'Sentiment Analyst', icon: FaNewspaper, color: 'from-purple-500 to-pink-500' },
  { id: 'macro', name: 'Macro Analyst', icon: FaGlobeAmericas, color: 'from-orange-500 to-red-500' },
  { id: 'regulatory', name: 'Regulatory Analyst', icon: FaBalanceScale, color: 'from-yellow-500 to-amber-500' },
];

export default function Home() {
  const [ticker, setTicker] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [orchestratorStatus, setOrchestratorStatus] = useState<OrchestratorStatus>({
    status: 'idle',
    message: 'Ready to analyze',
    progress: 0,
  });
  const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>(
    AGENTS.map(agent => ({
      id: agent.id,
      name: agent.name,
      status: 'idle',
      progress: 0,
    }))
  );
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [investorAdvice, setInvestorAdvice] = useState<string | null>(null);
  const [isGeneratingAdvice, setIsGeneratingAdvice] = useState(false);
  const [adviceError, setAdviceError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAnalyze = async (inputTicker: string) => {
    setTicker(inputTicker.toUpperCase());
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    // Reset statuses
    setOrchestratorStatus({ status: 'initializing', message: 'Initializing multi-agent system...', progress: 10 });
    setAgentStatuses(prev => prev.map(agent => ({ ...agent, status: 'idle', progress: 0 })));

    try {
      // Step 1: Orchestrator initializing
      await new Promise(resolve => setTimeout(resolve, 1000));
      setOrchestratorStatus({ status: 'analyzing', message: 'Coordinating specialist agents...', progress: 30 });

      // Step 2: Agents start working
      await new Promise(resolve => setTimeout(resolve, 500));
      setAgentStatuses(prev => prev.map(agent => ({ ...agent, status: 'working', progress: 20 })));

      // Step 3: Call backend API
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker: inputTicker.toUpperCase(), horizon: 'next_quarter' }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data: AnalysisResult = await response.json();

      // Step 4: Update agents with results
      setAgentStatuses(prev =>
        prev.map(agent => {
          const agentData = data.analysis_reports[agent.id];
          return {
            ...agent,
            status: agentData ? 'completed' : 'error',
            progress: 100,
            signal: agentData?.directional_signal,
            confidence: agentData?.confidence_score,
            summary: agentData?.summary,
            keyMetrics: agentData?.key_metrics,
          };
        })
      );

      // Step 5: Synthesizing
      setOrchestratorStatus({ status: 'synthesizing', message: 'Synthesizing final prediction...', progress: 80 });
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Step 6: Complete
      setOrchestratorStatus({ status: 'completed', message: 'Analysis complete!', progress: 100 });
      setResult(data);

      // Save to history
      try {
        const historyEntry = {
          ...data,
          id: `${data.ticker}-${Date.now()}`,
          timestamp: new Date().toISOString(),
        };
        
        const existingHistory = localStorage.getItem('analysis_history');
        const history = existingHistory ? JSON.parse(existingHistory) : [];
        history.unshift(historyEntry); // Add to beginning
        
        // Keep only last 50 entries
        if (history.length > 50) {
          history.length = 50;
        }
        
        localStorage.setItem('analysis_history', JSON.stringify(history));
      } catch (storageErr) {
        console.error('Failed to save to history:', storageErr);
      }

      // Step 7: Generate investor advice
      setIsGeneratingAdvice(true);
      setAdviceError(null);
      try {
        const adviceResponse = await fetch('/api/investor-advice', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ analysis: data }),
        });
        
        const adviceData = await adviceResponse.json();
        
        if (adviceResponse.ok) {
          setInvestorAdvice(adviceData.advice);
        } else {
          console.error('Investor advice API error:', adviceData);
          setAdviceError(adviceData.detail || 'Failed to generate advice');
        }
      } catch (adviceErr: any) {
        console.error('Failed to generate investor advice:', adviceErr);
        setAdviceError(adviceErr.message || 'Network error generating advice');
      } finally {
        setIsGeneratingAdvice(false);
      }

    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis');
      setOrchestratorStatus({ status: 'error', message: 'Analysis failed', progress: 0 });
      setAgentStatuses(prev => prev.map(agent => ({ ...agent, status: 'error', progress: 0 })));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setTicker('');
    setResult(null);
    setError(null);
    setInvestorAdvice(null);
    setIsGeneratingAdvice(false);
    setSelectedAgent(null);
    setIsModalOpen(false);
    setOrchestratorStatus({ status: 'idle', message: 'Ready to analyze', progress: 0 });
    setAgentStatuses(prev => prev.map(agent => ({ ...agent, status: 'idle', progress: 0 })));
  };

  const handleViewAgentDetails = (agent: AgentStatus) => {
    setSelectedAgent(agent);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <main className="min-h-screen p-4 md:p-8 relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/3 rounded-full blur-3xl" />
      </div>
      
      {/* Grid Pattern Overlay */}
      <div className="fixed inset-0 pointer-events-none opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
                           linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16 relative"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 mb-6">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-sm text-blue-400 font-medium">Powered by AI Agents</span>
          </div>

          
          <div className="flex flex-wrap items-center justify-center gap-2 md:gap-3 mb-3">
            <p className="text-slate-300 text-lg md:text-xl font-light">
              Multi-Agent A2A Architecture powered by
            </p>
            <div className="flex items-center gap-2">
              <img
                src="https://static0.anpoimages.com/wordpress/wp-content/uploads/2020/12/14/google-dark-background-hero.png"
                alt="Google"
                className="h-7 md:h-10 object-contain opacity-90 hover:opacity-100 transition-opacity"
              />
              <span className="text-slate-300 text-lg md:text-xl font-light">Gemini</span>
            </div>
            <span className="text-slate-500 hidden md:inline">•</span>
            <img
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Kaggle_Logo.svg/1200px-Kaggle_Logo.svg.png"
              alt="Kaggle"
              className="h-7 md:h-10 object-contain opacity-90 hover:opacity-100 transition-opacity"
            />
          </div>
          <p className="text-slate-500 text-sm">
            By svg
          </p>
        </motion.div>

        {/* Input Section */}
        {!isAnalyzing && !result && (
          <>
            <StockInput onAnalyze={handleAnalyze} isLoading={false} />
            
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="flex flex-wrap gap-4 justify-center mt-6"
            >
              <a
                href="/compare"
                className="flex items-center gap-2 px-6 py-3 glass hover:bg-slate-800/50 rounded-xl transition-all font-semibold"
              >
                <BarChart3 className="w-5 h-5" />
                Compare Stocks
              </a>
              <a
                href="/history"
                className="flex items-center gap-2 px-6 py-3 glass hover:bg-slate-800/50 rounded-xl transition-all font-semibold"
              >
                <Clock className="w-5 h-5" />
                View History
              </a>
              <a
                href="/capabilities"
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600/20 to-purple-600/20 hover:from-blue-600/30 hover:to-purple-600/30 border border-blue-500/30 rounded-xl transition-all font-semibold"
              >
                <Award className="w-5 h-5 text-blue-400" />
                Assignment Capabilities
              </a>
            </motion.div>
          </>
        )}

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="mb-8 glass p-6 rounded-2xl border-red-500/50"
            >
              <div className="flex items-center gap-3 text-red-400">
                <AlertCircle className="w-6 h-6" />
                <div>
                  <h3 className="font-semibold">Analysis Error</h3>
                  <p className="text-sm text-gray-300">{error}</p>
                </div>
              </div>
              <button
                onClick={handleReset}
                className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg transition-colors"
              >
                Try Again
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Analysis View */}
        <AnimatePresence mode="wait">
          {(isAnalyzing || result) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* Orchestrator */}
              <OrchestratorCard
                ticker={ticker}
                status={orchestratorStatus}
              />

              {/* Agents Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {agentStatuses.map((agent, index) => {
                  const agentConfig = AGENTS.find(a => a.id === agent.id);
                  return (
                    <AgentCard
                      key={agent.id}
                      agent={agent}
                      icon={agentConfig?.icon || Bot}
                      color={agentConfig?.color || 'from-gray-500 to-gray-600'}
                      delay={index * 0.1}
                      onViewDetails={() => handleViewAgentDetails(agent)}
                    />
                  );
                })}
              </div>

              {/* Results */}
              {result && (
                <>
                  <ResultsPanel
                    result={result}
                    onReset={handleReset}
                  />
                  
                  {/* TradingView Chart */}
                  <TradingViewWidget ticker={ticker} />
                  
                  {/* Investor Advisor Card */}
                  <InvestorAdvisorCard
                    advice={investorAdvice}
                    isGenerating={isGeneratingAdvice}
                    error={adviceError}
                    ticker={ticker}
                  />
                  
                  {/* Footer */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center text-sm text-slate-500 mt-8 pt-6 border-t border-slate-800/50"
                  >
                    <p className="font-medium">Analysis completed using A2A Protocol v0.3.0 • Powered by Google Gemini 2.0</p>
                    <p className="mt-2 text-xs">By svg</p>
                  </motion.div>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          icon={AGENTS.find(a => a.id === selectedAgent.id)?.icon || (() => null)}
          color={AGENTS.find(a => a.id === selectedAgent.id)?.color || 'from-gray-500 to-gray-600'}
        />
      )}
    </main>
  );
}

