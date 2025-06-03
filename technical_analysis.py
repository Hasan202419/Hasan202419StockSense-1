import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import streamlit as st

class TechnicalAnalyzer:
    """Provides technical analysis indicators and signals"""
    
    def __init__(self):
        self.indicators = {}
    
    def calculate_moving_averages(self, df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
        """
        Calculate simple moving averages
        
        Args:
            df (pd.DataFrame): Stock price data with 'Close' column
            periods (List[int]): List of periods for moving averages
            
        Returns:
            pd.DataFrame: DataFrame with moving averages added
        """
        result_df = df.copy()
        
        for period in periods:
            if len(df) >= period:
                result_df[f'MA_{period}'] = df['Close'].rolling(window=period).mean()
        
        return result_df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            df (pd.DataFrame): Stock price data with 'Close' column
            period (int): Period for RSI calculation
            
        Returns:
            pd.DataFrame: DataFrame with RSI added
        """
        result_df = df.copy()
        
        if len(df) < period:
            result_df['RSI'] = np.nan
            return result_df
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        result_df['RSI'] = 100 - (100 / (1 + rs))
        
        return result_df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df (pd.DataFrame): Stock price data with 'Close' column
            fast (int): Fast EMA period
            slow (int): Slow EMA period
            signal (int): Signal line EMA period
            
        Returns:
            pd.DataFrame: DataFrame with MACD indicators added
        """
        result_df = df.copy()
        
        if len(df) < slow:
            result_df['MACD'] = np.nan
            result_df['MACD_Signal'] = np.nan
            result_df['MACD_Histogram'] = np.nan
            return result_df
        
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        
        result_df['MACD'] = ema_fast - ema_slow
        result_df['MACD_Signal'] = result_df['MACD'].ewm(span=signal).mean()
        result_df['MACD_Histogram'] = result_df['MACD'] - result_df['MACD_Signal']
        
        return result_df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands
        
        Args:
            df (pd.DataFrame): Stock price data with 'Close' column
            period (int): Period for moving average and standard deviation
            std_dev (int): Number of standard deviations for bands
            
        Returns:
            pd.DataFrame: DataFrame with Bollinger Bands added
        """
        result_df = df.copy()
        
        if len(df) < period:
            result_df['BB_Upper'] = np.nan
            result_df['BB_Middle'] = np.nan
            result_df['BB_Lower'] = np.nan
            return result_df
        
        rolling_mean = df['Close'].rolling(window=period).mean()
        rolling_std = df['Close'].rolling(window=period).std()
        
        result_df['BB_Upper'] = rolling_mean + (rolling_std * std_dev)
        result_df['BB_Middle'] = rolling_mean
        result_df['BB_Lower'] = rolling_mean - (rolling_std * std_dev)
        
        return result_df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on technical indicators
        
        Args:
            df (pd.DataFrame): DataFrame with technical indicators
            
        Returns:
            pd.DataFrame: DataFrame with signals added
        """
        result_df = df.copy()
        
        # Initialize signal columns
        result_df['Signal'] = 'HOLD'
        result_df['Signal_Strength'] = 0
        
        signals = []
        
        # Moving Average Crossover Signals
        if 'MA_20' in df.columns and 'MA_50' in df.columns:
            ma20_above_ma50 = df['MA_20'] > df['MA_50']
            ma20_above_ma50_prev = df['MA_20'].shift(1) > df['MA_50'].shift(1)
            
            # Golden Cross (MA20 crosses above MA50)
            golden_cross = ma20_above_ma50 & ~ma20_above_ma50_prev
            # Death Cross (MA20 crosses below MA50)
            death_cross = ~ma20_above_ma50 & ma20_above_ma50_prev
            
            signals.append(golden_cross.astype(int) - death_cross.astype(int))
        
        # RSI Signals
        if 'RSI' in df.columns:
            rsi_oversold = df['RSI'] < 30
            rsi_overbought = df['RSI'] > 70
            rsi_signal = rsi_oversold.astype(int) - rsi_overbought.astype(int)
            signals.append(rsi_signal * 0.5)  # Lower weight for RSI
        
        # MACD Signals
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            macd_bullish = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
            macd_bearish = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
            macd_signal = macd_bullish.astype(int) - macd_bearish.astype(int)
            signals.append(macd_signal * 0.8)  # Higher weight for MACD
        
        # Combine signals
        if signals:
            combined_signal = sum(signals)
            
            # Determine signal strength and direction
            result_df.loc[combined_signal > 0.5, 'Signal'] = 'BUY'
            result_df.loc[combined_signal < -0.5, 'Signal'] = 'SELL'
            result_df['Signal_Strength'] = np.abs(combined_signal)
        
        return result_df
    
    def get_latest_signals(self, df: pd.DataFrame) -> Dict:
        """
        Get the latest technical analysis signals
        
        Args:
            df (pd.DataFrame): DataFrame with technical indicators and signals
            
        Returns:
            Dict: Latest signal information
        """
        if df.empty:
            return {'signal': 'NO DATA', 'strength': 0, 'indicators': {}}
        
        latest = df.iloc[-1]
        
        indicators = {}
        
        # Current price and moving averages
        indicators['current_price'] = latest.get('Close', 0)
        if 'MA_20' in df.columns:
            indicators['ma_20'] = latest.get('MA_20', 0)
        if 'MA_50' in df.columns:
            indicators['ma_50'] = latest.get('MA_50', 0)
        if 'MA_200' in df.columns:
            indicators['ma_200'] = latest.get('MA_200', 0)
        
        # RSI
        if 'RSI' in df.columns:
            rsi = latest.get('RSI', 50)
            indicators['rsi'] = rsi
            if rsi < 30:
                indicators['rsi_status'] = 'Oversold'
            elif rsi > 70:
                indicators['rsi_status'] = 'Overbought'
            else:
                indicators['rsi_status'] = 'Neutral'
        
        # MACD
        if 'MACD' in df.columns:
            indicators['macd'] = latest.get('MACD', 0)
            indicators['macd_signal'] = latest.get('MACD_Signal', 0)
            indicators['macd_histogram'] = latest.get('MACD_Histogram', 0)
        
        # Bollinger Bands
        if 'BB_Upper' in df.columns:
            indicators['bb_upper'] = latest.get('BB_Upper', 0)
            indicators['bb_middle'] = latest.get('BB_Middle', 0)
            indicators['bb_lower'] = latest.get('BB_Lower', 0)
            
            current_price = indicators['current_price']
            if current_price > indicators['bb_upper']:
                indicators['bb_status'] = 'Above Upper Band'
            elif current_price < indicators['bb_lower']:
                indicators['bb_status'] = 'Below Lower Band'
            else:
                indicators['bb_status'] = 'Within Bands'
        
        return {
            'signal': latest.get('Signal', 'HOLD'),
            'strength': latest.get('Signal_Strength', 0),
            'indicators': indicators
        }
    
    def create_technical_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """
        Create comprehensive technical analysis chart
        
        Args:
            df (pd.DataFrame): DataFrame with price data and indicators
            symbol (str): Stock symbol for chart title
            
        Returns:
            go.Figure: Plotly figure with technical analysis chart
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=[f'{symbol} - Price & Moving Averages', 'RSI', 'MACD'],
            row_width=[0.6, 0.2, 0.2]
        )
        
        # Price and Moving Averages
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Add moving averages
        colors = ['orange', 'blue', 'purple']
        ma_periods = [20, 50, 200]
        
        for i, period in enumerate(ma_periods):
            ma_col = f'MA_{period}'
            if ma_col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ma_col],
                        mode='lines',
                        name=f'MA {period}',
                        line=dict(color=colors[i], width=2)
                    ),
                    row=1, col=1
                )
        
        # Add Bollinger Bands if available
        if 'BB_Upper' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Upper'],
                    mode='lines',
                    name='BB Upper',
                    line=dict(color='gray', dash='dash'),
                    showlegend=False
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['BB_Lower'],
                    mode='lines',
                    name='BB Lower',
                    line=dict(color='gray', dash='dash'),
                    fill='tonexty',
                    fillcolor='rgba(128,128,128,0.1)',
                    showlegend=False
                ),
                row=1, col=1
            )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=2, col=1
            )
            
            # RSI reference lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        if 'MACD' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df['MACD'],
                    mode='lines',
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=3, col=1
            )
            
            if 'MACD_Signal' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df['MACD_Signal'],
                        mode='lines',
                        name='Signal Line',
                        line=dict(color='red')
                    ),
                    row=3, col=1
                )
            
            if 'MACD_Histogram' in df.columns:
                colors = ['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]
                fig.add_trace(
                    go.Bar(
                        x=df.index,
                        y=df['MACD_Histogram'],
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.6
                    ),
                    row=3, col=1
                )
        
        # Update layout
        fig.update_layout(
            title=f'Technical Analysis - {symbol}',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        return fig
    
    def identify_penny_stocks(self, stocks_data: Dict[str, Dict], threshold: float = 5.0) -> List[Dict]:
        """
        Identify penny stocks (stocks under specified threshold)
        
        Args:
            stocks_data (Dict): Dictionary of stock data
            threshold (float): Price threshold for penny stocks
            
        Returns:
            List[Dict]: List of penny stocks with analysis
        """
        penny_stocks = []
        
        for symbol, stock_info in stocks_data.items():
            if not stock_info:
                continue
                
            current_price = stock_info.get('regularMarketPrice', 0)
            
            if 0 < current_price <= threshold:
                # Calculate additional risk metrics
                market_cap = stock_info.get('marketCap', 0)
                volume = stock_info.get('averageVolume', 0)
                
                risk_level = 'High'
                if market_cap > 100e6 and volume > 100000:  # $100M+ market cap, 100K+ avg volume
                    risk_level = 'Medium'
                elif market_cap > 50e6 and volume > 50000:  # $50M+ market cap, 50K+ avg volume
                    risk_level = 'Medium-High'
                
                penny_stocks.append({
                    'symbol': symbol,
                    'price': current_price,
                    'market_cap': market_cap,
                    'volume': volume,
                    'risk_level': risk_level,
                    'sector': stock_info.get('sector', 'N/A'),
                    'industry': stock_info.get('industry', 'N/A')
                })
        
        # Sort by market cap (descending) to show more established penny stocks first
        penny_stocks.sort(key=lambda x: x['market_cap'], reverse=True)
        
        return penny_stocks
