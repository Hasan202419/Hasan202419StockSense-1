import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st

class HalalScreener:
    """Implements basic halal compliance screening for stocks"""
    
    def __init__(self):
        # Define prohibited business activities and sectors
        self.prohibited_sectors = {
            'gambling': ['Gambling', 'Casinos & Gaming'],
            'alcohol': ['Beverages—Wineries & Distilleries', 'Alcoholic Beverages'],
            'tobacco': ['Tobacco'],
            'adult_entertainment': ['Adult Entertainment'],
            'conventional_banking': ['Banks—Regional', 'Banks—Diversified'],
            'insurance': ['Insurance—Life', 'Insurance—Property & Casualty', 'Insurance—Diversified'],
            'weapons': ['Aerospace & Defense'],
            'pork': ['Farm Products', 'Packaged Foods']  # May need manual review
        }
        
        # Financial screening thresholds (simplified AAOIFI standards)
        self.financial_thresholds = {
            'debt_to_market_cap': 0.33,  # Total debt should not exceed 33% of market cap
            'interest_income_ratio': 0.05,  # Interest income should not exceed 5% of total income
            'non_compliant_income_ratio': 0.05,  # Non-compliant income should not exceed 5%
        }
    
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
