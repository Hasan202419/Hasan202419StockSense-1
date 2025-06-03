import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import streamlit as st

class DataFetcher:
    """Handles data fetching from Yahoo Finance API"""
    
    def __init__(self):
        self.cache_duration = 300  # 5 minutes cache for API calls
    
    @st.cache_data(ttl=300)
    def get_stock_info(_self, symbol: str) -> Optional[Dict]:
        """
        Fetch comprehensive stock information for a given symbol
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            Dict: Stock information or None if error
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            # Validate that we got valid data
            if not info or 'symbol' not in info:
                return None
                
            return info
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    @st.cache_data(ttl=300)
    def get_stock_history(_self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock price data
        
        Args:
            symbol (str): Stock ticker symbol
            period (str): Time period for historical data
            
        Returns:
            pd.DataFrame: Historical price data or None if error
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
                
            return hist
        except Exception as e:
            st.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    @st.cache_data(ttl=600)
    def get_multiple_stocks_info(_self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch information for multiple stocks
        
        Args:
            symbols (List[str]): List of stock ticker symbols
            
        Returns:
            Dict: Dictionary with symbol as key and stock info as value
        """
        results = {}
        progress_bar = st.progress(0)
        
        for i, symbol in enumerate(symbols):
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info
                
                if info and 'symbol' in info:
                    results[symbol.upper()] = info
                    
                progress_bar.progress((i + 1) / len(symbols))
            except Exception as e:
                st.warning(f"Could not fetch data for {symbol}: {str(e)}")
                continue
        
        progress_bar.empty()
        return results
    
    def get_financial_ratios(self, symbol: str) -> Optional[Dict]:
        """
        Calculate key financial ratios from stock info
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            Dict: Financial ratios or None if error
        """
        info = self.get_stock_info(symbol)
        if not info:
            return None
        
        try:
            ratios = {
                'debt_to_equity': info.get('debtToEquity', 0) / 100 if info.get('debtToEquity') else 0,
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),
                'profit_margin': info.get('profitMargins', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0)
            }
            
            return ratios
        except Exception as e:
            st.error(f"Error calculating ratios for {symbol}: {str(e)}")
            return None
    
    @st.cache_data(ttl=1800)  # 30 minutes cache for sector data
    def get_sp500_symbols(_self) -> List[str]:
        """
        Get S&P 500 stock symbols for screening
        
        Returns:
            List[str]: List of S&P 500 symbols
        """
        try:
            # Fetch S&P 500 companies from Wikipedia
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            symbols = sp500_table['Symbol'].tolist()
            
            # Clean symbols (remove dots for Yahoo Finance compatibility)
            cleaned_symbols = [symbol.replace('.', '-') for symbol in symbols]
            return cleaned_symbols[:100]  # Limit to first 100 for performance
            
        except Exception as e:
            st.error(f"Error fetching S&P 500 symbols: {str(e)}")
            # Fallback to a smaller list of common stocks
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
                'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'DIS', 'ADBE',
                'CRM', 'NFLX', 'KO', 'PEP', 'TMO', 'COST', 'ABBV', 'CVX', 'ACN',
                'LLY', 'MCD', 'ABT', 'AVGO', 'DHR', 'TXN', 'NEE', 'ORCL', 'VZ',
                'XOM', 'QCOM', 'BRK-B', 'NKE', 'PM', 'MRK', 'T', 'PFE', 'AMD',
                'HON', 'LOW', 'IBM', 'UPS', 'CAT', 'RTX'
            ]
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists and has valid data
        
        Args:
            symbol (str): Stock ticker symbol
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            
            # Check if we got valid data
            return bool(info and 'symbol' in info and info.get('regularMarketPrice'))
        except:
            return False
