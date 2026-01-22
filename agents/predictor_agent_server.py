"""
Predictor Agent - A2A Server (Port 8006)
Synthesizes all analysis reports and generates final stock prediction.
"""

import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import PREDICTOR_AGENT_PROMPT
from models.simple_predictor import predict as ml_predict

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for prediction synthesis
def ml_model_predict(
    fundamental_report: str,
    technical_report: str,
    sentiment_report: str,
    macro_report: str,
    regulatory_report: str
) -> str:
    """
    Generate ML-based prediction from all analysis reports.
    
    Args:
        fundamental_report: JSON string with fundamental analysis
        technical_report: JSON string with technical analysis
        sentiment_report: JSON string with sentiment analysis
        macro_report: JSON string with macro analysis
        regulatory_report: JSON string with regulatory analysis
    
    Returns:
        JSON string with prediction (recommendation, confidence, risk, rationale)
    """
    try:
        # Parse JSON reports
        fundamental = json.loads(fundamental_report)
        technical = json.loads(technical_report)
        sentiment = json.loads(sentiment_report)
        macro = json.loads(macro_report)
        regulatory = json.loads(regulatory_report)
        
        # Generate prediction
        prediction = ml_predict(
            fundamental, technical, sentiment, macro, regulatory
        )
        
        return json.dumps(prediction, indent=2)
        
    except Exception as e:
        error_result = {
            "error": f"Prediction failed: {str(e)}",
            "recommendation": "HOLD",
            "confidence": 0.0,
            "risk_level": "HIGH"
        }
        return json.dumps(error_result, indent=2)


def calculate_risk(
    fundamental_report: str,
    technical_report: str,
    sentiment_report: str,
    macro_report: str,
    regulatory_report: str
) -> str:
    """
    Calculate risk level based on signal disagreement and confidence.
    
    Args:
        Reports as JSON strings
    
    Returns:
        JSON string with risk assessment
    """
    try:
        import numpy as np
        
        fundamental = json.loads(fundamental_report)
        technical = json.loads(technical_report)
        sentiment = json.loads(sentiment_report)
        macro = json.loads(macro_report)
        regulatory = json.loads(regulatory_report)
        
        signals = [
            fundamental.get("directional_signal", 0),
            technical.get("directional_signal", 0),
            sentiment.get("directional_signal", 0),
            macro.get("directional_signal", 0),
            regulatory.get("directional_signal", 0)
        ]
        
        confidences = [
            fundamental.get("confidence_score", 50),
            technical.get("confidence_score", 50),
            sentiment.get("confidence_score", 50),
            macro.get("confidence_score", 50),
            regulatory.get("confidence_score", 50)
        ]
        
        signal_std = np.std(signals)
        avg_confidence = np.mean(confidences)
        
        if signal_std > 0.6 or avg_confidence < 40:
            risk_level = "HIGH"
        elif signal_std > 0.3 or avg_confidence < 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return json.dumps({
            "risk_level": risk_level,
            "signal_disagreement": round(signal_std, 3),
            "average_confidence": round(avg_confidence, 1),
            "explanation": f"Risk assessed as {risk_level} based on analyst disagreement and confidence levels."
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "risk_level": "UNKNOWN",
            "error": str(e)
        })


# Create the Predictor Agent
predictor_agent = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config, generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.2  # Very low for consistent predictions
    }),
    name="predictor_agent",
    description="Chief prediction synthesizer that generates final stock recommendations. Integrates all analysis reports using ML model and attention-weighted synthesis to produce BUY/HOLD/SELL recommendations with confidence scores and risk assessment.",
    instruction=PREDICTOR_AGENT_PROMPT,
    tools=[ml_model_predict, calculate_risk]
)

# Expose agent via A2A protocol
app = to_a2a(predictor_agent, port=8006)

print("✅ Predictor Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: ml_model_predict, calculate_risk")
print("   Port: 8006")
print("   Ready to serve via A2A protocol...")

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Predictor Agent A2A server on port 8006...")
    print("   Agent card: http://localhost:8006/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")

