import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Optional, Any
import streamlit as st
from datetime import datetime, timedelta
import requests
import json
import re

class AIResearchAssistant:
    """Advanced AI Research Assistant for Stock Market Analysis"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.research_cache = {}
        self.analysis_depth = "comprehensive"
        
        # Financial data sources
        self.data_sources = {
            'yahoo_finance': True,
            'sec_filings': True,
            'earnings_data': True,
            'insider_trading': True,
            'analyst_ratings': True
        }
        
        # Research capabilities
        self.research_areas = [
            'fundamental_analysis',
            'technical_analysis', 
            'market_sentiment',
            'competitive_analysis',
            'industry_trends',
            'economic_indicators',
            'risk_assessment',
            'valuation_models',
            'earnings_analysis',
            'management_analysis'
        ]
    
    def comprehensive_stock_research(self, symbol: str) -> Dict[str, Any]:
        """Conduct comprehensive research on a stock"""
        try:
            # Fetch comprehensive data
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            history = ticker.history(period="2y")
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            if not info or history.empty:
                return {"error": f"No data available for {symbol}"}
            
            research_report = {
                'symbol': symbol.upper(),
                'company_name': info.get('longName', symbol),
                'timestamp': datetime.now().isoformat(),
                'analysis_depth': 'comprehensive',
                'research_sections': {}
            }
            
            # 1. Company Overview & Business Model
            research_report['research_sections']['company_overview'] = self._analyze_company_overview(info)
            
            # 2. Financial Health Analysis
            research_report['research_sections']['financial_health'] = self._analyze_financial_health(
                info, financials, balance_sheet, cash_flow
            )
            
            # 3. Technical Analysis
            research_report['research_sections']['technical_analysis'] = self._analyze_technical_patterns(history, symbol)
            
            # 4. Valuation Analysis
            research_report['research_sections']['valuation'] = self._analyze_valuation(info, financials)
            
            # 5. Growth Analysis
            research_report['research_sections']['growth_analysis'] = self._analyze_growth_prospects(info, financials)
            
            # 6. Risk Assessment
            research_report['research_sections']['risk_assessment'] = self._analyze_investment_risks(info, history)
            
            # 7. Competitive Analysis
            research_report['research_sections']['competitive_analysis'] = self._analyze_competitive_position(info)
            
            # 8. Market Sentiment & Analyst Views
            research_report['research_sections']['market_sentiment'] = self._analyze_market_sentiment(info)
            
            # 9. Investment Recommendation
            research_report['research_sections']['investment_recommendation'] = self._generate_investment_recommendation(
                research_report['research_sections']
            )
            
            # 10. Key Metrics Summary
            research_report['key_metrics'] = self._extract_key_metrics(info, history)
            
            return research_report
            
        except Exception as e:
            return {"error": f"Research failed for {symbol}: {str(e)}"}
    
    def _analyze_company_overview(self, info: Dict) -> Dict[str, Any]:
        """Analyze company overview and business model"""
        return {
            'business_summary': info.get('longBusinessSummary', 'Not available'),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', 0),
            'market_cap_category': self._categorize_market_cap(info.get('marketCap', 0)),
            'employee_count': info.get('fullTimeEmployees', 'Not disclosed'),
            'headquarters': f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(', '),
            'website': info.get('website', 'Not available'),
            'exchange': info.get('exchange', 'Unknown'),
            'currency': info.get('currency', 'USD')
        }
    
    def _analyze_financial_health(self, info: Dict, financials: pd.DataFrame, 
                                 balance_sheet: pd.DataFrame, cash_flow: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive financial health analysis"""
        analysis = {
            'profitability': {},
            'liquidity': {},
            'solvency': {},
            'efficiency': {},
            'financial_strength_score': 0
        }
        
        # Profitability metrics
        analysis['profitability'] = {
            'profit_margin': info.get('profitMargins', 0),
            'operating_margin': info.get('operatingMargins', 0),
            'gross_margin': info.get('grossMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'roa': info.get('returnOnAssets', 0),
            'roic': self._calculate_roic(info)
        }
        
        # Liquidity metrics
        analysis['liquidity'] = {
            'current_ratio': info.get('currentRatio', 0),
            'quick_ratio': info.get('quickRatio', 0),
            'cash_ratio': self._calculate_cash_ratio(info),
            'working_capital': self._calculate_working_capital(balance_sheet)
        }
        
        # Solvency metrics
        analysis['solvency'] = {
            'debt_to_equity': info.get('debtToEquity', 0),
            'debt_to_assets': self._calculate_debt_to_assets(info),
            'interest_coverage': self._calculate_interest_coverage(financials),
            'debt_service_coverage': self._calculate_debt_service_coverage(cash_flow, info)
        }
        
        # Efficiency metrics
        analysis['efficiency'] = {
            'asset_turnover': self._calculate_asset_turnover(info),
            'inventory_turnover': self._calculate_inventory_turnover(info),
            'receivables_turnover': self._calculate_receivables_turnover(info)
        }
        
        # Calculate overall financial strength score
        analysis['financial_strength_score'] = self._calculate_financial_strength_score(analysis)
        
        return analysis
    
    def _analyze_technical_patterns(self, history: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Advanced technical analysis"""
        if history.empty:
            return {"error": "No historical data available"}
        
        close_prices = history['Close']
        volume = history['Volume']
        
        analysis = {
            'trend_analysis': {},
            'momentum_indicators': {},
            'volatility_analysis': {},
            'support_resistance': {},
            'pattern_recognition': {},
            'technical_score': 0
        }
        
        # Trend Analysis
        analysis['trend_analysis'] = {
            'short_term_trend': self._identify_trend(close_prices, 20),
            'medium_term_trend': self._identify_trend(close_prices, 50),
            'long_term_trend': self._identify_trend(close_prices, 200),
            'trend_strength': self._calculate_trend_strength(close_prices)
        }
        
        # Momentum Indicators
        analysis['momentum_indicators'] = {
            'rsi': self._calculate_rsi(close_prices),
            'macd': self._calculate_macd_signal(close_prices),
            'stochastic': self._calculate_stochastic(history),
            'williams_r': self._calculate_williams_r(history)
        }
        
        # Volatility Analysis
        analysis['volatility_analysis'] = {
            'historical_volatility': self._calculate_historical_volatility(close_prices),
            'bollinger_bands': self._analyze_bollinger_bands(close_prices),
            'average_true_range': self._calculate_atr(history)
        }
        
        # Support and Resistance
        analysis['support_resistance'] = self._identify_support_resistance(close_prices)
        
        # Pattern Recognition
        analysis['pattern_recognition'] = self._identify_chart_patterns(history)
        
        # Calculate technical score
        analysis['technical_score'] = self._calculate_technical_score(analysis)
        
        return analysis
    
    def _analyze_valuation(self, info: Dict, financials: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive valuation analysis"""
        analysis = {
            'multiple_valuation': {},
            'dcf_analysis': {},
            'relative_valuation': {},
            'intrinsic_value_estimate': 0,
            'valuation_grade': 'N/A'
        }
        
        # Multiple-based valuation
        analysis['multiple_valuation'] = {
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'price_to_book': info.get('priceToBook', 0),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
            'enterprise_value_revenue': info.get('enterpriseToRevenue', 0),
            'enterprise_value_ebitda': info.get('enterpriseToEbitda', 0)
        }
        
        # DCF Analysis (simplified)
        analysis['dcf_analysis'] = self._perform_dcf_analysis(info, financials)
        
        # Relative valuation
        analysis['relative_valuation'] = self._perform_relative_valuation(info)
        
        # Calculate intrinsic value estimate
        analysis['intrinsic_value_estimate'] = self._calculate_intrinsic_value(analysis, info)
        
        # Assign valuation grade
        analysis['valuation_grade'] = self._assign_valuation_grade(analysis, info)
        
        return analysis
    
    def _analyze_growth_prospects(self, info: Dict, financials: pd.DataFrame) -> Dict[str, Any]:
        """Analyze growth prospects and future potential"""
        return {
            'historical_growth': {
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'book_value_growth': self._calculate_book_value_growth(financials)
            },
            'future_projections': {
                'analyst_growth_estimates': info.get('earningsGrowth', 0),
                'revenue_growth_projection': self._project_revenue_growth(info, financials),
                'market_expansion_potential': self._assess_market_expansion(info)
            },
            'growth_drivers': self._identify_growth_drivers(info),
            'growth_sustainability': self._assess_growth_sustainability(info, financials),
            'growth_score': self._calculate_growth_score(info, financials)
        }
    
    def _analyze_investment_risks(self, info: Dict, history: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        return {
            'market_risks': {
                'beta': info.get('beta', 1.0),
                'volatility': self._calculate_historical_volatility(history['Close']),
                'max_drawdown': self._calculate_max_drawdown(history['Close']),
                'var_95': self._calculate_var(history['Close'], 0.95)
            },
            'financial_risks': {
                'debt_risk': self._assess_debt_risk(info),
                'liquidity_risk': self._assess_liquidity_risk(info),
                'profitability_risk': self._assess_profitability_risk(info)
            },
            'business_risks': {
                'industry_cyclicality': self._assess_industry_cyclicality(info),
                'competitive_risk': self._assess_competitive_risk(info),
                'regulatory_risk': self._assess_regulatory_risk(info)
            },
            'overall_risk_grade': self._calculate_overall_risk_grade(info, history)
        }
    
    def _analyze_competitive_position(self, info: Dict) -> Dict[str, Any]:
        """Analyze competitive position and market standing"""
        return {
            'market_position': {
                'market_cap_rank': self._determine_market_cap_rank(info),
                'industry_leadership': self._assess_industry_leadership(info),
                'competitive_moat': self._assess_competitive_moat(info)
            },
            'competitive_advantages': self._identify_competitive_advantages(info),
            'market_share_analysis': self._analyze_market_share(info),
            'competitive_threats': self._identify_competitive_threats(info),
            'competitive_strength_score': self._calculate_competitive_strength(info)
        }
    
    def _analyze_market_sentiment(self, info: Dict) -> Dict[str, Any]:
        """Analyze market sentiment and analyst views"""
        return {
            'analyst_ratings': {
                'recommendation_mean': info.get('recommendationMean', 0),
                'recommendation_key': info.get('recommendationKey', 'None'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions', 0),
                'target_high_price': info.get('targetHighPrice', 0),
                'target_low_price': info.get('targetLowPrice', 0),
                'target_mean_price': info.get('targetMeanPrice', 0),
                'target_median_price': info.get('targetMedianPrice', 0)
            },
            'institutional_interest': {
                'institutional_ownership': info.get('heldPercentInstitutions', 0),
                'insider_ownership': info.get('heldPercentInsiders', 0),
                'short_interest': info.get('shortPercentOfFloat', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0)
            },
            'market_perception': self._assess_market_perception(info),
            'sentiment_score': self._calculate_sentiment_score(info)
        }
    
    def _generate_investment_recommendation(self, sections: Dict) -> Dict[str, Any]:
        """Generate comprehensive investment recommendation"""
        # Extract scores from each section
        financial_score = sections.get('financial_health', {}).get('financial_strength_score', 50)
        technical_score = sections.get('technical_analysis', {}).get('technical_score', 50)
        growth_score = sections.get('growth_analysis', {}).get('growth_score', 50)
        sentiment_score = sections.get('market_sentiment', {}).get('sentiment_score', 50)
        
        # Calculate weighted overall score
        overall_score = (
            financial_score * 0.30 +
            technical_score * 0.25 +
            growth_score * 0.25 +
            sentiment_score * 0.20
        )
        
        # Determine recommendation
        if overall_score >= 80:
            recommendation = "Strong Buy"
            confidence = "High"
        elif overall_score >= 70:
            recommendation = "Buy"
            confidence = "Medium-High"
        elif overall_score >= 60:
            recommendation = "Hold"
            confidence = "Medium"
        elif overall_score >= 50:
            recommendation = "Weak Hold"
            confidence = "Medium-Low"
        else:
            recommendation = "Avoid/Sell"
            confidence = "Low"
        
        return {
            'recommendation': recommendation,
            'overall_score': overall_score,
            'confidence_level': confidence,
            'key_strengths': self._identify_key_strengths(sections),
            'key_concerns': self._identify_key_concerns(sections),
            'investment_thesis': self._generate_investment_thesis(sections, overall_score),
            'risk_reward_assessment': self._assess_risk_reward(sections),
            'time_horizon': self._recommend_time_horizon(sections),
            'position_sizing': self._recommend_position_sizing(sections)
        }
    
    def answer_stock_question(self, question: str, symbol: str = None) -> str:
        """Answer any stock-related question with precision and depth"""
        try:
            question_lower = question.lower()
            
            # Determine if symbol is mentioned in question
            if symbol is None:
                symbol = self._extract_symbol_from_question(question)
            
            # Categorize question type
            question_category = self._categorize_question(question_lower)
            
            # Generate comprehensive answer based on category
            if question_category == 'company_analysis' and symbol:
                return self._answer_company_analysis_question(question, symbol)
            elif question_category == 'technical_analysis' and symbol:
                return self._answer_technical_question(question, symbol)
            elif question_category == 'fundamental_analysis' and symbol:
                return self._answer_fundamental_question(question, symbol)
            elif question_category == 'market_general':
                return self._answer_market_general_question(question)
            elif question_category == 'valuation' and symbol:
                return self._answer_valuation_question(question, symbol)
            elif question_category == 'risk_analysis' and symbol:
                return self._answer_risk_question(question, symbol)
            else:
                return self._provide_general_guidance(question, symbol)
                
        except Exception as e:
            return f"I apologize, but I encountered an error while analyzing your question: {str(e)}. Please try rephrasing your question or provide more specific details."
    
    def _extract_symbol_from_question(self, question: str) -> Optional[str]:
        """Extract stock symbol from question text"""
        # Look for patterns like $AAPL, AAPL, (AAPL)
        patterns = [
            r'\$([A-Z]{1,5})',  # $AAPL
            r'\b([A-Z]{2,5})\b',  # AAPL
            r'\(([A-Z]{1,5})\)'  # (AAPL)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, question.upper())
            if matches:
                return matches[0]
        return None
    
    def _categorize_question(self, question: str) -> str:
        """Categorize the type of question being asked"""
        technical_keywords = ['chart', 'technical', 'trend', 'support', 'resistance', 'moving average', 'rsi', 'macd']
        fundamental_keywords = ['earnings', 'revenue', 'profit', 'balance sheet', 'cash flow', 'fundamental']
        valuation_keywords = ['valuation', 'price target', 'fair value', 'pe ratio', 'expensive', 'cheap']
        risk_keywords = ['risk', 'safe', 'volatile', 'beta', 'downside']
        
        if any(keyword in question for keyword in technical_keywords):
            return 'technical_analysis'
        elif any(keyword in question for keyword in fundamental_keywords):
            return 'fundamental_analysis'
        elif any(keyword in question for keyword in valuation_keywords):
            return 'valuation'
        elif any(keyword in question for keyword in risk_keywords):
            return 'risk_analysis'
        elif any(keyword in question for keyword in ['company', 'business', 'industry', 'sector']):
            return 'company_analysis'
        else:
            return 'market_general'
    
    # Helper methods for calculations (simplified implementations)
    def _categorize_market_cap(self, market_cap: float) -> str:
        if market_cap > 200e9:
            return "Mega Cap"
        elif market_cap > 10e9:
            return "Large Cap"
        elif market_cap > 2e9:
            return "Mid Cap"
        elif market_cap > 300e6:
            return "Small Cap"
        else:
            return "Micro Cap"
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not rsi.empty else 50.0
    
    def _calculate_historical_volatility(self, prices: pd.Series) -> float:
        returns = prices.pct_change().dropna()
        return float(returns.std() * np.sqrt(252) * 100) if len(returns) > 0 else 0.0
    
    def _calculate_financial_strength_score(self, analysis: Dict) -> float:
        # Simplified scoring based on key metrics
        score = 50  # Base score
        
        # Profitability scoring
        if analysis['profitability']['profit_margin'] > 0.15:
            score += 10
        if analysis['profitability']['roe'] > 0.15:
            score += 10
        
        # Liquidity scoring
        if analysis['liquidity']['current_ratio'] > 1.5:
            score += 10
        
        # Solvency scoring
        if analysis['solvency']['debt_to_equity'] < 50:
            score += 10
        
        return min(100, max(0, score))
    
    def _calculate_technical_score(self, analysis: Dict) -> float:
        # Simplified technical scoring
        score = 50
        
        # Trend scoring
        if analysis['trend_analysis']['short_term_trend'] == 'Bullish':
            score += 15
        if analysis['trend_analysis']['medium_term_trend'] == 'Bullish':
            score += 10
        
        # Momentum scoring
        rsi = analysis['momentum_indicators']['rsi']
        if 40 < rsi < 70:
            score += 10
        elif rsi < 30:
            score += 5  # Oversold
        
        return min(100, max(0, score))
    
    def _identify_trend(self, prices: pd.Series, period: int) -> str:
        if len(prices) < period:
            return "Insufficient Data"
        
        ma = prices.rolling(period).mean()
        current_price = prices.iloc[-1]
        current_ma = ma.iloc[-1]
        
        if current_price > current_ma * 1.02:
            return "Bullish"
        elif current_price < current_ma * 0.98:
            return "Bearish"
        else:
            return "Neutral"
    
    # Placeholder methods for complex calculations
    def _calculate_roic(self, info: Dict) -> float:
        return info.get('returnOnEquity', 0) * 0.8  # Simplified
    
    def _calculate_cash_ratio(self, info: Dict) -> float:
        return info.get('currentRatio', 0) * 0.5  # Simplified
    
    def _calculate_working_capital(self, balance_sheet: pd.DataFrame) -> float:
        return 0.0  # Simplified
    
    def _calculate_debt_to_assets(self, info: Dict) -> float:
        return info.get('debtToEquity', 0) / 100  # Simplified
    
    def _calculate_interest_coverage(self, financials: pd.DataFrame) -> float:
        return 5.0  # Simplified
    
    def _calculate_debt_service_coverage(self, cash_flow: pd.DataFrame, info: Dict) -> float:
        return 2.0  # Simplified
    
    def _calculate_asset_turnover(self, info: Dict) -> float:
        return 1.0  # Simplified
    
    def _calculate_inventory_turnover(self, info: Dict) -> float:
        return 5.0  # Simplified
    
    def _calculate_receivables_turnover(self, info: Dict) -> float:
        return 8.0  # Simplified
    
    def _extract_key_metrics(self, info: Dict, history: pd.DataFrame) -> Dict:
        return {
            'current_price': info.get('regularMarketPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 1.0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0),
            'average_volume': info.get('averageVolume', 0),
            'shares_outstanding': info.get('sharesOutstanding', 0)
        }
    
    # Additional placeholder methods for comprehensive analysis
    def _calculate_macd_signal(self, prices: pd.Series) -> str:
        return "Bullish"  # Simplified
    
    def _calculate_stochastic(self, history: pd.DataFrame) -> float:
        return 50.0  # Simplified
    
    def _calculate_williams_r(self, history: pd.DataFrame) -> float:
        return -50.0  # Simplified
    
    def _analyze_bollinger_bands(self, prices: pd.Series) -> Dict:
        return {"position": "Middle", "squeeze": False}  # Simplified
    
    def _calculate_atr(self, history: pd.DataFrame) -> float:
        return 2.0  # Simplified
    
    def _identify_support_resistance(self, prices: pd.Series) -> Dict:
        return {"support": prices.min(), "resistance": prices.max()}  # Simplified
    
    def _identify_chart_patterns(self, history: pd.DataFrame) -> List[str]:
        return ["Consolidation"]  # Simplified
    
    def _perform_dcf_analysis(self, info: Dict, financials: pd.DataFrame) -> Dict:
        return {"estimated_value": info.get('regularMarketPrice', 0) * 1.1}  # Simplified
    
    def _perform_relative_valuation(self, info: Dict) -> Dict:
        return {"industry_comparison": "Average"}  # Simplified
    
    def _calculate_intrinsic_value(self, analysis: Dict, info: Dict) -> float:
        return info.get('regularMarketPrice', 0) * 1.05  # Simplified
    
    def _assign_valuation_grade(self, analysis: Dict, info: Dict) -> str:
        pe = info.get('trailingPE', 20)
        if pe < 15:
            return "A"
        elif pe < 25:
            return "B"
        else:
            return "C"
    
    # Additional comprehensive analysis methods would be implemented here
    # These are simplified for brevity but would contain full calculations in production
    
    def _answer_company_analysis_question(self, question: str, symbol: str) -> str:
        research = self.comprehensive_stock_research(symbol)
        if 'error' in research:
            return f"I couldn't retrieve comprehensive data for {symbol}. {research['error']}"
        
        overview = research['research_sections']['company_overview']
        return f"""
**{overview['company_name']} ({symbol}) - Company Analysis**

**Business Overview:**
{overview['business_summary'][:500]}...

**Key Facts:**
• Sector: {overview['sector']}
• Industry: {overview['industry']}
• Market Cap: ${overview['market_cap']:,.0f} ({overview['market_cap_category']})
• Employees: {overview['employee_count']}
• Headquarters: {overview['headquarters']}

**Investment Grade:** {research['research_sections']['investment_recommendation']['recommendation']}
**Overall Score:** {research['research_sections']['investment_recommendation']['overall_score']:.1f}/100

For specific aspects of this company, feel free to ask more detailed questions about financials, valuation, or technical analysis.
"""
    
    def _answer_technical_question(self, question: str, symbol: str) -> str:
        # Implementation for technical analysis questions
        return f"Technical analysis for {symbol} would be provided here with detailed charts and indicators."
    
    def _answer_fundamental_question(self, question: str, symbol: str) -> str:
        # Implementation for fundamental analysis questions
        return f"Fundamental analysis for {symbol} would be provided here with detailed financial metrics."
    
    def _answer_market_general_question(self, question: str) -> str:
        # Implementation for general market questions
        return "General market analysis and insights would be provided here."
    
    def _answer_valuation_question(self, question: str, symbol: str) -> str:
        # Implementation for valuation questions
        return f"Valuation analysis for {symbol} would be provided here."
    
    def _answer_risk_question(self, question: str, symbol: str) -> str:
        # Implementation for risk analysis questions
        return f"Risk analysis for {symbol} would be provided here."
    
    def _provide_general_guidance(self, question: str, symbol: str) -> str:
        return f"I'd be happy to help with your question about {symbol if symbol else 'the stock market'}. Could you provide more specific details about what you'd like to know?"
    
    # Placeholder methods for detailed analysis components
    def _calculate_trend_strength(self, prices: pd.Series) -> float:
        return 0.75  # Simplified
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        return 0.15  # Simplified
    
    def _calculate_var(self, prices: pd.Series, confidence: float) -> float:
        returns = prices.pct_change().dropna()
        return float(returns.quantile(1 - confidence)) if len(returns) > 0 else 0.0
    
    def _assess_debt_risk(self, info: Dict) -> str:
        debt_ratio = info.get('debtToEquity', 0)
        if debt_ratio < 30:
            return "Low"
        elif debt_ratio < 60:
            return "Medium"
        else:
            return "High"
    
    def _assess_liquidity_risk(self, info: Dict) -> str:
        current_ratio = info.get('currentRatio', 0)
        if current_ratio > 2:
            return "Low"
        elif current_ratio > 1:
            return "Medium"
        else:
            return "High"
    
    def _assess_profitability_risk(self, info: Dict) -> str:
        profit_margin = info.get('profitMargins', 0)
        if profit_margin > 0.15:
            return "Low"
        elif profit_margin > 0.05:
            return "Medium"
        else:
            return "High"
    
    def _calculate_growth_score(self, info: Dict, financials: pd.DataFrame) -> float:
        score = 50
        revenue_growth = info.get('revenueGrowth', 0)
        earnings_growth = info.get('earningsGrowth', 0)
        
        if revenue_growth > 0.15:
            score += 20
        if earnings_growth > 0.20:
            score += 20
        
        return min(100, score)
    
    def _calculate_sentiment_score(self, info: Dict) -> float:
        score = 50
        recommendation = info.get('recommendationMean', 3)
        
        if recommendation <= 2:  # Buy/Strong Buy
            score += 20
        elif recommendation <= 2.5:
            score += 10
        
        return min(100, score)
    
    def _identify_key_strengths(self, sections: Dict) -> List[str]:
        return ["Strong financial position", "Positive growth trajectory", "Favorable market sentiment"]
    
    def _identify_key_concerns(self, sections: Dict) -> List[str]:
        return ["Market volatility", "Competitive pressure", "Economic uncertainty"]
    
    def _generate_investment_thesis(self, sections: Dict, score: float) -> str:
        if score >= 70:
            return "This stock presents a compelling investment opportunity with strong fundamentals and positive momentum."
        else:
            return "This stock requires careful consideration due to mixed signals in key metrics."
    
    def _assess_risk_reward(self, sections: Dict) -> str:
        return "Moderate risk with good reward potential"
    
    def _recommend_time_horizon(self, sections: Dict) -> str:
        return "Medium to long-term (1-3 years)"
    
    def _recommend_position_sizing(self, sections: Dict) -> str:
        return "Consider a moderate position size (2-5% of portfolio)"
    
    # Additional placeholder methods would be implemented for complete functionality
    def _calculate_book_value_growth(self, financials: pd.DataFrame) -> float:
        return 0.10  # Simplified
    
    def _project_revenue_growth(self, info: Dict, financials: pd.DataFrame) -> float:
        return info.get('revenueGrowth', 0.05)  # Simplified
    
    def _assess_market_expansion(self, info: Dict) -> str:
        return "Moderate expansion potential"  # Simplified
    
    def _identify_growth_drivers(self, info: Dict) -> List[str]:
        return ["Market expansion", "Product innovation", "Operational efficiency"]
    
    def _assess_growth_sustainability(self, info: Dict, financials: pd.DataFrame) -> str:
        return "Sustainable"  # Simplified
    
    def _assess_industry_cyclicality(self, info: Dict) -> str:
        return "Low cyclicality"  # Simplified
    
    def _assess_competitive_risk(self, info: Dict) -> str:
        return "Medium"  # Simplified
    
    def _assess_regulatory_risk(self, info: Dict) -> str:
        return "Low"  # Simplified
    
    def _calculate_overall_risk_grade(self, info: Dict, history: pd.DataFrame) -> str:
        return "B"  # Simplified
    
    def _determine_market_cap_rank(self, info: Dict) -> str:
        return "Top quartile"  # Simplified
    
    def _assess_industry_leadership(self, info: Dict) -> str:
        return "Strong position"  # Simplified
    
    def _assess_competitive_moat(self, info: Dict) -> str:
        return "Moderate moat"  # Simplified
    
    def _identify_competitive_advantages(self, info: Dict) -> List[str]:
        return ["Brand strength", "Technology", "Market position"]
    
    def _analyze_market_share(self, info: Dict) -> str:
        return "Significant market share"  # Simplified
    
    def _identify_competitive_threats(self, info: Dict) -> List[str]:
        return ["New entrants", "Technology disruption"]
    
    def _calculate_competitive_strength(self, info: Dict) -> float:
        return 75.0  # Simplified
    
    def _assess_market_perception(self, info: Dict) -> str:
        return "Positive"  # Simplified