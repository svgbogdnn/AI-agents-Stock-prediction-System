export interface AgentStatus {
  id: string;
  name: string;
  status: 'idle' | 'working' | 'completed' | 'error';
  progress: number;
  signal?: number;
  confidence?: number;
  summary?: string;
  keyMetrics?: Record<string, any>;
  error?: string;
}

export interface AnalysisResult {
  ticker: string;
  recommendation: string;
  confidence: number;
  weighted_signal: number;
  risk_level: string;
  rationale: string;
  analysis_reports: Record<string, AgentResponse>;
  elapsed_seconds: number;
}

export interface AgentResponse {
  agent: string;
  ticker: string;
  directional_signal: number;
  confidence_score: number;
  key_metrics?: Record<string, any>;
  summary?: string;
  data_source?: string;
}

export interface OrchestratorStatus {
  status: 'idle' | 'initializing' | 'analyzing' | 'synthesizing' | 'completed' | 'error';
  message: string;
  progress: number;
}

export interface NewsArticle {
  title: string;
  url: string;
  source: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  snippet: string;
  image_url?: string;
}

