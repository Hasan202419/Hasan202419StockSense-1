import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Tuple, Optional
import streamlit as st
from datetime import datetime, timedelta
import requests
import time
import random

class AutonomousAnalyzer:
    """AI-driven autonomous stock analysis and signal generation"""
    
    def __init__(self):
        self.analysis_weights = {
            'technical': 0.40,
            'fundamental': 0.35,
            'momentum': 0.15,
            'volume': 0.10
        }
        
        # Comprehensive US stock universe for autonomous research
        self.stock_universes = {
            'sp500': [],
            'nasdaq': [],
            'russell2000': [],
            'penny_stocks': [],
            'volatile_growth': []
        }
        
        self.market_sectors = [
            'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
            'Communication Services', 'Industrials', 'Consumer Defensive',
            'Energy', 'Utilities', 'Real Estate', 'Basic Materials'
        ]
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _fetch_extended_stock_universe(self) -> Dict[str, List[str]]:
        """Fetch comprehensive list of US stocks for autonomous analysis"""
        try:
            # Fetch S&P 500
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_tables = pd.read_html(sp500_url)
            sp500_symbols = sp500_tables[0]['Symbol'].str.replace('.', '-').tolist()
            
            # Fetch NASDAQ 100
            nasdaq_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            nasdaq_tables = pd.read_html(nasdaq_url)
            nasdaq_symbols = nasdaq_tables[4]['Ticker'].str.replace('.', '-').tolist()
            
            # Additional high-volume stocks for comprehensive analysis
            additional_stocks = [
                'AMC', 'GME', 'PLTR', 'WISH', 'CLOV', 'BB', 'SNDL', 'SOFI',
                'LCID', 'RIVN', 'F', 'BAC', 'WFC', 'JPM', 'GS', 'MS',
                'SNAP', 'TWTR', 'UBER', 'LYFT', 'ABNB', 'DASH', 'COIN',
                'SQ', 'PYPL', 'SHOP', 'ROKU', 'ZM', 'DOCU', 'CRWD'
            ]
            
            return {
                'sp500': sp500_symbols[:200],  # Limit for performance
                'nasdaq': nasdaq_symbols[:100],
                'additional': additional_stocks,
                'combined': list(set(sp500_symbols[:200] + nasdaq_symbols[:100] + additional_stocks))
            }
            
        except Exception as e:
            st.warning(f"Using fallback stock list due to: {str(e)}")
            # Comprehensive fallback list of major US stocks
            return {
                'combined': [
                    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
                    'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'DIS', 'ADBE',
                    'CRM', 'NFLX', 'KO', 'PEP', 'TMO', 'COST', 'ABBV', 'CVX', 'ACN',
                    'LLY', 'MCD', 'ABT', 'AVGO', 'DHR', 'TXN', 'NEE', 'ORCL', 'VZ',
                    'XOM', 'QCOM', 'BRK-B', 'NKE', 'PM', 'MRK', 'T', 'PFE', 'AMD',
                    'HON', 'LOW', 'IBM', 'UPS', 'CAT', 'RTX', 'INTC', 'GE', 'F',
                    'AMC', 'GME', 'PLTR', 'SOFI', 'LCID', 'RIVN', 'SNAP', 'UBER',
                    'SQ', 'PYPL', 'SHOP', 'ROKU', 'ZM', 'COIN', 'CRWD'
                ]
            }
    
    def autonomous_market_scan(self, max_stocks: int = 100) -> Dict[str, Dict]:
        """Autonomously scan the market for opportunities"""
        st.info("🤖 AI conducting autonomous market research...")
        
        # Get stock universe
        stock_universe = self._fetch_extended_stock_universe()
        all_symbols = stock_universe['combined'][:max_stocks]
        
        # Randomly sample for diverse analysis
        sampled_symbols = random.sample(all_symbols, min(max_stocks, len(all_symbols)))
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        analyzed_stocks = {}
        
        for i, symbol in enumerate(sampled_symbols):
            try:
                status_text.text(f"Analyzing {symbol} ({i+1}/{len(sampled_symbols)})")
                
                # Fetch real-time data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info and 'regularMarketPrice' in info:
                    analyzed_stocks[symbol] = info
                
                progress_bar.progress((i + 1) / len(sampled_symbols))
                
                # Respect API limits
                time.sleep(0.1)
                
            except Exception as e:
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        return analyzed_stocks
    
    def calculate_advanced_buy_signals(self, stocks_data: Dict[str, Dict]) -> pd.DataFrame:
        """Generate sophisticated buy signals using multiple algorithms"""
        signals_data = []
        
        for symbol, stock_info in stocks_data.items():
            try:
                # Fetch historical data for technical analysis
                ticker = yf.Ticker(symbol)
                hist_data = ticker.history(period="6mo")
                
                if hist_data.empty:
                    continue
                
                # Calculate comprehensive signals
                signal_score = self._calculate_composite_signal(stock_info, hist_data)
                
                # Risk assessment
                risk_level = self._assess_stock_risk(stock_info, hist_data)
                
                # Growth potential
                growth_score = self._calculate_growth_potential(stock_info, hist_data)
                
                # Final recommendation
                recommendation = self._generate_recommendation(signal_score, risk_level, growth_score)
                
                signals_data.append({
                    'symbol': symbol,
                    'company_name': stock_info.get('longName', symbol),
                    'current_price': stock_info.get('regularMarketPrice', 0),
                    'signal_score': signal_score,
                    'recommendation': recommendation,
                    'risk_level': risk_level,
                    'growth_score': growth_score,
                    'market_cap': stock_info.get('marketCap', 0),
                    'volume': stock_info.get('volume', 0),
                    'sector': stock_info.get('sector', 'Unknown'),
                    'pe_ratio': stock_info.get('trailingPE', 0),
                    'price_change_pct': self._calculate_price_momentum(hist_data),
                    'volatility': self._calculate_volatility(hist_data),
                    'is_penny_stock': stock_info.get('regularMarketPrice', 0) <= 5.0
                })
                
            except Exception as e:
                continue
        
        if not signals_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(signals_data)
        df = df.sort_values('signal_score', ascending=False)
        
        return df
    
    def _calculate_composite_signal(self, stock_info: Dict, hist_data: pd.DataFrame) -> float:
        """Calculate composite buy signal from multiple factors"""
        signals = []
        
        # Technical signals
        tech_signal = self._technical_signal(hist_data)
        signals.append(tech_signal * self.analysis_weights['technical'])
        
        # Fundamental signals
        fund_signal = self._fundamental_signal(stock_info)
        signals.append(fund_signal * self.analysis_weights['fundamental'])
        
        # Momentum signals
        momentum_signal = self._momentum_signal(hist_data)
        signals.append(momentum_signal * self.analysis_weights['momentum'])
        
        # Volume signals
        volume_signal = self._volume_signal(hist_data)
        signals.append(volume_signal * self.analysis_weights['volume'])
        
        return sum(signals)
    
    def _technical_signal(self, hist_data: pd.DataFrame) -> float:
        """Generate technical analysis signal (0-100)"""
        if len(hist_data) < 50:
            return 50  # Neutral
        
        close_prices = hist_data['Close']
        
        # Moving averages
        ma20 = close_prices.rolling(20).mean()
        ma50 = close_prices.rolling(50).mean()
        
        current_price = close_prices.iloc[-1]
        current_ma20 = ma20.iloc[-1]
        current_ma50 = ma50.iloc[-1]
        
        score = 50  # Start neutral
        
        # Price above moving averages
        if current_price > current_ma20:
            score += 15
        if current_price > current_ma50:
            score += 15
        if current_ma20 > current_ma50:
            score += 10
        
        # RSI calculation
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        if 30 < current_rsi < 70:
            score += 10
        elif current_rsi < 30:
            score += 5  # Oversold, potential buy
        
        return min(100, max(0, score))
    
    def _fundamental_signal(self, stock_info: Dict) -> float:
        """Generate fundamental analysis signal (0-100)"""
        score = 50  # Start neutral
        
        # P/E ratio analysis
        pe_ratio = stock_info.get('trailingPE', 0)
        if 0 < pe_ratio < 15:
            score += 20
        elif 15 <= pe_ratio < 25:
            score += 10
        elif pe_ratio > 40:
            score -= 10
        
        # Revenue growth
        revenue_growth = stock_info.get('revenueGrowth', 0)
        if revenue_growth > 0.15:  # 15% growth
            score += 15
        elif revenue_growth > 0.05:  # 5% growth
            score += 5
        
        # Profit margins
        profit_margin = stock_info.get('profitMargins', 0)
        if profit_margin > 0.15:  # 15% margin
            score += 10
        elif profit_margin > 0.05:  # 5% margin
            score += 5
        
        # Debt to equity
        debt_to_equity = stock_info.get('debtToEquity', 0)
        if debt_to_equity < 30:
            score += 5
        elif debt_to_equity > 100:
            score -= 10
        
        return min(100, max(0, score))
    
    def _momentum_signal(self, hist_data: pd.DataFrame) -> float:
        """Generate momentum signal (0-100)"""
        if len(hist_data) < 30:
            return 50
        
        close_prices = hist_data['Close']
        
        # Price momentum over different periods
        current_price = close_prices.iloc[-1]
        price_5d = close_prices.iloc[-6] if len(close_prices) > 5 else current_price
        price_20d = close_prices.iloc[-21] if len(close_prices) > 20 else current_price
        
        momentum_5d = (current_price - price_5d) / price_5d
        momentum_20d = (current_price - price_20d) / price_20d
        
        score = 50
        
        if momentum_5d > 0.02:  # 2% gain in 5 days
            score += 15
        elif momentum_5d > 0:
            score += 5
        
        if momentum_20d > 0.1:  # 10% gain in 20 days
            score += 20
        elif momentum_20d > 0:
            score += 10
        
        return min(100, max(0, score))
    
    def _volume_signal(self, hist_data: pd.DataFrame) -> float:
        """Generate volume-based signal (0-100)"""
        if len(hist_data) < 20:
            return 50
        
        volumes = hist_data['Volume']
        avg_volume = volumes.rolling(20).mean()
        current_volume = volumes.iloc[-1]
        avg_20d = avg_volume.iloc[-1]
        
        score = 50
        
        # Above average volume indicates interest
        if current_volume > avg_20d * 1.5:
            score += 20
        elif current_volume > avg_20d:
            score += 10
        
        return min(100, max(0, score))
    
    def _assess_stock_risk(self, stock_info: Dict, hist_data: pd.DataFrame) -> str:
        """Assess risk level of the stock"""
        risk_factors = 0
        
        # Market cap risk
        market_cap = stock_info.get('marketCap', 0)
        if market_cap < 2e9:  # Under $2B
            risk_factors += 2
        elif market_cap < 10e9:  # Under $10B
            risk_factors += 1
        
        # Price volatility
        if len(hist_data) >= 30:
            returns = hist_data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            if volatility > 0.5:  # 50% annual volatility
                risk_factors += 2
            elif volatility > 0.3:  # 30% annual volatility
                risk_factors += 1
        
        # Penny stock risk
        if stock_info.get('regularMarketPrice', 0) <= 5:
            risk_factors += 2
        
        # Debt levels
        debt_to_equity = stock_info.get('debtToEquity', 0)
        if debt_to_equity > 100:
            risk_factors += 1
        
        if risk_factors >= 4:
            return "High"
        elif risk_factors >= 2:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_growth_potential(self, stock_info: Dict, hist_data: pd.DataFrame) -> float:
        """Calculate growth potential score (0-100)"""
        score = 50
        
        # Revenue growth
        revenue_growth = stock_info.get('revenueGrowth', 0)
        if revenue_growth > 0.25:  # 25% growth
            score += 25
        elif revenue_growth > 0.15:  # 15% growth
            score += 15
        elif revenue_growth > 0.05:  # 5% growth
            score += 5
        
        # Earnings growth
        earnings_growth = stock_info.get('earningsGrowth', 0)
        if earnings_growth > 0.25:
            score += 20
        elif earnings_growth > 0.15:
            score += 10
        
        # Market position (sector growth)
        sector = stock_info.get('sector', '')
        growth_sectors = ['Technology', 'Healthcare', 'Consumer Cyclical']
        if sector in growth_sectors:
            score += 10
        
        return min(100, max(0, score))
    
    def _generate_recommendation(self, signal_score: float, risk_level: str, growth_score: float) -> str:
        """Generate final recommendation"""
        # Adjust signal score based on risk
        risk_adjustment = {"Low": 0, "Medium": -5, "High": -15}
        adjusted_score = signal_score + risk_adjustment[risk_level]
        
        # Factor in growth potential
        final_score = (adjusted_score * 0.7) + (growth_score * 0.3)
        
        if final_score >= 75:
            return "Strong Buy"
        elif final_score >= 65:
            return "Buy"
        elif final_score >= 55:
            return "Hold"
        elif final_score >= 45:
            return "Weak Hold"
        else:
            return "Avoid"
    
    def _calculate_price_momentum(self, hist_data: pd.DataFrame) -> float:
        """Calculate price momentum percentage"""
        if len(hist_data) < 30:
            return 0
        
        current_price = hist_data['Close'].iloc[-1]
        month_ago_price = hist_data['Close'].iloc[-30]
        
        return ((current_price - month_ago_price) / month_ago_price) * 100
    
    def _calculate_volatility(self, hist_data: pd.DataFrame) -> float:
        """Calculate annualized volatility"""
        if len(hist_data) < 30:
            return 0
        
        returns = hist_data['Close'].pct_change().dropna()
        return returns.std() * np.sqrt(252) * 100  # Percentage
    
    def identify_penny_stock_opportunities(self, stocks_data: Dict[str, Dict]) -> pd.DataFrame:
        """Identify high-potential penny stocks with buy signals"""
        penny_opportunities = []
        
        for symbol, stock_info in stocks_data.items():
            current_price = stock_info.get('regularMarketPrice', 0)
            
            if 0.1 <= current_price <= 5.0:  # Penny stock range
                try:
                    # Fetch historical data
                    ticker = yf.Ticker(symbol)
                    hist_data = ticker.history(period="3mo")
                    
                    if hist_data.empty:
                        continue
                    
                    # Calculate opportunity score
                    opportunity_score = self._calculate_penny_opportunity_score(stock_info, hist_data)
                    
                    if opportunity_score >= 60:  # Only high-potential opportunities
                        penny_opportunities.append({
                            'symbol': symbol,
                            'company_name': stock_info.get('longName', symbol),
                            'current_price': current_price,
                            'opportunity_score': opportunity_score,
                            'market_cap': stock_info.get('marketCap', 0),
                            'volume': stock_info.get('volume', 0),
                            'avg_volume': stock_info.get('averageVolume', 0),
                            'sector': stock_info.get('sector', 'Unknown'),
                            'price_momentum': self._calculate_price_momentum(hist_data),
                            'volatility': self._calculate_volatility(hist_data),
                            'risk_level': self._assess_stock_risk(stock_info, hist_data)
                        })
                        
                except Exception as e:
                    continue
        
        if not penny_opportunities:
            return pd.DataFrame()
        
        df = pd.DataFrame(penny_opportunities)
        df = df.sort_values('opportunity_score', ascending=False)
        
        return df
    
    def _calculate_penny_opportunity_score(self, stock_info: Dict, hist_data: pd.DataFrame) -> float:
        """Calculate opportunity score for penny stocks"""
        score = 0
        
        # Volume analysis (critical for penny stocks)
        avg_volume = stock_info.get('averageVolume', 0)
        if avg_volume > 1000000:  # 1M+ daily volume
            score += 25
        elif avg_volume > 500000:  # 500K+ daily volume
            score += 15
        elif avg_volume > 100000:  # 100K+ daily volume
            score += 10
        
        # Market cap consideration
        market_cap = stock_info.get('marketCap', 0)
        if market_cap > 100e6:  # $100M+ market cap
            score += 20
        elif market_cap > 50e6:  # $50M+ market cap
            score += 15
        elif market_cap > 10e6:  # $10M+ market cap
            score += 10
        
        # Recent price momentum
        if len(hist_data) >= 30:
            momentum = self._calculate_price_momentum(hist_data)
            if momentum > 20:  # 20%+ momentum
                score += 20
            elif momentum > 10:  # 10%+ momentum
                score += 15
            elif momentum > 0:  # Positive momentum
                score += 10
        
        # Technical indicators
        tech_score = self._technical_signal(hist_data)
        score += (tech_score - 50) * 0.4  # Scale technical score
        
        return min(100, max(0, score))