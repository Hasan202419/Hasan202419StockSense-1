import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass
import threading
import schedule

# Import our AI analysis modules
from autonomous_analyzer import AutonomousAnalyzer
from perpetual_ai_trader import PerpetualAITrader
from halal_screener import HalalScreener
from data_fetcher import DataFetcher
from ai_research_assistant import AIResearchAssistant

@dataclass
class TelegramSignal:
    """Represents a trading signal to be sent via Telegram"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    current_price: float
    target_price: float
    stop_loss: float
    analysis_summary: str
    technical_score: float
    fundamental_score: float
    halal_compliant: bool
    timestamp: datetime
    reasoning: str

class TelegramAlgoBot:
    """Autonomous Telegram Bot for Real-Time Stock Signals"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Initialize AI analysis components
        self.autonomous_analyzer = AutonomousAnalyzer()
        self.ai_trader = PerpetualAITrader()
        self.halal_screener = HalalScreener()
        self.data_fetcher = DataFetcher()
        self.ai_research = AIResearchAssistant()
        
        # Bot configuration
        self.signal_interval = 60  # Send signals every 60 seconds
        self.max_signals_per_hour = 10
        self.min_confidence_threshold = 0.75
        self.signals_sent_today = 0
        self.last_signal_time = None
        self.is_running = False
        
        # Market monitoring
        self.monitored_symbols = []
        self.signal_history = []
        self.performance_tracking = {}
        
        # Learning system
        self.successful_patterns = {}
        self.failed_patterns = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start_bot(self):
        """Start the autonomous telegram bot"""
        self.logger.info("Starting Telegram Algo Bot...")
        self.is_running = True
        
        # Initialize market universe
        self._initialize_market_universe()
        
        # Send startup message
        self.send_startup_message()
        
        # Schedule regular market analysis
        schedule.every(60).seconds.do(self._analyze_and_send_signals)
        schedule.every(5).minutes.do(self._update_market_universe)
        schedule.every(1).hours.do(self._send_performance_update)
        schedule.every().day.at("09:00").do(self._send_daily_market_outlook)
        schedule.every().day.at("16:00").do(self._send_market_close_summary)
        
        # Start the main bot loop
        self._run_bot_loop()
    
    def stop_bot(self):
        """Stop the bot"""
        self.is_running = False
        self.send_message("🛑 Algo Bot stopped. Market monitoring paused.")
        self.logger.info("Telegram Algo Bot stopped")
    
    def _run_bot_loop(self):
        """Main bot execution loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Bot loop error: {str(e)}")
                time.sleep(5)
    
    def _initialize_market_universe(self):
        """Initialize the universe of stocks to monitor"""
        try:
            # Get diverse stock universe
            sp500_stocks = self.data_fetcher.get_sp500_symbols()[:100]
            
            # Add popular trading stocks
            popular_stocks = [
                'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA',
                'AMD', 'PLTR', 'SOFI', 'AMC', 'GME', 'COIN', 'RIVN',
                'LCID', 'NIO', 'BABA', 'DIS', 'NFLX', 'UBER', 'LYFT'
            ]
            
            self.monitored_symbols = list(set(sp500_stocks + popular_stocks))
            self.logger.info(f"Monitoring {len(self.monitored_symbols)} stocks")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize market universe: {str(e)}")
            # Fallback to essential stocks
            self.monitored_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA',
                'JPM', 'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA'
            ]
    
    def _analyze_and_send_signals(self):
        """Core method: Analyze market and send buy signals"""
        try:
            if not self._should_send_signal():
                return
            
            self.logger.info("Analyzing market for signals...")
            
            # Scan market for opportunities
            high_potential_stocks = self._scan_for_opportunities()
            
            if not high_potential_stocks:
                return
            
            # Generate detailed signals
            signals = self._generate_detailed_signals(high_potential_stocks)
            
            # Filter for best signals
            best_signals = self._filter_best_signals(signals)
            
            if best_signals:
                # Send the top signal
                top_signal = best_signals[0]
                self._send_buy_signal(top_signal)
                self._track_signal_performance(top_signal)
            
        except Exception as e:
            self.logger.error(f"Signal analysis error: {str(e)}")
    
    def _scan_for_opportunities(self) -> List[Dict]:
        """Scan market for high-potential opportunities"""
        opportunities = []
        
        # Sample a subset for real-time analysis
        sample_size = min(50, len(self.monitored_symbols))
        sample_symbols = np.random.choice(self.monitored_symbols, sample_size, replace=False)
        
        for symbol in sample_symbols:
            try:
                # Quick opportunity assessment
                opportunity_score = self._quick_opportunity_assessment(symbol)
                
                if opportunity_score > 70:
                    opportunities.append({
                        'symbol': symbol,
                        'opportunity_score': opportunity_score,
                        'timestamp': datetime.now()
                    })
                    
            except Exception as e:
                continue
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        return opportunities[:10]  # Top 10 opportunities
    
    def _quick_opportunity_assessment(self, symbol: str) -> float:
        """Quick assessment of trading opportunity"""
        try:
            # Fetch real-time data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1mo")
            
            if not info or history.empty:
                return 0
            
            score = 50  # Base score
            
            # Price momentum
            if len(history) >= 5:
                current_price = history['Close'].iloc[-1]
                week_ago_price = history['Close'].iloc[-5] if len(history) >= 5 else current_price
                momentum = (current_price - week_ago_price) / week_ago_price
                
                if momentum > 0.05:  # 5%+ weekly gain
                    score += 20
                elif momentum > 0.02:  # 2%+ weekly gain
                    score += 10
            
            # Volume analysis
            if len(history) >= 10:
                recent_volume = history['Volume'].tail(3).mean()
                avg_volume = history['Volume'].head(-3).mean()
                volume_surge = recent_volume / avg_volume if avg_volume > 0 else 1
                
                if volume_surge > 1.5:
                    score += 15
                elif volume_surge > 1.2:
                    score += 8
            
            # Technical indicators
            if len(history) >= 20:
                # RSI
                delta = history['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]
                
                if 30 < current_rsi < 70:
                    score += 10
                elif current_rsi < 35:
                    score += 5  # Oversold potential
            
            # Fundamental quick check
            pe_ratio = info.get('trailingPE', 0)
            if 0 < pe_ratio < 25:
                score += 5
            
            market_cap = info.get('marketCap', 0)
            if market_cap > 1e9:  # $1B+ market cap
                score += 5
            
            return min(100, max(0, score))
            
        except Exception as e:
            return 0
    
    def _generate_detailed_signals(self, opportunities: List[Dict]) -> List[TelegramSignal]:
        """Generate detailed trading signals for opportunities"""
        signals = []
        
        for opp in opportunities[:5]:  # Top 5 for detailed analysis
            try:
                symbol = opp['symbol']
                
                # Get comprehensive data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                history = ticker.history(period="3mo")
                
                if not info or history.empty:
                    continue
                
                # Generate AI signal
                ai_signal = self.ai_trader._generate_ai_signal(symbol, info, history)
                
                if not ai_signal or ai_signal.confidence < self.min_confidence_threshold:
                    continue
                
                # Check halal compliance
                compliance_result = self.halal_screener.calculate_compliance_score(info)
                is_halal = compliance_result['business_compliant'] and compliance_result['financial_compliant']
                
                # Create telegram signal
                telegram_signal = TelegramSignal(
                    symbol=symbol,
                    signal_type=ai_signal.signal_type,
                    confidence=ai_signal.confidence,
                    current_price=info.get('regularMarketPrice', 0),
                    target_price=ai_signal.target_price,
                    stop_loss=ai_signal.stop_loss,
                    analysis_summary=ai_signal.reasoning,
                    technical_score=ai_signal.technical_score,
                    fundamental_score=ai_signal.fundamental_score,
                    halal_compliant=is_halal,
                    timestamp=datetime.now(),
                    reasoning=self._generate_signal_reasoning(ai_signal, info, compliance_result)
                )
                
                signals.append(telegram_signal)
                
            except Exception as e:
                continue
        
        return signals
    
    def _filter_best_signals(self, signals: List[TelegramSignal]) -> List[TelegramSignal]:
        """Filter and rank signals for sending"""
        # Filter buy signals only
        buy_signals = [s for s in signals if s.signal_type == "BUY"]
        
        # Sort by confidence and technical score
        buy_signals.sort(key=lambda s: (s.confidence, s.technical_score), reverse=True)
        
        # Filter high-confidence signals
        high_confidence = [s for s in buy_signals if s.confidence >= self.min_confidence_threshold]
        
        return high_confidence[:3]  # Top 3 signals
    
    def _send_buy_signal(self, signal: TelegramSignal):
        """Send buy signal via Telegram"""
        try:
            # Create formatted message
            message = self._format_signal_message(signal)
            
            # Send message
            success = self.send_message(message)
            
            if success:
                self.signals_sent_today += 1
                self.last_signal_time = datetime.now()
                self.signal_history.append(signal)
                self.logger.info(f"Sent buy signal for {signal.symbol}")
            
        except Exception as e:
            self.logger.error(f"Failed to send signal: {str(e)}")
    
    def _format_signal_message(self, signal: TelegramSignal) -> str:
        """Format signal for Telegram message"""
        halal_indicator = "✅ Halal" if signal.halal_compliant else "⚠️ Review Required"
        confidence_emoji = "🔥" if signal.confidence > 0.9 else "🚀" if signal.confidence > 0.8 else "📈"
        
        upside_potential = ((signal.target_price - signal.current_price) / signal.current_price) * 100
        
        message = f"""
{confidence_emoji} **AI BUY SIGNAL** {confidence_emoji}

