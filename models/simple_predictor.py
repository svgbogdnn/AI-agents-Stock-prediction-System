"""
Simple ML prediction model using XGBoost.
Converts 5 analysis reports into features and generates BUY/HOLD/SELL recommendation.
"""

import numpy as np
from typing import Dict, List, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("Warning: XGBoost not available. Using rule-based fallback.")


class StockPredictor:
    """
    Simple stock prediction model.
    For the capstone, we'll use a rule-based approach with attention weighting
    since we don't have historical training data readily available.
    """
    
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    def predict_from_reports(
        self,
        fundamental_report: Dict[str, Any],
        technical_report: Dict[str, Any],
        sentiment_report: Dict[str, Any],
        macro_report: Dict[str, Any],
        regulatory_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate prediction from analysis reports using attention-weighted synthesis.
        
        Args:
            fundamental_report: Fundamental analysis
            technical_report: Technical analysis
            sentiment_report: Sentiment analysis
            macro_report: Macro analysis
            regulatory_report: Regulatory analysis
        
        Returns:
            Dict with recommendation, confidence, risk_level, and rationale
        """
        # Extract signals and confidence scores
        signals = {
            "fundamental": (
                fundamental_report.get("directional_signal", 0.0),
                fundamental_report.get("confidence_score", 50.0)
            ),
            "technical": (
                technical_report.get("directional_signal", 0.0),
                technical_report.get("confidence_score", 50.0)
            ),
            "sentiment": (
                sentiment_report.get("directional_signal", 0.0),
                sentiment_report.get("confidence_score", 50.0)
            ),
            "macro": (
                macro_report.get("directional_signal", 0.0),
                macro_report.get("confidence_score", 50.0)
            ),
            "regulatory": (
                regulatory_report.get("directional_signal", 0.0),
                regulatory_report.get("confidence_score", 50.0)
            )
        }
        
        # Calculate attention-weighted aggregate signal
        weighted_signal, overall_confidence, weights = self._calculate_weighted_signal(signals)
        
        # Generate recommendation
        recommendation = self._signal_to_recommendation(weighted_signal)
        
        # Assess risk level
        risk_level = self._assess_risk(signals, weighted_signal)
        
        # Generate rationale
        rationale = self._generate_rationale(
            signals, weights, weighted_signal, recommendation
        )
        
        # Calculate price target (simplified)
        price_target = self._estimate_price_target(
            fundamental_report, technical_report, weighted_signal
        )
        
        return {
            "recommendation": recommendation,
            "price_target": price_target,
            "confidence": round(overall_confidence, 1),
            "risk_level": risk_level,
            "rationale": rationale,
            "contributing_factors": {
                "fundamental": round(weights["fundamental"], 3),
                "technical": round(weights["technical"], 3),
                "sentiment": round(weights["sentiment"], 3),
                "macro": round(weights["macro"], 3),
                "regulatory": round(weights["regulatory"], 3)
            },
            "fundamental_score": round(signals["fundamental"][0], 2),
            "technical_score": round(signals["technical"][0], 2),
            "sentiment_score": round(signals["sentiment"][0], 2),
            "macro_score": round(signals["macro"][0], 2),
            "regulatory_score": round(signals["regulatory"][0], 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_weighted_signal(
        self,
        signals: Dict[str, tuple]
    ) -> tuple[float, float, Dict[str, float]]:
        """
        Calculate attention-weighted aggregate signal.
        Higher confidence reports get higher weight.
        
        Returns:
            (weighted_signal, overall_confidence, weights)
        """
        total_weight = 0.0
        weighted_sum = 0.0
        confidence_sum = 0.0
        
        # Base weights (can be adjusted based on market conditions)
        base_weights = {
            "fundamental": 0.30,  # Emphasis on fundamentals
            "technical": 0.25,    # Technical momentum
            "sentiment": 0.20,    # Market sentiment
            "macro": 0.15,        # Economic conditions
            "regulatory": 0.10    # Legal/regulatory risks
        }
        
        final_weights = {}
        
        for key, (signal, confidence) in signals.items():
            # Confidence-based weighting (0-100 scale)
            confidence_weight = confidence / 100.0
            
            # Combine base weight with confidence
            weight = base_weights[key] * (0.5 + 0.5 * confidence_weight)
            
            final_weights[key] = weight
            total_weight += weight
            weighted_sum += signal * weight
            confidence_sum += confidence * base_weights[key]
        
        # Normalize weights
        if total_weight > 0:
            for key in final_weights:
                final_weights[key] /= total_weight
            weighted_signal = weighted_sum / total_weight
        else:
            weighted_signal = 0.0
        
        overall_confidence = confidence_sum
        
        return weighted_signal, overall_confidence, final_weights
    
    def _signal_to_recommendation(self, signal: float) -> str:
        """
        Convert aggregated signal to BUY/HOLD/SELL recommendation.
        
        Signal ranges:
        - > 0.5: Strong buy
        - 0.2 to 0.5: Buy
        - -0.2 to 0.2: Hold
        - -0.5 to -0.2: Sell
        - < -0.5: Strong sell
        """
        if signal > 0.3:
            return "BUY"
        elif signal < -0.3:
            return "SELL"
        else:
            return "HOLD"
    
    def _assess_risk(
        self,
        signals: Dict[str, tuple],
        weighted_signal: float
    ) -> str:
        """
        Assess risk level based on signal disagreement and market conditions.
        
        Returns:
            'LOW', 'MEDIUM', or 'HIGH'
        """
        # Calculate signal variance (disagreement between analysts)
        signal_values = [s[0] for s in signals.values()]
        signal_std = np.std(signal_values)
        
        # Calculate average confidence
        avg_confidence = np.mean([s[1] for s in signals.values()])
        
        # High risk if:
        # - Signals strongly disagree (high std)
        # - Low average confidence
        # - Extreme weighted signal (could be overextended)
        
        if signal_std > 0.6 or avg_confidence < 40:
            return "HIGH"
        elif signal_std > 0.3 or avg_confidence < 60 or abs(weighted_signal) > 0.8:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_rationale(
        self,
        signals: Dict[str, tuple],
        weights: Dict[str, float],
        weighted_signal: float,
        recommendation: str
    ) -> str:
        """Generate human-readable rationale for the prediction."""
        
        rationale_parts = [
            f"Recommendation: {recommendation} (Signal: {weighted_signal:.2f})\n"
        ]
        
        # Identify strongest signals
        sorted_signals = sorted(
            signals.items(),
            key=lambda x: abs(x[1][0]),
            reverse=True
        )
        
        rationale_parts.append("Key Factors:")
        
        for i, (key, (signal, confidence)) in enumerate(sorted_signals[:3], 1):
            direction = "positive" if signal > 0 else "negative" if signal < 0 else "neutral"
            rationale_parts.append(
                f"{i}. {key.title()} ({direction}, confidence: {confidence:.1f}%, weight: {weights[key]:.1%})"
            )
        
        # Add consensus/disagreement note
        signal_values = [s[0] for s in signals.values()]
        if np.std(signal_values) > 0.5:
            rationale_parts.append(
                "\nNote: Analysts show significant disagreement, suggesting higher uncertainty."
            )
        elif all(s > 0.2 for s in signal_values) or all(s < -0.2 for s in signal_values):
            rationale_parts.append(
                "\nNote: Strong consensus across all analysts."
            )
        
        return " ".join(rationale_parts)
    
    def _estimate_price_target(
        self,
        fundamental_report: Dict[str, Any],
        technical_report: Dict[str, Any],
        weighted_signal: float
    ) -> float:
        """
        Estimate price target based on current price and signal.
        This is a simplified approach for demonstration.
        """
        # Try to get current price from reports
        current_price = None
        
        if "current_price" in fundamental_report.get("key_metrics", {}):
            current_price = fundamental_report["key_metrics"]["current_price"]
        elif "current_price" in technical_report.get("key_metrics", {}):
            current_price = technical_report["key_metrics"]["current_price"]
        
        if not current_price:
            return None  # Can't estimate without current price
        
        # Simple target: adjust current price by signal magnitude
        # Signal range -1 to 1 → adjust by -20% to +20%
        adjustment = weighted_signal * 0.20
        price_target = current_price * (1 + adjustment)
        
        return round(price_target, 2)


# Helper functions for use in agent tools
def predict(
    fundamental: Dict,
    technical: Dict,
    sentiment: Dict,
    macro: Dict,
    regulatory: Dict
) -> Dict[str, Any]:
    """
    Main prediction function to be called by the Predictor agent.
    
    Args:
        fundamental, technical, sentiment, macro, regulatory: Analysis reports
    
    Returns:
        Prediction dict with recommendation, confidence, risk, and rationale
    """
    predictor = StockPredictor()
    return predictor.predict_from_reports(
        fundamental, technical, sentiment, macro, regulatory
    )


# Test function
if __name__ == "__main__":
    # Mock reports for testing
    mock_fundamental = {
        "directional_signal": 0.6,
        "confidence_score": 75.0,
        "key_metrics": {"current_price": 150.0}
    }
    
    mock_technical = {
        "directional_signal": 0.4,
        "confidence_score": 80.0,
        "key_metrics": {"current_price": 150.0}
    }
    
    mock_sentiment = {
        "directional_signal": 0.3,
        "confidence_score": 65.0,
        "key_metrics": {}
    }
    
    mock_macro = {
        "directional_signal": -0.2,
        "confidence_score": 70.0,
        "key_metrics": {}
    }
    
    mock_regulatory = {
        "directional_signal": 0.1,
        "confidence_score": 60.0,
        "key_metrics": {}
    }
    
    print("Testing Simple Predictor...")
    result = predict(
        mock_fundamental,
        mock_technical,
        mock_sentiment,
        mock_macro,
        mock_regulatory
    )
    
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Price Target: ${result['price_target']}")
    print(f"\nRationale:\n{result['rationale']}")
    print(f"\nContributing Factors:")
    for factor, weight in result['contributing_factors'].items():
        print(f"  {factor}: {weight:.1%}")

