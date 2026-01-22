"""
Pydantic schemas for structured output from all agents.
Following Day 2 best practices: JSON mode with strict validation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class AnalysisReport(BaseModel):
    """Base schema for all analysis agent outputs."""
    
    agent_name: str = Field(..., description="Name of the agent producing this report")
    ticker: str = Field(..., description="Stock ticker symbol")
    directional_signal: float = Field(
        ..., 
        ge=-1.0, 
        le=1.0,
        description="Trading signal: -1 (strong sell) to 1 (strong buy), 0 (neutral)"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Confidence in the analysis (0-100%)"
    )
    key_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Key numerical metrics specific to this analysis"
    )
    summary: str = Field(..., description="Human-readable summary of the analysis")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_name": "fundamental_analyst",
                "ticker": "GOOGL",
                "directional_signal": 0.7,
                "confidence_score": 82.5,
                "key_metrics": {
                    "pe_ratio": 28.5,
                    "revenue_growth_yoy": 0.12,
                    "debt_to_equity": 0.15
                },
                "summary": "Strong fundamentals with solid revenue growth...",
                "timestamp": "2025-11-21T10:30:00"
            }
        }


class FundamentalReport(AnalysisReport):
    """Fundamental analysis report schema."""
    
    agent_name: str = Field(default="fundamental_analyst")
    
    # Fundamental-specific metrics
    pe_ratio: Optional[float] = Field(None, description="Price-to-Earnings ratio")
    eps_growth: Optional[float] = Field(None, description="EPS growth rate YoY")
    revenue_growth: Optional[float] = Field(None, description="Revenue growth rate YoY")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-Equity ratio")
    current_ratio: Optional[float] = Field(None, description="Current ratio (liquidity)")
    
    @field_validator('directional_signal')
    def validate_signal(cls, v):
        if not -1.0 <= v <= 1.0:
            raise ValueError("directional_signal must be between -1 and 1")
        return v


class TechnicalReport(AnalysisReport):
    """Technical analysis report schema."""
    
    agent_name: str = Field(default="technical_analyst")
    
    # Technical indicators
    rsi: Optional[float] = Field(None, ge=0, le=100, description="Relative Strength Index")
    macd: Optional[float] = Field(None, description="MACD value")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    trend: Optional[Literal["bullish", "bearish", "neutral"]] = Field(
        None, 
        description="Overall trend direction"
    )


class SentimentReport(AnalysisReport):
    """News and sentiment analysis report schema."""
    
    agent_name: str = Field(default="sentiment_analyst")
    
    # Sentiment metrics
    overall_sentiment: Optional[Literal["positive", "negative", "neutral"]] = Field(
        None,
        description="Overall sentiment from news and social media"
    )
    news_count: Optional[int] = Field(None, description="Number of news articles analyzed")
    positive_ratio: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Ratio of positive sentiment (0-1)"
    )
    key_events: Optional[List[str]] = Field(
        default_factory=list,
        description="List of key events detected"
    )


class MacroReport(AnalysisReport):
    """Macro-economic analysis report schema."""
    
    agent_name: str = Field(default="macro_analyst")
    
    # Macro indicators
    gdp_growth: Optional[float] = Field(None, description="GDP growth rate")
    inflation_rate: Optional[float] = Field(None, description="Inflation rate")
    fed_rate: Optional[float] = Field(None, description="Federal funds rate")
    vix_level: Optional[float] = Field(None, description="VIX volatility index")
    market_regime: Optional[Literal["bull", "bear", "sideways"]] = Field(
        None,
        description="Current market regime"
    )


class RegulatoryReport(AnalysisReport):
    """Industry and regulatory analysis report schema."""
    
    agent_name: str = Field(default="regulatory_analyst")
    
    # Regulatory risk factors
    recent_filings: Optional[List[str]] = Field(
        default_factory=list,
        description="Recent SEC filings"
    )
    litigation_risk: Optional[Literal["low", "medium", "high"]] = Field(
        None,
        description="Litigation risk level"
    )
    regulatory_changes: Optional[List[str]] = Field(
        default_factory=list,
        description="Recent regulatory changes affecting the company"
    )
    industry_trend: Optional[str] = Field(None, description="Overall industry trend")


class PredictionReport(BaseModel):
    """Final prediction report from the Predictor agent."""
    
    ticker: str = Field(..., description="Stock ticker symbol")
    recommendation: Literal["BUY", "HOLD", "SELL"] = Field(
        ...,
        description="Final trading recommendation"
    )
    price_target: Optional[float] = Field(
        None,
        description="Predicted price target (optional)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Overall confidence in the prediction (0-100%)"
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        ...,
        description="Risk level of this prediction"
    )
    rationale: str = Field(
        ...,
        description="Comprehensive rationale explaining the prediction"
    )
    contributing_factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Weight of each analysis type in the final decision"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Input analysis reports (for transparency)
    fundamental_score: Optional[float] = None
    technical_score: Optional[float] = None
    sentiment_score: Optional[float] = None
    macro_score: Optional[float] = None
    regulatory_score: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "GOOGL",
                "recommendation": "BUY",
                "price_target": 165.50,
                "confidence": 78.5,
                "risk_level": "MEDIUM",
                "rationale": "Strong fundamentals and positive technical indicators...",
                "contributing_factors": {
                    "fundamental": 0.30,
                    "technical": 0.25,
                    "sentiment": 0.20,
                    "macro": 0.15,
                    "regulatory": 0.10
                },
                "timestamp": "2025-11-21T10:35:00"
            }
        }

