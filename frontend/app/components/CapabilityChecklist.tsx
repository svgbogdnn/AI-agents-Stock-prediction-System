'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle, Award, Save } from 'lucide-react';

interface CapabilityItem {
  id: string;
  title: string;
  description: string;
  category: string;
}

const CAPABILITIES: CapabilityItem[] = [
  // Agent Tools & MCP
  { id: 'mcp-integration', title: 'MCP Integration', description: 'Agent-to-agent communication via MCP protocol', category: 'Agent Tools & MCP' },
  { id: 'custom-tools', title: 'Custom Tools', description: 'Financial data fetching tools (Polygon, FRED, SEC, NewsAPI)', category: 'Agent Tools & MCP' },
  { id: 'a2a-protocol', title: 'A2A Protocol', description: 'Agent-to-agent communication demonstrated', category: 'Agent Tools & MCP' },
  
  // Context & Memory
  { id: 'session-management', title: 'Session Management', description: 'Browser localStorage for history tracking', category: 'Context & Memory' },
  { id: 'analysis-history', title: 'Analysis History', description: 'Last 50 analyses stored with timestamps', category: 'Context & Memory' },
  { id: 'rag-knowledge', title: 'RAG Knowledge Base', description: 'Domain expertise embedded in prompts', category: 'Context & Memory' },
  
  // Quality Metrics
  { id: 'confidence-scoring', title: 'Confidence Scoring', description: '0-100% confidence scores per agent', category: 'Quality Metrics' },
  { id: 'signal-strength', title: 'Signal Strength', description: 'Directional signals (-1 to +1) visualization', category: 'Quality Metrics' },
  { id: 'risk-assessment', title: 'Risk Assessment', description: 'LOW/MEDIUM/HIGH risk categorization', category: 'Quality Metrics' },
  { id: 'performance-tracking', title: 'Performance Tracking', description: 'Execution time and efficiency metrics', category: 'Quality Metrics' },
  
  // Explainability
  { id: 'transparent-outputs', title: 'Transparent Outputs', description: 'All agent responses visible and accessible', category: 'Explainability' },
  { id: 'rationale-generation', title: 'Rationale Generation', description: 'AI explains reasoning for recommendations', category: 'Explainability' },
  { id: 'data-attribution', title: 'Data Source Attribution', description: 'Every metric cites its data source', category: 'Explainability' },
  { id: 'agent-deep-dive', title: 'Agent Deep Dive', description: 'Expandable detailed analysis per agent', category: 'Explainability' },
  
  // Architecture
  { id: 'multi-agent', title: 'Multi-Agent System', description: '7 specialized agents working together', category: 'Architecture' },
  { id: 'orchestration', title: 'Orchestration Pattern', description: 'Coordinator manages workflow', category: 'Architecture' },
  { id: 'parallel-execution', title: 'Parallel Execution', description: 'Agents analyze simultaneously', category: 'Architecture' },
  { id: 'consensus-synthesis', title: 'Consensus Synthesis', description: 'Weighted signal aggregation', category: 'Architecture' },
  
  // Observability
  { id: 'traceability', title: 'Traceability', description: 'Complete data flow tracking', category: 'Observability' },
  { id: 'agent-details', title: 'Agent Execution Details', description: 'Input/output for each agent visible', category: 'Observability' },
  { id: 'performance-score', title: 'Performance Score', description: 'Overall system performance metric', category: 'Observability' },
  { id: 'monitoring', title: 'Monitoring System', description: 'Real-time metrics and status tracking', category: 'Observability' },
  
  // Real-Time Data
  { id: 'live-apis', title: 'Live API Integration', description: 'Real-time data from financial APIs', category: 'Real-Time Data' },
  { id: 'data-freshness', title: 'Data Freshness', description: 'Timestamps show data recency', category: 'Real-Time Data' },
  { id: 'fallback-chain', title: 'Fallback Chain', description: 'Primary → Secondary → Tertiary sources', category: 'Real-Time Data' },
  
  // Gen AI Features
  { id: 'structured-output', title: 'Structured Output', description: 'Pydantic schemas for responses', category: 'Gen AI Features' },
  { id: 'long-context', title: 'Long Context Window', description: '1M token window utilization', category: 'Gen AI Features' },
  { id: 'document-understanding', title: 'Document Understanding', description: 'SEC filings processing', category: 'Gen AI Features' },
  { id: 'sentiment-analysis', title: 'Sentiment Analysis', description: 'News processing and sentiment', category: 'Gen AI Features' },
  { id: 'nl-generation', title: 'Natural Language Generation', description: 'Investor advice generation', category: 'Gen AI Features' },
];

interface CapabilityChecklistProps {
  onSave?: (checked: string[]) => void;
}

export default function CapabilityChecklist({ onSave }: CapabilityChecklistProps) {
  const [checked, setChecked] = useState<Set<string>>(new Set());
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Load from localStorage
    const stored = localStorage.getItem('capability_checklist');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setChecked(new Set(parsed));
      } catch (error) {
        console.error('Failed to load checklist:', error);
      }
    }
  }, []);

  const toggleCheck = (id: string) => {
    setChecked(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      setHasChanges(true);
      return newSet;
    });
  };

  const handleSave = () => {
    const checkedArray = Array.from(checked);
    localStorage.setItem('capability_checklist', JSON.stringify(checkedArray));
    setHasChanges(false);
    if (onSave) {
      onSave(checkedArray);
    }
  };

  const categories = Array.from(new Set(CAPABILITIES.map(c => c.category)));

  const getProgress = () => {
    return Math.round((checked.size / CAPABILITIES.length) * 100);
  };

  return (
    <div className="glass-dark rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Award className="w-6 h-6 text-yellow-400" />
          <div>
            <h3 className="text-xl font-bold text-white">Assignment Capabilities Checklist</h3>
            <p className="text-sm text-slate-400">Track your video walkthrough progress</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-2xl font-bold text-white">{checked.size}/{CAPABILITIES.length}</div>
            <div className="text-sm text-slate-400">{getProgress()}% Complete</div>
          </div>
          {hasChanges && (
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg transition-colors text-green-400"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="relative h-3 bg-slate-900/80 rounded-full overflow-hidden">
          <motion.div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${getProgress()}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-6">
        {categories.map((category) => {
          const categoryItems = CAPABILITIES.filter(c => c.category === category);
          const categoryChecked = categoryItems.filter(c => checked.has(c.id)).length;
          
          return (
            <div key={category} className="border border-slate-700/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-white">{category}</h4>
                <span className="text-sm text-slate-400">
                  {categoryChecked}/{categoryItems.length}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {categoryItems.map((item) => {
                  const isChecked = checked.has(item.id);
                  return (
                    <motion.button
                      key={item.id}
                      onClick={() => toggleCheck(item.id)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/50 hover:bg-slate-800/50 transition-colors text-left"
                    >
                      {isChecked ? (
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
                      ) : (
                        <Circle className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className={`font-semibold mb-1 ${isChecked ? 'text-white' : 'text-slate-300'}`}>
                          {item.title}
                        </div>
                        <div className="text-xs text-slate-400">{item.description}</div>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