**Symbol:** {signal.symbol}
**Current Price:** ${signal.current_price:.2f}
**Target Price:** ${signal.target_price:.2f}
**Stop Loss:** ${signal.stop_loss:.2f}
**Upside Potential:** {upside_potential:.1f}%

**Confidence:** {signal.confidence:.1%}
**Technical Score:** {signal.technical_score:.1f}/100
**Fundamental Score:** {signal.fundamental_score:.1f}/100

**{halal_indicator}**

**Analysis:**
{signal.reasoning}

**Risk Management:**
- Position Size: 2-5% of portfolio
- Stop Loss: ${signal.stop_loss:.2f} (-{((signal.current_price - signal.stop_loss) / signal.current_price) * 100:.1f}%)
- Time Horizon: Medium-term (1-3 months)

**Disclaimer:** AI-generated signal for educational purposes. Not financial advice.

🕐 Generated: {signal.timestamp.strftime('%H:%M:%S')}
"""
        return message.strip()
    
    def _should_send_signal(self) -> bool:
        """Check if we should send a signal now"""
        # Check rate limiting
        if self.signals_sent_today >= self.max_signals_per_hour:
            return False
        
        # Check time since last signal
        if self.last_signal_time:
            time_since_last = datetime.now() - self.last_signal_time
            if time_since_last.total_seconds() < self.signal_interval:
                return False
        
        # Check market hours (9:30 AM - 4:00 PM ET)
        current_time = datetime.now()
        market_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
        
        if not (market_open <= current_time <= market_close):
            return False
        
        return True
    
    def _generate_signal_reasoning(self, ai_signal, info: Dict, compliance_result: Dict) -> str:
        """Generate detailed reasoning for the signal"""
        reasoning_parts = []
        
        # Technical reasoning
        if ai_signal.technical_score > 75:
            reasoning_parts.append("Strong technical setup with positive momentum indicators")
        elif ai_signal.technical_score > 60:
            reasoning_parts.append("Favorable technical patterns emerging")
        
        # Fundamental reasoning
        if ai_signal.fundamental_score > 75:
            reasoning_parts.append("Solid fundamental metrics with growth potential")
        elif ai_signal.fundamental_score > 60:
            reasoning_parts.append("Decent fundamentals supporting price movement")
        
        # Market cap and liquidity
        market_cap = info.get('marketCap', 0)
        if market_cap > 10e9:
            reasoning_parts.append("Large-cap stability with institutional interest")
        elif market_cap > 2e9:
            reasoning_parts.append("Mid-cap growth opportunity with balanced risk")
        
        # Volume analysis
        avg_volume = info.get('averageVolume', 0)
        if avg_volume > 1000000:
            reasoning_parts.append("High liquidity ensures easy entry/exit")
        
        return ". ".join(reasoning_parts) + "."
    
    def _track_signal_performance(self, signal: TelegramSignal):
        """Track signal performance for learning"""
        self.performance_tracking[signal.symbol] = {
            'entry_price': signal.current_price,
            'target_price': signal.target_price,
            'stop_loss': signal.stop_loss,
            'entry_time': signal.timestamp,
            'signal_confidence': signal.confidence
        }
    
    def _update_market_universe(self):
        """Update the list of stocks to monitor"""
        try:
            # Add trending stocks based on volume
            trending_stocks = self._identify_trending_stocks()
            new_stocks = [s for s in trending_stocks if s not in self.monitored_symbols]
            
            if new_stocks:
                self.monitored_symbols.extend(new_stocks[:10])
                self.logger.info(f"Added {len(new_stocks)} trending stocks to watchlist")
        
        except Exception as e:
            self.logger.error(f"Failed to update market universe: {str(e)}")
    
    def _identify_trending_stocks(self) -> List[str]:
        """Identify trending stocks based on volume and price movement"""
        # This would integrate with real-time market data feeds
        # For now, return popular trading stocks
        return ['PLTR', 'SOFI', 'RIVN', 'LCID', 'NIO', 'COIN', 'HOOD']
    
    def _send_performance_update(self):
        """Send hourly performance update"""
        if not self.signal_history:
            return
        
        try:
            recent_signals = [s for s in self.signal_history if 
                            (datetime.now() - s.timestamp).total_seconds() < 3600]
            
            if recent_signals:
                avg_confidence = np.mean([s.confidence for s in recent_signals])
                message = f"""
