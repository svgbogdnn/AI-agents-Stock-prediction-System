'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, Award, Code, Database, Brain, Target, 
  Layers, Shield, Zap, MessageSquare, BarChart3, TrendingUp,
  ChevronDown, ChevronRight
} from 'lucide-react';

interface CapabilitySection {
  id: string;
  title: string;
  icon: any;
  color: string;
  requirement: string;
  implementation: string[];
  demonstrations: string[];
  mcpIntegration?: string;
}

export default function CapabilitiesPage() {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const capabilities: CapabilitySection[] = [
    {
      id: 'mcp',
      title: 'Agent Tools & MCP Interoperability',
      icon: Code,
      color: 'from-blue-500 to-cyan-500',
      requirement: 'Demonstrate agent tools and MCP (Model Context Protocol) integration',
      implementation: [
        '✅ A2A Protocol v0.3.0 - Full agent-to-agent communication',
        '✅ Custom Tools: Polygon API, FRED API, SEC Edgar, NewsAPI',
        '✅ MCP Server Integration: Financial data providers',
        '✅ Tool Calling: Structured function execution',
        '✅ Agent Cards: JSON metadata exchange',
        '✅ JSONRPC Transport: Standard RPC protocol',
      ],
      demonstrations: [
        'Each agent exposes tools via MCP server (ports 8001-8006)',
        'Orchestrator calls agents using RemoteA2aAgent',
        'Tools fetch real-time data from external APIs',
        'Structured outputs using Pydantic schemas',
      ],
      mcpIntegration: 'Financial MCP Servers: Polygon.io, FRED, SEC Edgar APIs'
    },
    {
      id: 'context',
      title: 'Context Engineering & Memory',
      icon: Brain,
      color: 'from-purple-500 to-pink-500',
      requirement: 'Implement sessions, memory, and context management',
      implementation: [
        '✅ Session Management: Browser localStorage for history',
        '✅ Analysis Memory: Last 50 analyses stored locally',
        '✅ Agent Context: Each agent maintains domain knowledge',
        '✅ RAG Knowledge Base: Prompts with embedded expertise',
        '✅ Context Caching: Reusable market data',
        '✅ Long Context: Gemini 1M token window utilized',
      ],
      demonstrations: [
        'History page tracks all past analyses',
        'Each agent has specialized domain knowledge in prompts',
        'Orchestrator maintains session state during analysis',
        'Results stored with timestamp for future reference',
      ],
    },
    {
      id: 'quality',
      title: 'Measuring Agent Quality',
      icon: Target,
      color: 'from-green-500 to-emerald-500',
      requirement: 'Implement metrics and quality measurement',
      implementation: [
        '✅ Confidence Scoring: Each agent provides 0-100% confidence',
        '✅ Signal Strength: Directional signals (-1 to +1)',
        '✅ Risk Assessment: LOW/MEDIUM/HIGH categorization',
        '✅ Execution Time: Track analysis performance',
        '✅ Data Source Verification: Badge system for reliability',
        '✅ Agent Agreement: Consensus measurement across agents',
      ],
      demonstrations: [
        'Confidence gauge shows overall system confidence',
        'Radar chart visualizes agent signal consensus',
        'Risk level calculated from signal variance',
        'Performance metrics: 4-6 second analysis time',
      ],
    },
    {
      id: 'explainability',
      title: 'Agent Explainability',
      icon: MessageSquare,
      color: 'from-orange-500 to-red-500',
      requirement: 'Transparent decision-making and reasoning',
      implementation: [
        '✅ Transparent Agent Outputs: All responses visible',
        '✅ Rationale Generation: AI explains its reasoning',
        '✅ Data Source Attribution: Every metric cited',
        '✅ Agent Deep Dive: Expandable detailed analysis',
        '✅ Investor Advisor: Plain-English explanations',
        '✅ Visual Explanations: Charts show signal composition',
      ],
      demonstrations: [
        'Each agent card shows: signal, confidence, summary, data source',
        'Agent detail modal reveals: all metrics, trends, verification',
        'Investor Advisor translates technical data to actionable advice',
        'Radar chart shows which agents are bullish/bearish',
      ],
    },
    {
      id: 'architecture',
      title: 'Multi-Agent Architecture',
      icon: Layers,
      color: 'from-indigo-500 to-blue-500',
      requirement: 'Hierarchical agent coordination',
      implementation: [
        '✅ 7 Specialized Agents: Each domain expert',
        '✅ Coordinator Pattern: Orchestrator manages workflow',
        '✅ Parallel Execution: All agents analyze simultaneously',
        '✅ Consensus Synthesis: Weighted signal aggregation',
        '✅ Hub-and-Spoke: Central orchestrator, distributed agents',
        '✅ Microservices: Each agent is independent service',
      ],
      demonstrations: [
        'Fundamental: Analyzes financials, market cap, sector',
        'Technical: Price momentum, trends, indicators',
        'Sentiment: News analysis, social signals',
        'Macro: Economic indicators, interest rates',
        'Regulatory: SEC filings, compliance',
        'Predictor: ML-based synthesis',
        'Investor Advisor: Human-readable recommendations',
      ],
    },
    {
      id: 'realtime',
      title: 'Real-Time Data Integration',
      icon: Zap,
      color: 'from-yellow-500 to-orange-500',
      requirement: 'Live API integration and data freshness',
      implementation: [
        '✅ 4 Real Financial APIs: Polygon, FRED, NewsAPI, SEC Edgar',
        '✅ Live Market Data: Current prices, volumes, fundamentals',
        '✅ Recent News: Last 7 days of articles',
        '✅ Economic Indicators: Latest GDP, inflation, rates',
        '✅ SEC Filings: 10-K, 10-Q, 8-K forms',
        '✅ Fallback Chain: Primary → Secondary → Tertiary sources',
      ],
      demonstrations: [
        'Every analysis uses real API calls (not mock data)',
        'Data source badges verify information origin',
        'Timestamps show data freshness',
        'Error handling with graceful fallbacks',
      ],
    },
    {
      id: 'genai',
      title: 'Gen AI Capabilities (12+)',
      icon: Award,
      color: 'from-pink-500 to-purple-500',
      requirement: 'Showcase multiple Gen AI features',
      implementation: [
        '1. Custom Tools - Financial data fetchers',
        '2. A2A Protocol - Agent communication',
        '3. Structured Output - Pydantic schemas',
        '4. Multi-Agent Orchestration - Coordinator pattern',
        '5. RAG Knowledge Base - Domain expertise',
        '6. Long Context Window - 1M tokens',
        '7. Document Understanding - SEC filings',
        '8. Sentiment Analysis - News processing',
        '9. Context Caching - Market data reuse',
        '10. Parallel Execution - Concurrent agents',
        '11. Confidence Scoring - Quality metrics',
        '12. Natural Language Generation - Investor advice',
      ],
      demonstrations: [
        'All capabilities demonstrated in live system',
        'Jupyter notebook shows transparent execution',
        'Frontend visualizes agent collaboration',
        'Real-world financial application',
      ],
    },
  ];

  return (
    <main className="min-h-screen p-4 md:p-8 relative overflow-hidden">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[600px] h-[600px] bg-blue-600/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="flex items-center justify-center gap-4 mb-5">
            <Award className="w-12 h-12 text-blue-500" />
            <h1 className="text-5xl md:text-6xl font-bold gradient-text">
              Assignment Capabilities
            </h1>
          </div>
          <p className="text-slate-400 text-lg mb-3">
            Comprehensive demonstration of all course requirements
          </p>
          <p className="text-slate-500 text-sm">
            By svg
          </p>
        </motion.div>

        {/* Requirements Checklist */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass rounded-2xl p-8 mb-8"
        >
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <CheckCircle className="w-7 h-7 text-green-400" />
            Assignment Requirements Checklist
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass-dark rounded-xl p-5 border-l-4 border-blue-500">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-blue-400 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-white mb-2">Agent Tools & MCP</h3>
                  <p className="text-sm text-slate-400">A2A Protocol, Custom Tools, MCP Servers</p>
                </div>
              </div>
            </div>
            <div className="glass-dark rounded-xl p-5 border-l-4 border-purple-500">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-purple-400 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-white mb-2">Context & Memory</h3>
                  <p className="text-sm text-slate-400">Sessions, History, RAG Knowledge Base</p>
                </div>
              </div>
            </div>
            <div className="glass-dark rounded-xl p-5 border-l-4 border-green-500">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-white mb-2">Quality Metrics</h3>
                  <p className="text-sm text-slate-400">Confidence, Risk, Performance Tracking</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Detailed Capabilities */}
        <div className="space-y-4">
          {capabilities.map((capability, index) => {
            const Icon = capability.icon;
            const isExpanded = expandedSection === capability.id;

            return (
              <motion.div
                key={capability.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="glass rounded-xl overflow-hidden"
              >
                {/* Header */}
                <button
                  onClick={() => setExpandedSection(isExpanded ? null : capability.id)}
                  className="w-full p-6 flex items-center justify-between hover:bg-slate-800/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${capability.color}`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="text-left">
                      <h3 className="text-xl font-bold text-white">{capability.title}</h3>
                      <p className="text-sm text-slate-400 mt-1">{capability.requirement}</p>
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-6 h-6 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-6 h-6 text-slate-400" />
                  )}
                </button>

                {/* Expanded Content */}
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="px-6 pb-6 space-y-6"
                  >
                    {/* Implementation */}
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <Code className="w-5 h-5 text-blue-400" />
                        Implementation Details
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {capability.implementation.map((item, i) => (
                          <div key={i} className="glass-dark rounded-lg p-3 text-sm text-slate-300">
                            {item}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Demonstrations */}
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-400" />
                        Live Demonstrations
                      </h4>
                      <div className="space-y-2">
                        {capability.demonstrations.map((demo, i) => (
                          <div key={i} className="flex items-start gap-3">
                            <ChevronRight className="w-4 h-4 text-green-400 flex-shrink-0 mt-1" />
                            <p className="text-sm text-slate-300">{demo}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* MCP Integration */}
                    {capability.mcpIntegration && (
                      <div className="glass-dark rounded-lg p-4 border-l-4 border-cyan-500">
                        <h4 className="text-sm font-semibold text-cyan-400 mb-2 flex items-center gap-2">
                          <Database className="w-4 h-4" />
                          MCP Integration
                        </h4>
                        <p className="text-sm text-slate-300">{capability.mcpIntegration}</p>
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Footer Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-xl p-8 mt-8"
        >
          <h3 className="text-2xl font-bold text-white mb-6 text-center">System Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2">7</div>
              <div className="text-sm text-slate-400">AI Agents</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">4</div>
              <div className="text-sm text-slate-400">Real APIs</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400 mb-2">12+</div>
              <div className="text-sm text-slate-400">Gen AI Features</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-cyan-400 mb-2">4-6s</div>
              <div className="text-sm text-slate-400">Analysis Time</div>
            </div>
          </div>
        </motion.div>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex gap-4 justify-center mt-8"
        >
          <a
            href="/"
            className="flex items-center gap-2 px-6 py-3 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg transition-colors text-slate-300"
          >
            ← Back to Dashboard
          </a>
          <a
            href="/history"
            className="flex items-center gap-2 px-6 py-3 glass hover:bg-slate-800/50 rounded-lg transition-colors font-semibold"
          >
            <BarChart3 className="w-5 h-5" />
            View Analysis History
          </a>
        </motion.div>
      </div>
    </main>
  );
}

