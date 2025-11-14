"""
AI 3D Signal Panel - Real-time Trading Signals Generator
Integrates with Stock AI Platform for 3D Visualization
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ API keys loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables.")


class AI3DSignalPanel:
    """
    AI-powered signal generation for 3D Trading Dashboard
    Generates buy/sell/hold signals with confidence scores
    """

    def __init__(self):
        self.signals = []
        self.fear_greed_index = {"fear": 50, "greed": 50}
        self.market_sentiment = "NEUTRAL"
        self.signal_history = []

        # Load API keys
        self.polygon_api_key = os.getenv('POLYGON_API_KEY')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')

        # API availability status
        self.has_polygon = bool(self.polygon_api_key)
        self.has_alpha_vantage = bool(self.alpha_vantage_key)
        self.has_finnhub = bool(self.finnhub_key)
        self.has_news_api = bool(self.news_api_key)

        if self.has_polygon:
            st.info(f"✅ Polygon.io API connected - Real-time data enabled")
        if self.has_finnhub:
            st.info(f"✅ Finnhub API connected - Advanced analysis enabled")
        if self.has_alpha_vantage:
            st.info(f"✅ Alpha Vantage API connected - Technical indicators enabled")

    def _fetch_polygon_data(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time data from Polygon.io API"""
        if not self.has_polygon:
            return None

        try:
            import requests

            # Get latest quote
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/prev?adjusted=true&apiKey={self.polygon_api_key}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    result = data['results'][0]
                    return {
                        'symbol': symbol,
                        'open': result.get('o'),
                        'high': result.get('h'),
                        'low': result.get('l'),
                        'close': result.get('c'),
                        'volume': result.get('v'),
                        'source': 'polygon'
                    }
        except Exception as e:
            print(f"Polygon API error for {symbol}: {e}")

        return None

    def _fetch_finnhub_data(self, symbol: str) -> Optional[Dict]:
        """Fetch real-time data from Finnhub API"""
        if not self.has_finnhub:
            return None

        try:
            import requests

            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'symbol': symbol,
                    'current': data.get('c'),
                    'high': data.get('h'),
                    'low': data.get('l'),
                    'open': data.get('o'),
                    'previous_close': data.get('pc'),
                    'source': 'finnhub'
                }
        except Exception as e:
            print(f"Finnhub API error for {symbol}: {e}")

        return None

    def generate_ai_signals(
        self, symbols: List[str], timeframe: str = "1d"
    ) -> List[Dict]:
        """
        Generate AI trading signals for given symbols

        Args:
            symbols: List of stock symbols (e.g., ['AAPL', 'TSLA', 'NVDA'])
            timeframe: Data timeframe ('1d', '1h', '5m')

        Returns:
            List of signal dictionaries with action, confidence, and targets
        """
        signals = []

        for symbol in symbols:
            try:
                # Try Polygon API first (most reliable)
                polygon_data = self._fetch_polygon_data(symbol)

                # Try Finnhub API as backup
                finnhub_data = self._fetch_finnhub_data(symbol)

                # Fallback to yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="3mo", interval=timeframe)

                if hist.empty or len(hist) < 20:
                    # Try using API data if yfinance fails
                    if polygon_data or finnhub_data:
                        st.info(f"📡 Using API data for {symbol}")
                    else:
                        continue

                # Get current info
                info = ticker.info
                current_price = hist["Close"].iloc[-1] if not hist.empty else (
                    polygon_data.get('close') if polygon_data else
                    finnhub_data.get('current') if finnhub_data else 0
                )

                if current_price == 0:
                    continue

                # Enrich with API data
                if polygon_data:
                    info['volume'] = polygon_data.get('volume', info.get('volume', 0))

                # Generate signal using AI analysis
                signal = self._analyze_and_generate_signal(
                    symbol, hist, info, current_price
                )

                if signal:
                    # Add data source info
                    if polygon_data:
                        signal['data_source'] = 'Polygon.io (Real-time)'
                    elif finnhub_data:
                        signal['data_source'] = 'Finnhub (Real-time)'
                    else:
                        signal['data_source'] = 'Yahoo Finance'

                    signals.append(signal)

            except Exception as e:
                st.warning(f"⚠️ Error analyzing {symbol}: {str(e)}")
                continue

        self.signals = signals
        return signals

    def _analyze_and_generate_signal(
        self, symbol: str, hist: pd.DataFrame, info: Dict, current_price: float
    ) -> Optional[Dict]:
        """
        Advanced AI analysis to generate trading signal

        Uses multiple indicators:
        - Moving Averages (SMA, EMA)
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Volume Analysis
        - Price Action Patterns
        """

        try:
            closes = hist["Close"]
            volumes = hist["Volume"]

            # === TECHNICAL INDICATORS ===

            # Moving Averages
            sma_20 = closes.rolling(window=20).mean().iloc[-1]
            sma_50 = closes.rolling(window=50).mean().iloc[-1] if len(closes) >= 50 else sma_20
            ema_12 = closes.ewm(span=12, adjust=False).mean().iloc[-1]
            ema_26 = closes.ewm(span=26, adjust=False).mean().iloc[-1]

            # RSI Calculation
            rsi = self._calculate_rsi(closes)

            # MACD
            macd = ema_12 - ema_26
            signal_line = closes.ewm(span=9, adjust=False).mean().iloc[-1]
            macd_histogram = macd - signal_line

            # Volume Analysis
            avg_volume = volumes.rolling(window=20).mean().iloc[-1]
            current_volume = volumes.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            # Price Momentum
            price_change_1d = (
                (current_price - closes.iloc[-2]) / closes.iloc[-2] * 100
            )
            price_change_5d = (
                (current_price - closes.iloc[-6]) / closes.iloc[-6] * 100
                if len(closes) >= 6
                else 0
            )
            price_change_20d = (
                (current_price - closes.iloc[-21]) / closes.iloc[-21] * 100
                if len(closes) >= 21
                else 0
            )

            # === AI SCORING SYSTEM ===

            buy_score = 0
            sell_score = 0

            # 1. Moving Average Signals
            if current_price > sma_20:
                buy_score += 15
            else:
                sell_score += 10

            if current_price > sma_50:
                buy_score += 10
            else:
                sell_score += 8

            # Golden Cross / Death Cross
            if sma_20 > sma_50:
                buy_score += 15
            elif sma_20 < sma_50:
                sell_score += 15

            # 2. RSI Signals
            if rsi < 30:  # Oversold - potential buy
                buy_score += 20
            elif rsi > 70:  # Overbought - potential sell
                sell_score += 20
            elif 40 < rsi < 60:  # Neutral zone
                buy_score += 5
                sell_score += 5

            # 3. MACD Signals
            if macd_histogram > 0:  # Bullish momentum
                buy_score += 12
            else:  # Bearish momentum
                sell_score += 12

            # 4. Volume Confirmation
            if volume_ratio > 1.5:  # High volume
                if price_change_1d > 0:
                    buy_score += 15
                else:
                    sell_score += 15

            # 5. Price Momentum
            if price_change_5d > 5:  # Strong uptrend
                buy_score += 10
            elif price_change_5d < -5:  # Strong downtrend
                sell_score += 10

            if price_change_20d > 15:
                buy_score += 8
            elif price_change_20d < -15:
                sell_score += 8

            # === DETERMINE ACTION ===

            total_score = buy_score + sell_score
            if total_score == 0:
                total_score = 1  # Avoid division by zero

            buy_confidence = int((buy_score / total_score) * 100)
            sell_confidence = int((sell_score / total_score) * 100)

            # Decision logic
            if buy_confidence >= 65:
                action = "BUY"
                confidence = buy_confidence
                target_price = current_price * 1.10  # 10% upside target
            elif sell_confidence >= 65:
                action = "SELL"
                confidence = sell_confidence
                target_price = current_price * 0.90  # 10% downside target
            else:
                action = "HOLD"
                confidence = max(buy_confidence, sell_confidence)
                target_price = current_price * 1.02  # 2% neutral target

            # === CREATE SIGNAL ===

            signal = {
                "symbol": symbol,
                "action": action,
                "confidence": confidence,
                "price": round(current_price, 2),
                "target": round(target_price, 2),
                "rsi": round(rsi, 2),
                "volume_ratio": round(volume_ratio, 2),
                "price_change_1d": round(price_change_1d, 2),
                "price_change_5d": round(price_change_5d, 2),
                "timestamp": datetime.now().isoformat(),
                "indicators": {
                    "sma_20": round(sma_20, 2),
                    "sma_50": round(sma_50, 2),
                    "macd": round(macd, 4),
                    "buy_score": buy_score,
                    "sell_score": sell_score,
                },
            }

            return signal

        except Exception as e:
            st.error(f"❌ Signal analysis error for {symbol}: {str(e)}")
            return None

    def _calculate_rsi(
        self, prices: pd.Series, period: int = 14
    ) -> float:
        """
        Calculate Relative Strength Index (RSI)

        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        """
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0)
        loss = -deltas.where(deltas < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0

    def calculate_fear_greed_index(self, market_data: Dict) -> Dict[str, int]:
        """
        Calculate Fear & Greed Index based on market conditions

        Factors:
        - Market momentum (S&P 500 performance)
        - Stock price breadth (advancing vs declining stocks)
        - Put/Call ratio
        - Volatility (VIX)
        - Safe haven demand
        """

        try:
            # Simplified Fear & Greed calculation
            # In production, use real VIX, put/call ratios, etc.

            fear_score = 50
            greed_score = 50

            # Sample calculation based on signals
            buy_signals = sum(1 for s in self.signals if s["action"] == "BUY")
            sell_signals = sum(1 for s in self.signals if s["action"] == "SELL")
            total_signals = len(self.signals) if self.signals else 1

            buy_ratio = (buy_signals / total_signals) * 100
            sell_ratio = (sell_signals / total_signals) * 100

            # Adjust Fear/Greed based on market signals
            if buy_ratio > 60:
                greed_score = int(50 + (buy_ratio - 50))
                fear_score = 100 - greed_score
                self.market_sentiment = "GREEDY"
            elif sell_ratio > 60:
                fear_score = int(50 + (sell_ratio - 50))
                greed_score = 100 - fear_score
                self.market_sentiment = "FEARFUL"
            else:
                self.market_sentiment = "NEUTRAL"

            self.fear_greed_index = {"fear": fear_score, "greed": greed_score}

            return self.fear_greed_index

        except Exception as e:
            st.error(f"❌ Fear/Greed calculation error: {str(e)}")
            return {"fear": 50, "greed": 50}

    def get_top_signals(self, limit: int = 10, min_confidence: int = 70) -> List[Dict]:
        """
        Get top signals filtered by confidence threshold

        Args:
            limit: Maximum number of signals to return
            min_confidence: Minimum confidence score (0-100)

        Returns:
            List of top signals sorted by confidence
        """
        filtered = [s for s in self.signals if s["confidence"] >= min_confidence]
        sorted_signals = sorted(
            filtered, key=lambda x: x["confidence"], reverse=True
        )
        return sorted_signals[:limit]

    def export_signals_json(self) -> str:
        """
        Export signals as JSON for 3D dashboard consumption

        Returns:
            JSON string of signals and market data
        """
        data = {
            "signals": self.signals,
            "fear_greed": self.fear_greed_index,
            "market_sentiment": self.market_sentiment,
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(self.signals),
        }

        return json.dumps(data, indent=2)

    def render_3d_dashboard(self, signals_data: Optional[List[Dict]] = None):
        """
        Render 3D Trading Dashboard in Streamlit

        Args:
            signals_data: Optional pre-generated signals, otherwise uses self.signals
        """

        if signals_data is None:
            signals_data = self.signals

        # Read HTML template
        html_file = Path(__file__).parent / "templates" / "trading_3d_dashboard.html"

        if not html_file.exists():
            st.error("❌ 3D Dashboard template not found!")
            return

        # Read HTML content
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inject signals data into HTML
        signals_json = json.dumps(signals_data)
        fear_greed_json = json.dumps(self.fear_greed_index)

        # Replace placeholder data in HTML
        html_content = html_content.replace(
            "let aiSignals = [",
            f"let aiSignals = {signals_json}; let oldSignals = ["
        )

        html_content = html_content.replace(
            "updateSentiment(45, 55)",
            f"updateSentiment({self.fear_greed_index['fear']}, {self.fear_greed_index['greed']})"
        )

        # Render in Streamlit
        components.html(html_content, height=800, scrolling=False)


# === CONVENIENCE FUNCTIONS ===


def create_3d_signal_panel(
    symbols: List[str] = None, timeframe: str = "1d"
) -> AI3DSignalPanel:
    """
    Factory function to create and initialize 3D Signal Panel

    Args:
        symbols: Stock symbols to analyze
        timeframe: Data timeframe

    Returns:
        Initialized AI3DSignalPanel instance
    """

    if symbols is None:
        symbols = ["AAPL", "TSLA", "NVDA", "META", "GOOGL", "AMZN", "MSFT"]

    panel = AI3DSignalPanel()
    panel.generate_ai_signals(symbols, timeframe)
    panel.calculate_fear_greed_index({})

    return panel


def display_3d_signals_streamlit(symbols: List[str] = None):
    """
    Streamlit component to display 3D signals dashboard

    Usage in Streamlit app:
        from ai_3d_signal_panel import display_3d_signals_streamlit
        display_3d_signals_streamlit(['AAPL', 'TSLA', 'NVDA'])
    """

    st.title("🎯 AI 3D Trading Signals Dashboard")

    # Initialize panel
    with st.spinner("🤖 Generating AI signals..."):
        panel = create_3d_signal_panel(symbols)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_signals = len(panel.signals)
        st.metric("📊 Total Signals", total_signals)

    with col2:
        buy_signals = sum(1 for s in panel.signals if s["action"] == "BUY")
        st.metric("🟢 Buy Signals", buy_signals)

    with col3:
        sell_signals = sum(1 for s in panel.signals if s["action"] == "SELL")
        st.metric("🔴 Sell Signals", sell_signals)

    with col4:
        st.metric("😨 Fear", f"{panel.fear_greed_index['fear']}%")

    st.markdown("---")

    # Render 3D Dashboard
    panel.render_3d_dashboard()

    # Display signal details table
    st.markdown("---")
    st.subheader("📋 Signal Details")

    if panel.signals:
        df = pd.DataFrame(panel.signals)
        st.dataframe(
            df[["symbol", "action", "confidence", "price", "target", "rsi", "volume_ratio"]],
            use_container_width=True
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Signals CSV",
            data=csv,
            file_name=f"ai_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ No signals generated. Try different symbols or timeframe.")


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    # Testing the AI 3D Signal Panel
    print("🤖 AI 3D Signal Panel - Testing Mode\n")

    # Create panel
    panel = AI3DSignalPanel()

    # Generate signals
    test_symbols = ["AAPL", "TSLA", "NVDA", "META", "GOOGL"]
    print(f"📊 Analyzing {len(test_symbols)} stocks...\n")

    signals = panel.generate_ai_signals(test_symbols)

    # Display results
    print(f"✅ Generated {len(signals)} signals:\n")
    for signal in signals:
        print(
            f"  {signal['symbol']:<6} | {signal['action']:<5} | "
            f"Confidence: {signal['confidence']:>3}% | "
            f"Price: ${signal['price']:>7.2f} → ${signal['target']:>7.2f}"
        )

    # Calculate Fear/Greed
    print("\n" + "=" * 60)
    fg = panel.calculate_fear_greed_index({})
    print(f"😨 Fear Index: {fg['fear']}%")
    print(f"😃 Greed Index: {fg['greed']}%")
    print(f"📊 Market Sentiment: {panel.market_sentiment}")

    # Export JSON
    print("\n" + "=" * 60)
    print("📄 Exported JSON:")
    print(panel.export_signals_json())