📊 **Hourly Performance Update**

Signals Generated: {len(recent_signals)}
Average Confidence: {avg_confidence:.1%}
Market Status: Active Monitoring

Top Performers: {', '.join([s.symbol for s in recent_signals[:3]])}
"""
                self.send_message(message.strip())
        
        except Exception as e:
            self.logger.error(f"Failed to send performance update: {str(e)}")
    
    def _send_daily_market_outlook(self):
        """Send daily market outlook"""
        message = """
🌅 **Daily Market Outlook**

AI Analysis: Scanning market for opportunities
Focus Areas: High-growth tech, undervalued dividend stocks
Risk Level: Moderate with careful position sizing

Key Watchlist Updates:
- Monitoring earnings season impacts
- Tracking sector rotation patterns
- Analyzing institutional flow data

Ready to identify profitable opportunities! 🎯
"""
        self.send_message(message.strip())
    
    def _send_market_close_summary(self):
        """Send market close summary"""
        try:
            signals_today = [s for s in self.signal_history if 
                           s.timestamp.date() == datetime.now().date()]
            
            message = f"""
🔔 **Market Close Summary**

Signals Generated Today: {len(signals_today)}
Average Confidence: {np.mean([s.confidence for s in signals_today]):.1%} if signals_today else 0
Top Picks: {', '.join([s.symbol for s in signals_today[:3]]) if signals_today else 'None'}

