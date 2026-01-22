"""
Technical indicators calculator using TA-Lib and Polygon price data.
Calculates RSI, MACD, Moving Averages, Bollinger Bands, etc.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import warnings

# Try to import talib, provide fallback if not available
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    warnings.warn("TA-Lib not available. Using simplified calculations.")

from tools.polygon_fetcher import get_price_history


def calculate_indicators(
    ticker: str,
    days: int = 365,
    timespan: str = "day"
) -> Dict[str, Any]:
    """
    Calculate comprehensive technical indicators for a stock.
    
    Args:
        ticker: Stock symbol
        days: Number of days of historical data
        timespan: 'day', 'week', or 'month'
    
    Returns:
        Dict containing:
        - rsi: Relative Strength Index (14-period)
        - macd: MACD line, signal line, histogram
        - sma_50: 50-period Simple Moving Average
        - sma_200: 200-period Simple Moving Average
        - ema_12: 12-period Exponential Moving Average
        - ema_26: 26-period Exponential Moving Average
        - bollinger_bands: Upper, middle, lower bands
        - trend: Overall trend direction (bullish/bearish/neutral)
        - current_price: Latest closing price
    """
    try:
        # Get price history
        price_data = get_price_history(ticker, days=days, timespan=timespan)
        
        if "error" in price_data or "data" not in price_data:
            return {
                "error": "Could not fetch price data",
                "ticker": ticker
            }
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(price_data["data"])
        
        if len(df) < 50:
            return {
                "error": f"Insufficient data: only {len(df)} periods available",
                "ticker": ticker
            }
        
        # Extract closing prices
        close_prices = np.array(df["close"].values, dtype=float)
        high_prices = np.array(df["high"].values, dtype=float)
        low_prices = np.array(df["low"].values, dtype=float)
        volumes = np.array(df["volume"].values, dtype=float)
        
        indicators = {"ticker": ticker, "timespan": timespan}
        
        if TALIB_AVAILABLE:
            # Use TA-Lib for accurate calculations
            indicators.update(_calculate_with_talib(
                close_prices, high_prices, low_prices, volumes
            ))
        else:
            # Use simplified calculations
            indicators.update(_calculate_simplified(close_prices))
        
        # Determine trend
        indicators["trend"] = _determine_trend(indicators)
        indicators["current_price"] = float(close_prices[-1])
        indicators["price_change_pct"] = float(
            ((close_prices[-1] - close_prices[0]) / close_prices[0]) * 100
        )
        indicators["timestamp"] = datetime.now().isoformat()
        
        return indicators
        
    except Exception as e:
        return {
            "error": f"Error calculating indicators: {str(e)}",
            "ticker": ticker
        }


def _calculate_with_talib(
    close: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    volume: np.ndarray
) -> Dict[str, Any]:
    """Calculate indicators using TA-Lib library."""
    
    indicators = {}
    
    try:
        # RSI (Relative Strength Index)
        rsi = talib.RSI(close, timeperiod=14)
        indicators["rsi"] = float(rsi[-1]) if not np.isnan(rsi[-1]) else None
        
        # MACD (Moving Average Convergence Divergence)
        macd, macd_signal, macd_hist = talib.MACD(
            close, fastperiod=12, slowperiod=26, signalperiod=9
        )
        indicators["macd"] = {
            "macd_line": float(macd[-1]) if not np.isnan(macd[-1]) else None,
            "signal_line": float(macd_signal[-1]) if not np.isnan(macd_signal[-1]) else None,
            "histogram": float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else None
        }
        
        # Moving Averages
        sma_50 = talib.SMA(close, timeperiod=50)
        sma_200 = talib.SMA(close, timeperiod=200)
        ema_12 = talib.EMA(close, timeperiod=12)
        ema_26 = talib.EMA(close, timeperiod=26)
        
        indicators["sma_50"] = float(sma_50[-1]) if not np.isnan(sma_50[-1]) else None
        indicators["sma_200"] = float(sma_200[-1]) if not np.isnan(sma_200[-1]) else None
        indicators["ema_12"] = float(ema_12[-1]) if not np.isnan(ema_12[-1]) else None
        indicators["ema_26"] = float(ema_26[-1]) if not np.isnan(ema_26[-1]) else None
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        indicators["bollinger_bands"] = {
            "upper": float(bb_upper[-1]) if not np.isnan(bb_upper[-1]) else None,
            "middle": float(bb_middle[-1]) if not np.isnan(bb_middle[-1]) else None,
            "lower": float(bb_lower[-1]) if not np.isnan(bb_lower[-1]) else None
        }
        
        # ATR (Average True Range) - Volatility
        atr = talib.ATR(high, low, close, timeperiod=14)
        indicators["atr"] = float(atr[-1]) if not np.isnan(atr[-1]) else None
        
        # Stochastic Oscillator
        slowk, slowd = talib.STOCH(
            high, low, close,
            fastk_period=14, slowk_period=3, slowk_matype=0,
            slowd_period=3, slowd_matype=0
        )
        indicators["stochastic"] = {
            "k": float(slowk[-1]) if not np.isnan(slowk[-1]) else None,
            "d": float(slowd[-1]) if not np.isnan(slowd[-1]) else None
        }
        
        # OBV (On-Balance Volume)
        obv = talib.OBV(close, volume)
        indicators["obv"] = float(obv[-1]) if not np.isnan(obv[-1]) else None
        
    except Exception as e:
        print(f"Error in TA-Lib calculations: {e}")
    
    return indicators


def _calculate_simplified(close: np.ndarray) -> Dict[str, Any]:
    """Simplified indicator calculations without TA-Lib."""
    
    indicators = {}
    
    try:
        # RSI (simplified)
        rsi = _simple_rsi(close, period=14)
        indicators["rsi"] = float(rsi)
        
        # Simple Moving Averages
        if len(close) >= 50:
            indicators["sma_50"] = float(np.mean(close[-50:]))
        if len(close) >= 200:
            indicators["sma_200"] = float(np.mean(close[-200:]))
        
        # Exponential Moving Averages (simplified)
        indicators["ema_12"] = float(_simple_ema(close, 12))
        indicators["ema_26"] = float(_simple_ema(close, 26))
        
        # MACD (simplified)
        ema_12 = _simple_ema(close, 12)
        ema_26 = _simple_ema(close, 26)
        macd_line = ema_12 - ema_26
        
        indicators["macd"] = {
            "macd_line": float(macd_line),
            "signal_line": None,  # Would need more calculation
            "histogram": None
        }
        
        # Bollinger Bands (simplified)
        sma_20 = np.mean(close[-20:])
        std_20 = np.std(close[-20:])
        indicators["bollinger_bands"] = {
            "upper": float(sma_20 + 2 * std_20),
            "middle": float(sma_20),
            "lower": float(sma_20 - 2 * std_20)
        }
        
    except Exception as e:
        print(f"Error in simplified calculations: {e}")
    
    return indicators


def _simple_rsi(prices: np.ndarray, period: int = 14) -> float:
    """Calculate RSI without TA-Lib."""
    deltas = np.diff(prices)
    
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def _simple_ema(prices: np.ndarray, period: int) -> float:
    """Calculate EMA without TA-Lib."""
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema


def _determine_trend(indicators: Dict[str, Any]) -> str:
    """
    Determine overall trend based on multiple indicators.
    
    Returns:
        'bullish', 'bearish', or 'neutral'
    """
    bullish_signals = 0
    bearish_signals = 0
    
    # Check RSI
    rsi = indicators.get("rsi")
    if rsi:
        if rsi > 50:
            bullish_signals += 1
        elif rsi < 50:
            bearish_signals += 1
    
    # Check MACD
    macd = indicators.get("macd", {})
    if macd.get("macd_line") and macd.get("signal_line"):
        if macd["macd_line"] > macd["signal_line"]:
            bullish_signals += 1
        else:
            bearish_signals += 1
    
    # Check Moving Averages (Golden/Death Cross)
    sma_50 = indicators.get("sma_50")
    sma_200 = indicators.get("sma_200")
    current_price = indicators.get("current_price")
    
    if sma_50 and sma_200:
        if sma_50 > sma_200:  # Golden cross
            bullish_signals += 2  # Weight this more
        else:  # Death cross
            bearish_signals += 2
    
    if current_price and sma_50:
        if current_price > sma_50:
            bullish_signals += 1
        else:
            bearish_signals += 1
    
    # Determine trend
    if bullish_signals > bearish_signals + 1:
        return "bullish"
    elif bearish_signals > bullish_signals + 1:
        return "bearish"
    else:
        return "neutral"


def get_support_resistance(ticker: str, days: int = 180) -> Dict[str, Any]:
    """
    Identify key support and resistance levels.
    
    Args:
        ticker: Stock symbol
        days: Number of days to analyze
    
    Returns:
        Dict with support and resistance levels
    """
    try:
        price_data = get_price_history(ticker, days=days)
        
        if "error" in price_data or "data" not in price_data:
            return {"error": "Could not fetch price data"}
        
        df = pd.DataFrame(price_data["data"])
        highs = df["high"].values
        lows = df["low"].values
        
        # Simple approach: find recent peaks and troughs
        resistance = float(np.max(highs[-90:]))  # Last 90 days high
        support = float(np.min(lows[-90:]))  # Last 90 days low
        
        current_price = float(df["close"].iloc[-1])
        
        return {
            "ticker": ticker,
            "resistance": resistance,
            "support": support,
            "current_price": current_price,
            "distance_to_resistance_pct": ((resistance - current_price) / current_price) * 100,
            "distance_to_support_pct": ((current_price - support) / current_price) * 100
        }
        
    except Exception as e:
        return {"error": f"Error calculating support/resistance: {str(e)}"}


# Test function
if __name__ == "__main__":
    ticker = "AAPL"
    
    print(f"Calculating technical indicators for {ticker}...")
    indicators = calculate_indicators(ticker, days=365)
    
    print(f"\nRSI: {indicators.get('rsi')}")
    print(f"Trend: {indicators.get('trend')}")
    print(f"SMA 50: {indicators.get('sma_50')}")
    print(f"SMA 200: {indicators.get('sma_200')}")
    
    print(f"\nSupport/Resistance:")
    sr = get_support_resistance(ticker)
    print(f"Support: ${sr.get('support'):.2f}")
    print(f"Resistance: ${sr.get('resistance'):.2f}")

