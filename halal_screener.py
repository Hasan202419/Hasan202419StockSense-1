import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st
from datetime import datetime
import yfinance as yf

class HalalScreener:
    """Implements basic halal compliance screening for stocks"""
    
    def __init__(self):
        # Define prohibited business activities and sectors (Enhanced AAOIFI Standards)
        self.prohibited_sectors = {
            'gambling': ['Gambling', 'Casinos & Gaming', 'Gambling & Gaming'],
            'alcohol': ['Beverages—Wineries & Distilleries', 'Alcoholic Beverages', 'Brewers'],
            'tobacco': ['Tobacco', 'Cigarettes', 'Smoking Products'],
            'adult_entertainment': ['Adult Entertainment', 'Adult Content'],
            'conventional_banking': ['Banks—Regional', 'Banks—Diversified', 'Commercial Banks', 'Investment Banking'],
            'insurance': ['Insurance—Life', 'Insurance—Property & Casualty', 'Insurance—Diversified', 'Life Insurance'],
            'weapons': ['Aerospace & Defense', 'Defense', 'Military Equipment', 'Weapons Manufacturing'],
            'pork': ['Pork Products', 'Pig Farming'],
            'music_industry': ['Music Labels', 'Entertainment Studios'],
            'conventional_finance': ['Credit Services', 'Consumer Finance', 'Payday Lending']
        }
        
        # Enhanced AAOIFI financial screening thresholds
        self.financial_thresholds = {
            'debt_to_market_cap': 0.33,  # Total debt should not exceed 33% of market cap
            'debt_to_total_assets': 0.30,  # Debt to total assets ratio
            'interest_income_ratio': 0.05,  # Interest income should not exceed 5% of total income
            'non_compliant_income_ratio': 0.05,  # Non-compliant income should not exceed 5%
            'cash_and_interest_bearing_ratio': 0.33,  # Cash + interest bearing securities ratio
            'accounts_receivable_ratio': 0.45  # Accounts receivable ratio
        }
        
        # Halal investment categories
        self.halal_preferred_sectors = [
            'Technology', 'Healthcare', 'Consumer Goods', 'Utilities', 'Real Estate',
            'Manufacturing', 'Retail', 'Transportation', 'Food & Beverages', 'Telecommunications'
        ]
    
    def screen_business_activity(self, stock_info: Dict) -> Tuple[bool, str]:
        """
        Screen stock based on business activities
        
        Args:
            stock_info (Dict): Stock information from Yahoo Finance
            
        Returns:
            Tuple[bool, str]: (is_compliant, reason)
        """
        try:
            sector = stock_info.get('sector', '').lower()
            industry = stock_info.get('industry', '').lower()
            business_summary = stock_info.get('longBusinessSummary', '').lower()
            
            # Check prohibited sectors
            for category, sectors in self.prohibited_sectors.items():
                for prohibited_sector in sectors:
                    if prohibited_sector.lower() in industry or prohibited_sector.lower() in sector:
                        return False, f"Prohibited sector: {prohibited_sector}"
            
            # Check business summary for prohibited keywords
            prohibited_keywords = [
                'alcohol', 'gambling', 'casino', 'tobacco', 'cigarette',
                'adult entertainment', 'pornography', 'pork', 'bacon',
                'conventional banking', 'interest-based lending'
            ]
            
            for keyword in prohibited_keywords:
                if keyword in business_summary:
                    return False, f"Prohibited business activity: {keyword}"
            
            return True, "Business activity appears compliant"
            
        except Exception as e:
            return False, f"Error screening business activity: {str(e)}"
    
    def screen_financial_ratios(self, stock_info: Dict) -> Tuple[bool, List[str]]:
        """
        Screen stock based on financial ratios
        
        Args:
            stock_info (Dict): Stock information from Yahoo Finance
            
        Returns:
            Tuple[bool, List[str]]: (is_compliant, list of issues)
        """
        issues = []
        
        try:
            market_cap = stock_info.get('marketCap', 0)
            total_debt = stock_info.get('totalDebt', 0)
            
            # Debt-to-market cap ratio
            if market_cap > 0 and total_debt > 0:
                debt_ratio = total_debt / market_cap
                if debt_ratio > self.financial_thresholds['debt_to_market_cap']:
                    issues.append(f"High debt ratio: {debt_ratio:.2%} (limit: {self.financial_thresholds['debt_to_market_cap']:.0%})")
            
            # Additional financial checks
            debt_to_equity = stock_info.get('debtToEquity', 0)
            if debt_to_equity > 33:  # 33% threshold
                issues.append(f"High debt-to-equity ratio: {debt_to_equity:.1f}% (limit: 33%)")
            
            # Interest coverage ratio (if available)
            interest_coverage = stock_info.get('interestCoverage')
            if interest_coverage and interest_coverage < 2.5:
                issues.append(f"Low interest coverage ratio: {interest_coverage:.2f} (minimum: 2.5)")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error in financial screening: {str(e)}")
            return False, issues
    
    def calculate_compliance_score(self, stock_info: Dict) -> Dict:
        """
        Calculate an overall compliance score for the stock
        
        Args:
            stock_info (Dict): Stock information from Yahoo Finance
            
        Returns:
            Dict: Compliance analysis results
        """
        business_compliant, business_reason = self.screen_business_activity(stock_info)
        financial_compliant, financial_issues = self.screen_financial_ratios(stock_info)
        
        # Calculate overall score (0-100)
        score = 0
        if business_compliant:
            score += 60  # Business activity is most important
        if financial_compliant:
            score += 40  # Financial ratios
        elif len(financial_issues) == 1:
            score += 20  # Partial credit for minor issues
        
        # Determine compliance status
        if score >= 80:
            status = "Likely Compliant"
            color = "🟢"
        elif score >= 60:
            status = "Requires Review"
            color = "🟡"
        else:
            status = "Non-Compliant"
            color = "🔴"
        
        return {
            'symbol': stock_info.get('symbol', 'N/A'),
            'score': score,
            'status': status,
            'color': color,
            'business_compliant': business_compliant,
            'business_reason': business_reason,
            'financial_compliant': financial_compliant,
            'financial_issues': financial_issues,
            'sector': stock_info.get('sector', 'N/A'),
            'industry': stock_info.get('industry', 'N/A'),
            'market_cap': stock_info.get('marketCap', 0),
            'current_price': stock_info.get('regularMarketPrice', 0)
        }
    
    def screen_multiple_stocks(self, stocks_data: Dict[str, Dict]) -> pd.DataFrame:
        """
        Screen multiple stocks for halal compliance
        
        Args:
            stocks_data (Dict): Dictionary of stock data
            
        Returns:
            pd.DataFrame: Screening results
        """
        results = []
        
        for symbol, stock_info in stocks_data.items():
            if stock_info:  # Only process valid stock data
                compliance_result = self.calculate_compliance_score(stock_info)
                results.append(compliance_result)
        
        if not results:
            return pd.DataFrame()
        
        df = pd.DataFrame(results)
        
        # Sort by compliance score (descending)
        df = df.sort_values('score', ascending=False)
        
        # Format market cap for display
        df['market_cap_formatted'] = df['market_cap'].apply(self._format_market_cap)
        df['current_price_formatted'] = df['current_price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
        
        return df
    
    def _format_market_cap(self, market_cap: float) -> str:
        """Format market cap for display"""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}" if market_cap > 0 else "N/A"
    
    def get_screening_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for screening results
        
        Args:
            df (pd.DataFrame): Screening results dataframe
            
        Returns:
            Dict: Summary statistics
        """
        if df.empty:
            return {
                'total_stocks': 0,
                'compliant_stocks': 0,
                'requires_review': 0,
                'non_compliant': 0,
                'compliance_rate': 0
            }
        
        total = len(df)
        compliant = len(df[df['status'] == 'Likely Compliant'])
        review = len(df[df['status'] == 'Requires Review'])
        non_compliant = len(df[df['status'] == 'Non-Compliant'])
        
        return {
            'total_stocks': total,
            'compliant_stocks': compliant,
            'requires_review': review,
            'non_compliant': non_compliant,
            'compliance_rate': (compliant / total * 100) if total > 0 else 0
        }
    
    def get_halal_market_opportunities(self, stocks_data: Dict[str, Dict]) -> Dict:
        """
        Identify top halal investment opportunities with detailed analysis
        
        Args:
            stocks_data (Dict): Dictionary of stock data
            
        Returns:
            Dict: Comprehensive halal investment opportunities
        """
        halal_opportunities = {
            'top_halal_stocks': [],
            'shariah_compliant_growth': [],
            'ethical_dividend_stocks': [],
            'halal_penny_stocks': [],
            'sector_analysis': {},
            'compliance_summary': {}
        }
        
        # Screen all stocks for halal compliance
        screening_results = self.screen_multiple_stocks(stocks_data)
        
        if screening_results.empty:
            return halal_opportunities
        
        # Filter only compliant stocks
        compliant_stocks = screening_results[
            screening_results['status'].isin(['Likely Compliant', 'Requires Review'])
        ]
        
        if compliant_stocks.empty:
            return halal_opportunities
        
        # Categorize halal opportunities
        for _, stock in compliant_stocks.iterrows():
            symbol = stock['symbol']
            stock_info = stocks_data.get(symbol, {})
            
            if not stock_info:
                continue
            
            # Get additional metrics
            current_price = stock_info.get('regularMarketPrice', 0)
            market_cap = stock_info.get('marketCap', 0)
            pe_ratio = stock_info.get('trailingPE', 0)
            dividend_yield = stock_info.get('dividendYield', 0)
            
            stock_analysis = {
                'symbol': symbol,
                'company_name': stock_info.get('longName', symbol),
                'current_price': current_price,
                'market_cap': market_cap,
                'sector': stock['sector'],
                'compliance_score': stock['score'],
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield * 100 if dividend_yield else 0,
                'halal_grade': self._calculate_halal_grade(stock, stock_info)
            }
            
            # Categorize by investment type
            if current_price <= 5 and market_cap > 0:
                halal_opportunities['halal_penny_stocks'].append(stock_analysis)
            
            if dividend_yield and dividend_yield > 0.02:  # 2%+ dividend yield
                halal_opportunities['ethical_dividend_stocks'].append(stock_analysis)
            
            if market_cap > 1e9 and pe_ratio and pe_ratio < 25:  # Growth potential
                halal_opportunities['shariah_compliant_growth'].append(stock_analysis)
            
            # All high-scoring stocks
            if stock['score'] >= 85:
                halal_opportunities['top_halal_stocks'].append(stock_analysis)
        
        # Sort each category by compliance score
        for category in halal_opportunities:
            if isinstance(halal_opportunities[category], list):
                halal_opportunities[category] = sorted(
                    halal_opportunities[category],
                    key=lambda x: x['compliance_score'],
                    reverse=True
                )[:20]  # Top 20 in each category
        
        # Sector analysis
        halal_opportunities['sector_analysis'] = self._analyze_halal_sectors(compliant_stocks)
        
        # Compliance summary
        halal_opportunities['compliance_summary'] = {
            'total_analyzed': len(screening_results),
            'fully_compliant': len(screening_results[screening_results['score'] >= 85]),
            'requires_review': len(screening_results[screening_results['score'].between(60, 84)]),
            'avg_compliance_score': screening_results['score'].mean(),
            'top_halal_sectors': list(halal_opportunities['sector_analysis'].keys())[:5]
        }
        
        return halal_opportunities
    
    def _calculate_halal_grade(self, compliance_result: pd.Series, stock_info: Dict) -> str:
        """Calculate comprehensive halal investment grade"""
        score = compliance_result['score']
        
        # Additional factors for grading
        bonus_points = 0
        
        # Preferred sectors bonus
        sector = compliance_result.get('sector', '')
        if sector in self.halal_preferred_sectors:
            bonus_points += 5
        
        # Strong financials bonus
        debt_ratio = stock_info.get('debtToEquity', 0)
        if debt_ratio < 20:  # Low debt
            bonus_points += 5
        
        # ESG and social responsibility bonus
        if 'sustainable' in stock_info.get('longBusinessSummary', '').lower():
            bonus_points += 3
        
        final_score = min(100, score + bonus_points)
        
        if final_score >= 95:
            return 'A+'
        elif final_score >= 90:
            return 'A'
        elif final_score >= 85:
            return 'A-'
        elif final_score >= 80:
            return 'B+'
        elif final_score >= 75:
            return 'B'
        elif final_score >= 70:
            return 'B-'
        elif final_score >= 65:
            return 'C+'
        else:
            return 'C'
    
    def _analyze_halal_sectors(self, compliant_stocks: pd.DataFrame) -> Dict:
        """Analyze halal compliance by sector"""
        sector_analysis = {}
        
        for sector in compliant_stocks['sector'].unique():
            if sector and sector != 'N/A':
                sector_stocks = compliant_stocks[compliant_stocks['sector'] == sector]
                
                sector_analysis[sector] = {
                    'stock_count': len(sector_stocks),
                    'avg_compliance_score': sector_stocks['score'].mean(),
                    'fully_compliant_count': len(sector_stocks[sector_stocks['score'] >= 85]),
                    'compliance_rate': len(sector_stocks[sector_stocks['score'] >= 85]) / len(sector_stocks) * 100,
                    'top_stocks': sector_stocks.nlargest(3, 'score')['symbol'].tolist()
                }
        
        # Sort by compliance rate
        return dict(sorted(sector_analysis.items(), 
                          key=lambda x: x[1]['compliance_rate'], 
                          reverse=True))
    
    def generate_halal_investment_report(self, opportunities: Dict) -> str:
        """Generate comprehensive halal investment report"""
        summary = opportunities.get('compliance_summary', {})
        
        report = f"""
        # 🕌 Halal Investment Analysis Report
        
        **Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        ## 📊 Market Overview
        - **Total Stocks Analyzed:** {summary.get('total_analyzed', 0):,}
        - **Fully Shariah Compliant:** {summary.get('fully_compliant', 0)}
        - **Requires Scholar Review:** {summary.get('requires_review', 0)}
        - **Average Compliance Score:** {summary.get('avg_compliance_score', 0):.1f}/100
        
        ## 🎯 Top Investment Categories
        
        ### 1. Premium Halal Stocks (Grade A+/A)
        **Count:** {len(opportunities.get('top_halal_stocks', []))}
        - Highest AAOIFI compliance scores
        - Strong financial metrics
        - Preferred business activities
        
        ### 2. Ethical Dividend Stocks
        **Count:** {len(opportunities.get('ethical_dividend_stocks', []))}
        - Regular halal dividend income
        - Stable business models
        - Long-term wealth building
        
        ### 3. Shariah-Compliant Growth
        **Count:** {len(opportunities.get('shariah_compliant_growth', []))}
        - High growth potential
        - Technology and innovation focus
        - Future-oriented businesses
        
        ### 4. Halal Penny Stock Opportunities
        **Count:** {len(opportunities.get('halal_penny_stocks', []))}
        - Under $5 per share
        - Potential for significant returns
        - Higher risk, higher reward
        
        ## 🏭 Sector Analysis
        **Top Halal-Friendly Sectors:**
        """
        
        sector_analysis = opportunities.get('sector_analysis', {})
        for i, (sector, data) in enumerate(list(sector_analysis.items())[:5], 1):
            report += f"""
        {i}. **{sector}**
           - Compliance Rate: {data['compliance_rate']:.1f}%
           - Stock Count: {data['stock_count']}
           - Avg Score: {data['avg_compliance_score']:.1f}
            """
        
        report += """
        
        ## ⚖️ AAOIFI Compliance Notes
        - All recommendations follow AAOIFI Shariah standards
        - Business activity screening completed
        - Financial ratio analysis performed
        - Debt levels evaluated according to Islamic principles
        
        ## 🔍 Important Disclaimers
        - This analysis is for educational purposes only
        - Consult qualified Islamic scholars for final approval
        - Consider individual risk tolerance and investment goals
        - Regular monitoring of compliance status recommended
        
        ---
        *"And Allah has permitted trade and forbidden usury (riba)" - Quran 2:275*
        """
        
        return report