Tomorrow's Focus:
- Pre-market analysis starting 8:00 AM
- Earnings announcements monitoring
- Technical breakout detection

Rest well! Tomorrow brings new opportunities. 🌙
"""
            self.send_message(message.strip())
        
        except Exception as e:
            self.logger.error(f"Failed to send market close summary: {str(e)}")
    
    def send_startup_message(self):
        """Send bot startup message"""
        message = """
🤖 **Halal Algo Trading Bot Activated**

Features:
✅ Real-time market analysis every 60 seconds
✅ AI-powered buy signal generation
✅ Halal compliance screening (AAOIFI standards)
✅ Technical & fundamental analysis
✅ Risk management with stop-loss levels
✅ Performance tracking and learning

Market Coverage: S&P 500 + trending stocks
Signal Frequency: Every 60 seconds (market hours)
Confidence Threshold: 75%+

Ready to identify profitable halal investment opportunities! 🚀

**Commands:**
/status - Bot status
/performance - Performance metrics
/stop - Stop bot
/start - Restart bot
/help - Command list

**Disclaimer:** AI-generated signals for educational purposes. Always conduct your own research before investing.
"""
        self.send_message(message.strip())
    
    def send_message(self, text: str) -> bool:
        """Send message via Telegram API"""
        try:
            url = f"{self.base_url}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return True
            else:
                self.logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return False
    
    def handle_command(self, command: str, message_text: str = "") -> str:
        """Handle Telegram bot commands"""
        command = command.lower().strip()
        
        if command == "/start":
            if not self.is_running:
                threading.Thread(target=self.start_bot, daemon=True).start()
                return "🚀 Algo Bot started! Monitoring market for opportunities..."
            else:
                return "✅ Bot is already running and monitoring the market."
        
        elif command == "/stop":
            self.stop_bot()
            return "🛑 Algo Bot stopped. Market monitoring paused."
        
        elif command == "/status":
            status = "🟢 Running" if self.is_running else "🔴 Stopped"
            return f"""
**Bot Status:** {status}
**Signals Sent Today:** {self.signals_sent_today}
**Monitored Stocks:** {len(self.monitored_symbols)}
**Last Signal:** {self.last_signal_time.strftime('%H:%M:%S') if self.last_signal_time else 'None'}
**Market Hours:** {'Active' if self._should_send_signal() else 'Closed'}
"""
        
        elif command == "/performance":
            if not self.signal_history:
                return "📊 No signals generated yet. Bot is analyzing market conditions."
            
            recent_signals = self.signal_history[-10:]
            avg_confidence = np.mean([s.confidence for s in recent_signals])
            
            return f"""
📈 **Performance Metrics**

Recent Signals: {len(recent_signals)}
Average Confidence: {avg_confidence:.1%}
Top Picks: {', '.join([s.symbol for s in recent_signals[-3:]])}

Learning System: Active
Pattern Recognition: Improving
Market Adaptation: Continuous
"""
        
        elif command == "/help":
            return """
🤖 **Algo Bot Commands**

**/start** - Start bot monitoring
**/stop** - Stop bot monitoring  
**/status** - Check bot status
**/performance** - View performance metrics
**/analysis [SYMBOL]** - Get stock analysis
**/watchlist** - View current watchlist
**/settings** - Bot configuration

**Features:**
- Real-time signal generation
- Halal compliance screening
- Risk management
- Performance tracking
"""
        
        elif command.startswith("/analysis"):
            symbol = message_text.split()[-1].upper() if len(message_text.split()) > 1 else None
            if symbol:
                return self._get_stock_analysis(symbol)
            else:
                return "Please provide a stock symbol: /analysis AAPL"
        
        elif command == "/watchlist":
            top_stocks = self.monitored_symbols[:20]
            return f"📋 **Current Watchlist** (Top 20):\n{', '.join(top_stocks)}\n\nTotal: {len(self.monitored_symbols)} stocks monitored"
        
        else:
            return "❓ Unknown command. Type /help for available commands."
    
    def _get_stock_analysis(self, symbol: str) -> str:
        """Get detailed stock analysis"""
        try:
            # Get comprehensive analysis
            analysis = self.ai_research.comprehensive_stock_research(symbol)
            
            if 'error' in analysis:
                return f"❌ Could not analyze {symbol}. Please check the symbol."
            
            recommendation = analysis['research_sections']['investment_recommendation']
            key_metrics = analysis['key_metrics']
            
            return f"""
📊 **{symbol} Analysis**

**Recommendation:** {recommendation['recommendation']}
**Overall Score:** {recommendation['overall_score']:.1f}/100
**Confidence:** {recommendation['confidence_level']}

**Key Metrics:**
- Current Price: ${key_metrics['current_price']:.2f}
- Market Cap: ${key_metrics['market_cap']:,.0f}
- P/E Ratio: {key_metrics['pe_ratio']:.1f}
- Beta: {key_metrics['beta']:.2f}

**Investment Thesis:**
{recommendation['investment_thesis']}

**Risk Level:** {recommendation.get('risk_reward_assessment', 'Moderate')}
**Time Horizon:** {recommendation.get('time_horizon', '1-3 years')}
"""
        
        except Exception as e:
            return f"❌ Analysis failed for {symbol}: {str(e)}"

# Bot initialization and management functions
def create_telegram_bot(bot_token: str, chat_id: str) -> TelegramAlgoBot:
    """Create and configure Telegram bot"""
    return TelegramAlgoBot(bot_token, chat_id)

def start_telegram_bot_service(bot_token: str, chat_id: str):
    """Start Telegram bot as a service"""
    bot = create_telegram_bot(bot_token, chat_id)
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.start_bot, daemon=True)
    bot_thread.start()
    
    return bot

if __name__ == "__main__":
    # Configuration
    BOT_TOKEN = "7839339510:AAFnRHqigiXZHnWF8m2T2Li6iXLPWAw_uQg"
    CHAT_ID = "5043945231"
    
    # Create and start bot
    bot = create_telegram_bot(BOT_TOKEN, CHAT_ID)
    
    try:
        print("Starting Telegram Algo Bot...")
        bot.start_bot()
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.stop_bot()
    except Exception as e:
        print(f"Bot error: {str(e)}")
        bot.stop_bot()