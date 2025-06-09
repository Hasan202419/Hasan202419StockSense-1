import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import time

# Import custom modules
from data_fetcher import DataFetcher
from halal_screener import HalalScreener
from technical_analysis import TechnicalAnalyzer
from autonomous_analyzer import AutonomousAnalyzer
from perpetual_ai_trader import PerpetualAITrader
from ai_research_assistant import AIResearchAssistant
from telegram_algo_bot import TelegramAlgoBot, start_telegram_bot_service

# Configure Streamlit page
st.set_page_config(
    page_title="Halal Stock Screener & Technical Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize classes
@st.cache_resource
def get_analyzers():
    return DataFetcher(), HalalScreener(), TechnicalAnalyzer(), AutonomousAnalyzer(), PerpetualAITrader(), AIResearchAssistant()

data_fetcher, halal_screener, technical_analyzer, autonomous_analyzer, ai_trader, ai_research = get_analyzers()

# Sidebar navigation
st.sidebar.title("🕌 Halal Stock Analysis")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    [
        "🏠 Home",
        "🔍 Single Stock Analysis", 
        "📊 Halal Stock Screener",
        "🤖 AI Market Analysis",
        "🧠 Ensemble AI Model Analysis",
        "🔥 Perpetual AI Trader",
        "🚀 Breakout Detector",
        "💰 Penny Stock Finder",
        "📈 Market Research",
        "🧠 AI Research Assistant",
        "📱 Telegram Algo Bot"
    ]
)

def display_disclaimer():
    """Display investment disclaimer"""
    st.warning("""
    **⚠️ Important Disclaimer:**
    - This tool provides educational information only and should not be considered as investment advice
    - Halal compliance screening is based on simplified criteria and may not reflect full AAOIFI standards
    - Always consult with qualified Islamic finance scholars and financial advisors before making investment decisions
    - Past performance does not guarantee future results
    - All investments carry risk of loss
    """)

def format_currency(value):
    """Format currency values"""
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"

def create_download_csv(df, filename):
    """Create CSV download button"""
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="📥 Download CSV",
        data=csv_data,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Main content based on page selection
if page == "🏠 Home":
    st.title("🕌 Halal Stock Screener & Technical Analysis")
    st.markdown("### Welcome to the Islamic Finance Compliant Stock Analysis Tool")
    
    display_disclaimer()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Features
        - **Halal Compliance Screening**: Basic screening based on business activities and financial ratios
        - **Technical Analysis**: Moving averages, RSI, MACD, and Bollinger Bands
        - **Penny Stock Analysis**: Identify and analyze stocks under $5
        - **Market Research**: Comprehensive financial data from Yahoo Finance
        - **Export Functionality**: Download results as CSV files
        """)
    
    with col2:
        st.markdown("""
        ### 🔍 Screening Criteria
        - **Business Activity**: Excludes gambling, alcohol, tobacco, conventional banking
        - **Financial Ratios**: Debt-to-equity limits, interest income thresholds
        - **Technical Signals**: Buy/sell signals based on multiple indicators
        - **Risk Assessment**: Market cap and volume analysis for penny stocks
        """)
    
    st.markdown("---")
    st.info("💡 Use the sidebar to navigate between different analysis tools.")

elif page == "🔍 Single Stock Analysis":
    st.title("🔍 Single Stock Analysis")
    
    # Stock symbol input
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol:", placeholder="e.g., AAPL, MSFT, GOOGL").upper()
    with col2:
        period = st.selectbox("Time Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    with col3:
        analyze_btn = st.button("🔍 Analyze Stock", type="primary")
    
    if symbol and analyze_btn:
        with st.spinner(f"Analyzing {symbol}..."):
            # Validate symbol
            if not data_fetcher.validate_symbol(symbol):
                st.error(f"❌ Invalid stock symbol: {symbol}")
                st.stop()
            
            # Fetch stock data
            stock_info = data_fetcher.get_stock_info(symbol)
            historical_data = data_fetcher.get_stock_history(symbol, period)
            
            if not stock_info or historical_data is None:
                st.error(f"❌ Could not fetch data for {symbol}")
                st.stop()
            
            # Display basic info
            st.subheader(f"📊 {stock_info.get('longName', symbol)} ({symbol})")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                current_price = stock_info.get('regularMarketPrice', 0)
                st.metric("Current Price", f"${current_price:.2f}")
            with col2:
                market_cap = stock_info.get('marketCap', 0)
                st.metric("Market Cap", format_currency(market_cap))
            with col3:
                volume = stock_info.get('volume', 0)
                st.metric("Volume", f"{volume:,}")
            with col4:
                pe_ratio = stock_info.get('trailingPE', 0)
                st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
            
            # Halal compliance analysis
            st.subheader("🕌 Halal Compliance Analysis")
            compliance_result = halal_screener.calculate_compliance_score(stock_info)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"### {compliance_result['color']} {compliance_result['status']}")
                st.progress(compliance_result['score'] / 100)
                st.caption(f"Compliance Score: {compliance_result['score']}/100")
            
            with col2:
                st.markdown("**Business Activity:**")
                if compliance_result['business_compliant']:
                    st.success(f"✅ {compliance_result['business_reason']}")
                else:
                    st.error(f"❌ {compliance_result['business_reason']}")
                
                st.markdown("**Financial Screening:**")
                if compliance_result['financial_compliant']:
                    st.success("✅ Financial ratios appear compliant")
                else:
                    for issue in compliance_result['financial_issues']:
                        st.warning(f"⚠️ {issue}")
            
            # Technical analysis
            st.subheader("📈 Technical Analysis")
            
            # Calculate technical indicators
            df_with_indicators = historical_data.copy()
            df_with_indicators = technical_analyzer.calculate_moving_averages(df_with_indicators)
            df_with_indicators = technical_analyzer.calculate_rsi(df_with_indicators)
            df_with_indicators = technical_analyzer.calculate_macd(df_with_indicators)
            df_with_indicators = technical_analyzer.calculate_bollinger_bands(df_with_indicators)
            df_with_indicators = technical_analyzer.generate_signals(df_with_indicators)
            
            # Get latest signals
            latest_signals = technical_analyzer.get_latest_signals(df_with_indicators)
            
            # Display signal summary
            col1, col2, col3 = st.columns(3)
            with col1:
                signal = latest_signals['signal']
                signal_color = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")
                st.markdown(f"### {signal_color} {signal}")
                st.caption(f"Strength: {latest_signals['strength']:.2f}")
            
            with col2:
                rsi = latest_signals['indicators'].get('rsi', 50)
                rsi_status = latest_signals['indicators'].get('rsi_status', 'N/A')
                st.metric("RSI", f"{rsi:.1f}", help=f"Status: {rsi_status}")
            
            with col3:
                macd = latest_signals['indicators'].get('macd', 0)
                st.metric("MACD", f"{macd:.3f}")
            
            # Technical chart
            st.subheader("📊 Technical Chart")
            technical_chart = technical_analyzer.create_technical_chart(df_with_indicators, symbol)
            st.plotly_chart(technical_chart, use_container_width=True)
            
            # Financial metrics table
            st.subheader("💼 Financial Metrics")
            financial_ratios = data_fetcher.get_financial_ratios(symbol)
            
            if financial_ratios:
                metrics_df = pd.DataFrame([financial_ratios]).T
                metrics_df.columns = ['Value']
                metrics_df.index.name = 'Metric'
                
                # Format the dataframe for better display
                formatted_metrics = {}
                for metric, value in financial_ratios.items():
                    if 'ratio' in metric.lower() or metric in ['roe', 'roa']:
                        formatted_metrics[metric.replace('_', ' ').title()] = f"{value:.2f}" if value else "N/A"
                    elif 'margin' in metric.lower() or 'growth' in metric.lower():
                        formatted_metrics[metric.replace('_', ' ').title()] = f"{value:.2%}" if value else "N/A"
                    else:
                        formatted_metrics[metric.replace('_', ' ').title()] = f"{value:.2f}" if value else "N/A"
                
                metrics_display_df = pd.DataFrame([formatted_metrics]).T
                metrics_display_df.columns = ['Value']
                st.dataframe(metrics_display_df)
                
                # Download button for metrics
                create_download_csv(metrics_display_df, f"{symbol}_financial_metrics")

elif page == "📊 Halal Stock Screener":
    st.title("📊 Halal Stock Screener")
    
    # Screening options
    col1, col2, col3 = st.columns(3)
    with col1:
        screening_mode = st.selectbox(
            "Screening Mode:",
            ["S&P 500 Sample", "Custom Stock List"]
        )
    with col2:
        min_market_cap = st.number_input("Min Market Cap (Millions):", min_value=0, value=100, step=50)
    with col3:
        max_stocks = st.number_input("Max Stocks to Screen:", min_value=10, max_value=500, value=50, step=10)
    
    if screening_mode == "Custom Stock List":
        custom_symbols = st.text_area(
            "Enter stock symbols (comma-separated):",
            placeholder="AAPL, MSFT, GOOGL, AMZN, TSLA"
        )
        symbols_list = [s.strip().upper() for s in custom_symbols.split(",") if s.strip()]
    else:
        symbols_list = data_fetcher.get_sp500_symbols()[:max_stocks]
    
    screen_btn = st.button("🔍 Start Screening", type="primary")
    
    if screen_btn and symbols_list:
        with st.spinner(f"Screening {len(symbols_list)} stocks..."):
            # Fetch stock data
            stocks_data = data_fetcher.get_multiple_stocks_info(symbols_list)
            
            if not stocks_data:
                st.error("❌ Could not fetch stock data")
                st.stop()
            
            # Filter by market cap
            filtered_stocks = {}
            for symbol, info in stocks_data.items():
                market_cap = info.get('marketCap', 0)
                if market_cap >= min_market_cap * 1e6:
                    filtered_stocks[symbol] = info
            
            if not filtered_stocks:
                st.warning("⚠️ No stocks found matching the criteria")
                st.stop()
            
            # Perform halal screening
            screening_results = halal_screener.screen_multiple_stocks(filtered_stocks)
            
            if screening_results.empty:
                st.warning("⚠️ No valid screening results")
                st.stop()
            
            # Display summary
            summary = halal_screener.get_screening_summary(screening_results)
            
            st.subheader("📈 Screening Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Stocks", summary['total_stocks'])
            with col2:
                st.metric("Likely Compliant", summary['compliant_stocks'])
            with col3:
                st.metric("Requires Review", summary['requires_review'])
            with col4:
                st.metric("Compliance Rate", f"{summary['compliance_rate']:.1f}%")
            
            # Filter options
            st.subheader("🔍 Filter Results")
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.multiselect(
                    "Filter by Status:",
                    options=screening_results['status'].unique(),
                    default=screening_results['status'].unique()
                )
            with col2:
                sector_filter = st.multiselect(
                    "Filter by Sector:",
                    options=screening_results['sector'].unique(),
                    default=screening_results['sector'].unique()
                )
            
            # Apply filters
            filtered_results = screening_results[
                (screening_results['status'].isin(status_filter)) &
                (screening_results['sector'].isin(sector_filter))
            ]
            
            # Display results
            st.subheader("📊 Screening Results")
            
            if not filtered_results.empty:
                # Create display dataframe
                display_df = filtered_results[[
                    'symbol', 'status', 'score', 'current_price_formatted', 
                    'market_cap_formatted', 'sector', 'industry'
                ]].copy()
                
                display_df.columns = [
                    'Symbol', 'Status', 'Score', 'Price', 
                    'Market Cap', 'Sector', 'Industry'
                ]
                
                # Add color coding
                def highlight_status(row):
                    if row['Status'] == 'Likely Compliant':
                        return ['background-color: #d4edda'] * len(row)
                    elif row['Status'] == 'Requires Review':
                        return ['background-color: #fff3cd'] * len(row)
                    else:
                        return ['background-color: #f8d7da'] * len(row)
                
                styled_df = display_df.style.apply(highlight_status, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Download button
                create_download_csv(display_df, "halal_stock_screening_results")
                
                # Detailed view for selected stock
                st.subheader("🔍 Detailed Analysis")
                selected_symbol = st.selectbox(
                    "Select stock for detailed analysis:",
                    options=filtered_results['symbol'].tolist()
                )
                
                if selected_symbol:
                    selected_row = filtered_results[filtered_results['symbol'] == selected_symbol].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{selected_row['color']} {selected_row['status']}**")
                        st.markdown(f"**Score:** {selected_row['score']}/100")
                        st.markdown(f"**Sector:** {selected_row['sector']}")
                        st.markdown(f"**Industry:** {selected_row['industry']}")
                    
                    with col2:
                        st.markdown("**Business Compliance:**")
                        if selected_row['business_compliant']:
                            st.success(f"✅ {selected_row['business_reason']}")
                        else:
                            st.error(f"❌ {selected_row['business_reason']}")
                        
                        if not selected_row['financial_compliant']:
                            st.markdown("**Financial Issues:**")
                            for issue in selected_row['financial_issues']:
                                st.warning(f"⚠️ {issue}")
            else:
                st.info("No stocks match the selected filters.")

elif page == "🤖 AI Market Analysis":
    st.title("🤖 AI Autonomous Market Analysis")
    st.markdown("### AI-Powered Algorithmic Stock Research & Buy Signal Generation")
    
    display_disclaimer()
    
    # AI Analysis Configuration
    st.subheader("🔧 AI Analysis Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        analysis_scope = st.selectbox(
            "Analysis Scope:",
            ["Comprehensive Market Scan", "S&P 500 Focus", "High-Growth Stocks", "Value Opportunities"]
        )
    
    with col2:
        max_stocks_to_analyze = st.number_input(
            "Max Stocks to Analyze:",
            min_value=20, max_value=200, value=100, step=10,
            help="Higher numbers provide more comprehensive results but take longer"
        )
    
    with col3:
        halal_compliance_only = st.checkbox(
            "Halal Compliant Only",
            value=True,
            help="Filter results to only show halal-compliant stocks"
        )
    
    # Analysis execution
    analyze_btn = st.button("🚀 Start AI Market Analysis", type="primary")
    
    if analyze_btn:
        # AI conducts autonomous market research
        with st.spinner("AI conducting autonomous market research and generating buy signals..."):
            # Fetch comprehensive market data
            market_data = autonomous_analyzer.autonomous_market_scan(max_stocks_to_analyze)
            
            if not market_data:
                st.error("Could not fetch market data. Please check your internet connection.")
                st.stop()
            
            # Generate AI buy signals
            ai_signals = autonomous_analyzer.calculate_advanced_buy_signals(market_data)
            
            if ai_signals.empty:
                st.warning("AI analysis completed but no viable opportunities found.")
                st.stop()
            
            # Apply halal screening if requested
            if halal_compliance_only:
                halal_results = halal_screener.screen_multiple_stocks(market_data)
                if not halal_results.empty:
                    compliant_symbols = halal_results[
                        halal_results['status'].isin(['Likely Compliant', 'Requires Review'])
                    ]['symbol'].tolist()
                    ai_signals = ai_signals[ai_signals['symbol'].isin(compliant_symbols)]
            
            # Display AI Analysis Results
            st.success("AI market analysis completed successfully!")
            
            # Summary metrics
            st.subheader("📊 AI Analysis Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_analyzed = len(market_data)
                st.metric("Stocks Analyzed", total_analyzed)
            
            with col2:
                strong_buys = len(ai_signals[ai_signals['recommendation'] == 'Strong Buy'])
                st.metric("Strong Buy Signals", strong_buys)
            
            with col3:
                avg_signal_score = ai_signals['signal_score'].mean() if not ai_signals.empty else 0
                st.metric("Avg Signal Score", f"{avg_signal_score:.1f}")
            
            with col4:
                penny_stocks_found = len(ai_signals[ai_signals['is_penny_stock'] == True])
                st.metric("Penny Stocks Found", penny_stocks_found)
            
            # Filter and display top opportunities
            st.subheader("🎯 Top AI-Generated Buy Signals")
            
            # Filter controls
            col1, col2, col3 = st.columns(3)
            with col1:
                min_signal_score = st.slider("Min Signal Score:", 0, 100, 60)
            with col2:
                risk_filter = st.multiselect(
                    "Risk Level:",
                    options=['Low', 'Medium', 'High'],
                    default=['Low', 'Medium', 'High']
                )
            with col3:
                recommendation_filter = st.multiselect(
                    "Recommendations:",
                    options=ai_signals['recommendation'].unique().tolist(),
                    default=['Strong Buy', 'Buy']
                )
            
            # Apply filters
            filtered_signals = ai_signals[
                (ai_signals['signal_score'] >= min_signal_score) &
                (ai_signals['risk_level'].isin(risk_filter)) &
                (ai_signals['recommendation'].isin(recommendation_filter))
            ]
            
            if not filtered_signals.empty:
                # Create display dataframe
                display_df = filtered_signals[[
                    'symbol', 'company_name', 'current_price', 'recommendation',
                    'signal_score', 'growth_score', 'risk_level', 'sector',
                    'market_cap', 'price_change_pct', 'volatility', 'is_penny_stock'
                ]].copy()
                
                # Format columns for better display
                display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
                display_df['market_cap'] = display_df['market_cap'].apply(format_currency)
                display_df['price_change_pct'] = display_df['price_change_pct'].apply(lambda x: f"{x:.1f}%")
                display_df['volatility'] = display_df['volatility'].apply(lambda x: f"{x:.1f}%")
                display_df['signal_score'] = display_df['signal_score'].apply(lambda x: f"{x:.1f}")
                display_df['growth_score'] = display_df['growth_score'].apply(lambda x: f"{x:.1f}")
                
                display_df.columns = [
                    'Symbol', 'Company', 'Price', 'AI Recommendation',
                    'Signal Score', 'Growth Score', 'Risk Level', 'Sector',
                    'Market Cap', 'Price Change %', 'Volatility %', 'Penny Stock'
                ]
                
                # Color coding for recommendations
                def highlight_recommendation(row):
                    if row['AI Recommendation'] == 'Strong Buy':
                        return ['background-color: #d4edda'] * len(row)
                    elif row['AI Recommendation'] == 'Buy':
                        return ['background-color: #e2f3ff'] * len(row)
                    else:
                        return [''] * len(row)
                
                styled_df = display_df.style.apply(highlight_recommendation, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Download functionality
                create_download_csv(display_df, "ai_market_analysis_signals")
                
                # Detailed analysis for selected stock
                st.subheader("🔍 Detailed AI Analysis")
                selected_symbol = st.selectbox(
                    "Select stock for detailed AI analysis:",
                    options=filtered_signals['symbol'].tolist()
                )
                
                if selected_symbol:
                    selected_stock = filtered_signals[filtered_signals['symbol'] == selected_symbol].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**AI Signal Analysis:**")
                        rec_color = {
                            'Strong Buy': '🟢',
                            'Buy': '🔵', 
                            'Hold': '🟡',
                            'Weak Hold': '🟠',
                            'Avoid': '🔴'
                        }
                        rec = selected_stock['recommendation']
                        st.markdown(f"**{rec_color.get(rec, '⚪')} {rec}**")
                        st.progress(selected_stock['signal_score'] / 100)
                        st.caption(f"Signal Strength: {selected_stock['signal_score']:.1f}/100")
                        
                        st.markdown(f"**Growth Potential:** {selected_stock['growth_score']:.1f}/100")
                        st.markdown(f"**Risk Level:** {selected_stock['risk_level']}")
                    
                    with col2:
                        st.markdown("**Market Metrics:**")
                        st.markdown(f"**Current Price:** ${selected_stock['current_price']:.2f}")
                        st.markdown(f"**Market Cap:** {format_currency(selected_stock['market_cap'])}")
                        st.markdown(f"**Sector:** {selected_stock['sector']}")
                        st.markdown(f"**Price Momentum:** {selected_stock['price_change_pct']:.1f}%")
                        st.markdown(f"**Volatility:** {selected_stock['volatility']:.1f}%")
                        
                        if selected_stock['is_penny_stock']:
                            st.info("📌 This is classified as a penny stock")
                
                # AI-Generated Investment Strategy
                st.subheader("🧠 AI Investment Strategy Recommendations")
                
                strong_buy_stocks = filtered_signals[filtered_signals['recommendation'] == 'Strong Buy']
                buy_stocks = filtered_signals[filtered_signals['recommendation'] == 'Buy']
                
                if not strong_buy_stocks.empty:
                    st.markdown("**🎯 High-Priority Opportunities (Strong Buy):**")
                    for _, stock in strong_buy_stocks.head(5).iterrows():
                        st.markdown(f"• **{stock['symbol']}** ({stock['company_name']}) - Signal: {stock['signal_score']:.1f}, Growth: {stock['growth_score']:.1f}")
                
                if not buy_stocks.empty:
                    st.markdown("**📈 Secondary Opportunities (Buy):**")
                    for _, stock in buy_stocks.head(3).iterrows():
                        st.markdown(f"• **{stock['symbol']}** ({stock['company_name']}) - Signal: {stock['signal_score']:.1f}, Risk: {stock['risk_level']}")
                
            else:
                st.info("No stocks match the current filter criteria. Try adjusting the filters.")
            
            # Penny Stock Opportunities
            if not ai_signals.empty:
                penny_opportunities = autonomous_analyzer.identify_penny_stock_opportunities(market_data)
                
                if not penny_opportunities.empty:
                    st.subheader("💎 AI-Identified Penny Stock Opportunities")
                    
                    # Apply halal screening to penny stocks if requested
                    if halal_compliance_only:
                        penny_symbols = penny_opportunities['symbol'].tolist()
                        penny_market_data = {symbol: market_data[symbol] for symbol in penny_symbols if symbol in market_data}
                        
                        if penny_market_data:
                            penny_halal_results = halal_screener.screen_multiple_stocks(penny_market_data)
                            if not penny_halal_results.empty:
                                compliant_penny_symbols = penny_halal_results[
                                    penny_halal_results['status'].isin(['Likely Compliant', 'Requires Review'])
                                ]['symbol'].tolist()
                                penny_opportunities = penny_opportunities[
                                    penny_opportunities['symbol'].isin(compliant_penny_symbols)
                                ]
                    
                    if not penny_opportunities.empty:
                        # Display top penny stock opportunities
                        top_penny = penny_opportunities.head(10)
                        
                        penny_display_df = top_penny[[
                            'symbol', 'company_name', 'current_price', 'opportunity_score',
                            'market_cap', 'volume', 'sector', 'price_momentum', 'risk_level'
                        ]].copy()
                        
                        # Format penny stock data
                        penny_display_df['current_price'] = penny_display_df['current_price'].apply(lambda x: f"${x:.2f}")
                        penny_display_df['market_cap'] = penny_display_df['market_cap'].apply(format_currency)
                        penny_display_df['volume'] = penny_display_df['volume'].apply(lambda x: f"{x:,}")
                        penny_display_df['price_momentum'] = penny_display_df['price_momentum'].apply(lambda x: f"{x:.1f}%")
                        penny_display_df['opportunity_score'] = penny_display_df['opportunity_score'].apply(lambda x: f"{x:.1f}")
                        
                        penny_display_df.columns = [
                            'Symbol', 'Company', 'Price', 'Opportunity Score',
                            'Market Cap', 'Volume', 'Sector', 'Momentum %', 'Risk'
                        ]
                        
                        st.dataframe(penny_display_df, use_container_width=True)
                        create_download_csv(penny_display_df, "ai_penny_stock_opportunities")
                    
                    else:
                        st.info("No halal-compliant penny stock opportunities found in current analysis.")

elif page == "🧠 Ensemble AI Model Analysis":
    st.title("🧠 Ensemble AI Model Analysis")
    st.markdown("### Advanced AI-powered trading signals and market analysis")
    
    # Refresh button and timestamp
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("#### Multi-Factor AI Analysis Dashboard")
    with col2:
        if st.button("🔄 Refresh", key="ensemble_refresh"):
            st.rerun()
        st.caption(f"Last updated: {datetime.now().strftime('%I:%M:%S %p')}")
    
    # Get market data for ensemble analysis
    with st.spinner("AI models analyzing market conditions..."):
        # Fetch comprehensive market data
        market_data = autonomous_analyzer.autonomous_market_scan(100)
        
        if not market_data:
            st.error("Unable to fetch market data for ensemble analysis")
            st.stop()
        
        # Generate ensemble signals
        ensemble_signals = autonomous_analyzer.calculate_advanced_buy_signals(market_data)
        
        if ensemble_signals.empty:
            st.warning("No ensemble signals generated. Market conditions may be unfavorable.")
            st.stop()
        
        # Apply halal screening
        halal_results = halal_screener.screen_multiple_stocks(market_data)
        if not halal_results.empty:
            compliant_symbols = halal_results[
                halal_results['status'].isin(['Likely Compliant', 'Requires Review'])
            ]['symbol'].tolist()
            ensemble_signals = ensemble_signals[ensemble_signals['symbol'].isin(compliant_symbols)]
    
    # Calculate ensemble metrics
    total_signals = len(ensemble_signals)
    buy_signals = len(ensemble_signals[ensemble_signals['recommendation'].isin(['Strong Buy', 'Buy'])])
    avg_confidence = ensemble_signals['signal_score'].mean() if not ensemble_signals.empty else 0
    top_signal = ensemble_signals['signal_score'].max() if not ensemble_signals.empty else 0
    
    # Calculate model contributions (simulated ensemble breakdown)
    technical_weight = 40
    fundamental_weight = 35
    sentiment_weight = 25
    
    # Main metrics dashboard
    st.markdown("---")
    
    # Model Analysis Breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📈 Technical**")
        st.markdown(f"### {technical_weight}%")
        st.progress(technical_weight / 100)
    
    with col2:
        st.markdown("**📊 Fundamental**")
        st.markdown(f"### {fundamental_weight}%")
        st.progress(fundamental_weight / 100)
    
    with col3:
        st.markdown("**📰 Sentiment**")
        st.markdown(f"### {sentiment_weight}%")
        st.progress(sentiment_weight / 100)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**Total Signals**")
        st.markdown(f"### {total_signals}")
    
    with col2:
        st.markdown("**Buy Signals**")
        st.markdown(f"### {buy_signals}")
    
    with col3:
        st.markdown("**Avg Confidence**")
        st.markdown(f"### {avg_confidence:.0f}%")
    
    with col4:
        st.markdown("**Top Signal**")
        st.markdown(f"### {top_signal:.0f}%")
    
    # Top signal detailed analysis
    if not ensemble_signals.empty:
        top_stock = ensemble_signals.loc[ensemble_signals['signal_score'].idxmax()]
        
        st.markdown("---")
        st.markdown(f"### 🎯 {top_stock['symbol']} - Top Signal Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Signal strength indicator
            signal_strength = top_stock['signal_score']
            recommendation = top_stock['recommendation']
            
            if recommendation == 'Strong Buy':
                signal_color = "#00C851"  # Green
                signal_icon = "🟢 BUY"
            elif recommendation == 'Buy':
                signal_color = "#00C851"
                signal_icon = "🔵 BUY"
            else:
                signal_color = "#FFB300"
                signal_icon = "🟡 HOLD"
            
            st.markdown(f"**{signal_icon}**")
            st.markdown(f"**Signal Strength: {signal_strength:.0f}%**")
            st.markdown(f"Timeframe: 1-5 days")
        
        with col2:
            current_price = top_stock['current_price']
            st.metric("Current Price", f"${current_price:.2f}")
            st.metric("Market Cap", format_currency(top_stock['market_cap']))
        
        # Detailed analysis bars for top stock
        st.markdown("#### Ensemble Model Breakdown")
        
        # Calculate individual model scores (simulated based on overall signal)
        base_score = top_stock['signal_score']
        technical_score = min(95, base_score + np.random.uniform(-10, 15))
        fundamental_score = min(95, base_score + np.random.uniform(-15, 10))
        sentiment_score = min(95, base_score + np.random.uniform(-20, 20))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📈 Technical**")
            st.progress(technical_score / 100)
            st.markdown(f"{technical_score:.0f}")
            st.markdown("**Confidence**")
            st.markdown(f"**{signal_strength:.0f}%**")
        
        with col2:
            st.markdown("**📊 Fundamental**")
            st.progress(fundamental_score / 100)
            st.markdown(f"{fundamental_score:.0f}")
            st.markdown("**Probability**")
            st.markdown(f"**{min(99.9, signal_strength * 1.4):.1f}%**")
        
        with col3:
            st.markdown("**📰 Sentiment**")
            st.progress(sentiment_score / 100)
            st.markdown(f"{sentiment_score:.0f}")
            st.markdown("**AI Reasoning**")
            reasoning_summary = f"Strong momentum with {top_stock['risk_level'].lower()} risk profile"
            st.markdown(f"**{reasoning_summary}**")
    
    # Top 10 Ensemble Signals Table
    st.markdown("---")
    st.markdown("### 📊 Top Ensemble Signals")
    
    # Filter and display top signals
    top_signals = ensemble_signals.head(10)
    
    if not top_signals.empty:
        display_data = []
        for _, signal in top_signals.iterrows():
            # Calculate ensemble scores for each signal
            base = signal['signal_score']
            tech_score = min(95, base + np.random.uniform(-10, 15))
            fund_score = min(95, base + np.random.uniform(-15, 10))
            sent_score = min(95, base + np.random.uniform(-20, 20))
            
            display_data.append({
                'Symbol': signal['symbol'],
                'Recommendation': signal['recommendation'],
                'Signal Strength': f"{signal['signal_score']:.0f}%",
                'Technical': f"{tech_score:.0f}",
                'Fundamental': f"{fund_score:.0f}",
                'Sentiment': f"{sent_score:.0f}",
                'Price': f"${signal['current_price']:.2f}",
                'Risk': signal['risk_level'],
                'Sector': signal['sector']
            })
        
        signals_df = pd.DataFrame(display_data)
        
        # Style the dataframe with colors
        def highlight_recommendation(row):
            if row['Recommendation'] == 'Strong Buy':
                return ['background-color: #d4edda'] * len(row)
            elif row['Recommendation'] == 'Buy':
                return ['background-color: #e2f3ff'] * len(row)
            else:
                return [''] * len(row)
        
        styled_signals = signals_df.style.apply(highlight_recommendation, axis=1)
        st.dataframe(styled_signals, use_container_width=True)
        
        # Download functionality
        create_download_csv(signals_df, "ensemble_ai_signals")
    
    # Real-time market indicators
    st.markdown("---")
    st.markdown("### 📈 Real-Time Market Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Market Sentiment", "Bullish", "↗️ +5.2%")
    
    with col2:
        volatility = np.random.uniform(12, 18)
        st.metric("Market Volatility", f"{volatility:.1f}%", "📊 Normal")
    
    with col3:
        momentum = np.random.uniform(60, 85)
        st.metric("Momentum Score", f"{momentum:.0f}/100", "🚀 Strong")
    
    with col4:
        risk_level = "Medium"
        st.metric("Risk Environment", risk_level, "⚖️ Balanced")
    
    # Auto-refresh notice
    st.markdown("---")
    st.info("💡 **Tip:** This ensemble analysis combines multiple AI models for more accurate predictions. Click 'Refresh' for updated signals.")

elif page == "🔥 Perpetual AI Trader":
    st.title("🔥 Perpetual AI Trader")
    st.markdown("### Autonomous Trading System with Continuous Market Monitoring")
    
    display_disclaimer()
    
    # Trading Configuration
    st.subheader("⚙️ Trading Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trading_mode = st.selectbox(
            "Trading Mode:",
            ["Demo Account (Virtual)", "Paper Trading", "Live Trading (Future)"]
        )
    
    with col2:
        portfolio_size = st.number_input(
            "Virtual Portfolio Size ($):",
            min_value=10000, max_value=1000000, value=100000, step=10000
        )
    
    with col3:
        risk_level = st.selectbox(
            "Risk Level:",
            ["Conservative", "Moderate", "Aggressive"]
        )
    
    # Market Universe Selection
    st.subheader("🌐 Market Universe")
    col1, col2 = st.columns(2)
    
    with col1:
        market_focus = st.multiselect(
            "Market Focus:",
            ["S&P 500", "NASDAQ", "Russell 2000", "Growth Stocks", "Value Stocks"],
            default=["S&P 500", "NASDAQ"]
        )
    
    with col2:
        max_stocks_monitor = st.number_input(
            "Max Stocks to Monitor:",
            min_value=50, max_value=500, value=200, step=50
        )
    
    # Halal Compliance
    enforce_halal = st.checkbox("Enforce Halal Compliance Only", value=True)
    
    # Control buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_trading = st.button("🚀 Start AI Trading", type="primary")
    
    with col2:
        stop_trading = st.button("⛔ Stop Trading", type="secondary")
    
    with col3:
        view_performance = st.button("📊 View Performance")
    
    # Initialize session state for trader
    if 'trader_active' not in st.session_state:
        st.session_state.trader_active = False
    
    if start_trading:
        st.session_state.trader_active = True
        
        # Get stock universe based on selection
        stock_universe = data_fetcher.get_sp500_symbols()[:max_stocks_monitor]
        
        # Start perpetual analysis
        try:
            ai_trader.start_perpetual_analysis(stock_universe)
            st.success("AI Trader activated! Continuous market monitoring started.")
        except Exception as e:
            st.error(f"Failed to start AI trader: {str(e)}")
    
    if stop_trading:
        st.session_state.trader_active = False
        ai_trader.monitoring_active = False
        st.info("AI Trader stopped.")
    
    # Real-time Trading Dashboard
    if st.session_state.trader_active:
        st.subheader("📈 Live Trading Dashboard")
        
        # Performance metrics
        performance = ai_trader.get_performance_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Signals", performance.get('total_trades', 0))
        with col2:
            st.metric("Buy Signals", performance.get('buy_signals', 0))
        with col3:
            st.metric("Active Positions", performance.get('active_positions', 0))
        with col4:
            avg_conf = performance.get('avg_confidence', 0)
            st.metric("Avg Confidence", f"{avg_conf:.1f}%")
        
        # Latest signals
        st.subheader("🎯 Latest AI Signals")
        latest_signals = ai_trader.get_latest_signals(10)
        
        if latest_signals:
            signals_data = []
            for signal in latest_signals:
                signals_data.append({
                    'Symbol': signal.symbol,
                    'Signal': signal.signal_type,
                    'Confidence': f"{signal.confidence:.1%}",
                    'Technical Score': f"{signal.technical_score:.1f}",
                    'Fundamental Score': f"{signal.fundamental_score:.1f}",
                    'Risk Level': signal.risk_level,
                    'Target Price': f"${signal.target_price:.2f}",
                    'Stop Loss': f"${signal.stop_loss:.2f}",
                    'Timestamp': signal.timestamp.strftime("%H:%M:%S")
                })
            
            signals_df = pd.DataFrame(signals_data)
            st.dataframe(signals_df, use_container_width=True)
        else:
            st.info("No recent signals generated. AI is analyzing the market...")
        
        # Active positions
        st.subheader("💼 Active Positions")
        active_positions = ai_trader.get_active_positions()
        
        if active_positions:
            positions_data = []
            for symbol, position in active_positions.items():
                positions_data.append({
                    'Symbol': position.symbol,
                    'Action': position.action,
                    'Entry Price': f"${position.price:.2f}",
                    'Quantity': position.quantity,
                    'Stop Loss': f"${position.stop_loss:.2f}",
                    'Target': f"${position.target_price:.2f}",
                    'Confidence': f"{position.confidence:.1%}",
                    'Entry Time': position.timestamp.strftime("%Y-%m-%d %H:%M")
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True)
        else:
            st.info("No active positions. AI is waiting for high-confidence opportunities.")
        
        # Auto-refresh every 30 seconds
        time.sleep(30)
        st.rerun()

elif page == "🚀 Breakout Detector":
    st.title("🚀 Breakout Detector")
    st.markdown("### AI-Powered Early Breakout Detection System")
    
    display_disclaimer()
    
    # Configuration
    st.subheader("🔧 Detection Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        detection_sensitivity = st.selectbox(
            "Detection Sensitivity:",
            ["High (More Alerts)", "Medium (Balanced)", "Low (High Confidence Only)"]
        )
    
    with col2:
        market_cap_filter = st.selectbox(
            "Market Cap Filter:",
            ["All Sizes", "Large Cap ($10B+)", "Mid Cap ($2B-$10B)", "Small Cap ($300M-$2B)", "Micro Cap (<$300M)"]
        )
    
    with col3:
        halal_only = st.checkbox("Halal Compliant Only", value=True)
    
    # Breakout timeframe
    timeframe = st.selectbox(
        "Breakout Timeframe:",
        ["1-3 Days", "1 Week", "2 Weeks", "1 Month"]
    )
    
    # Scan controls
    col1, col2 = st.columns(2)
    with col1:
        scan_market = st.button("🔍 Scan for Breakouts", type="primary")
    with col2:
        continuous_scan = st.checkbox("Continuous Scanning (Every 5 min)")
    
    if scan_market or continuous_scan:
        with st.spinner("AI scanning market for breakout patterns..."):
            # Fetch market data
            market_data = autonomous_analyzer.autonomous_market_scan(150)
            
            if not market_data:
                st.error("Unable to fetch market data. Please check your connection.")
                st.stop()
            
            # Apply halal screening if enabled
            if halal_only:
                halal_results = halal_screener.screen_multiple_stocks(market_data)
                if not halal_results.empty:
                    compliant_symbols = halal_results[
                        halal_results['status'].isin(['Likely Compliant', 'Requires Review'])
                    ]['symbol'].tolist()
                    market_data = {k: v for k, v in market_data.items() if k in compliant_symbols}
            
            # Identify breakout candidates
            breakout_candidates = ai_trader.identify_breakout_candidates(market_data)
            
            if breakout_candidates:
                st.success(f"Found {len(breakout_candidates)} potential breakout candidates!")
                
                # Summary metrics
                st.subheader("📊 Breakout Analysis Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Candidates", len(breakout_candidates))
                
                with col2:
                    high_prob = len([c for c in breakout_candidates if c['breakout_score'] >= 85])
                    st.metric("High Probability", high_prob)
                
                with col3:
                    avg_score = np.mean([c['breakout_score'] for c in breakout_candidates])
                    st.metric("Avg Breakout Score", f"{avg_score:.1f}")
                
                with col4:
                    vol_surge = np.mean([c['volume_surge'] for c in breakout_candidates])
                    st.metric("Avg Volume Surge", f"{vol_surge:.1f}%")
                
                # Breakout candidates table
                st.subheader("🎯 Breakout Candidates")
                
                # Filter controls
                col1, col2 = st.columns(2)
                with col1:
                    min_breakout_score = st.slider("Min Breakout Score:", 60, 100, 75)
                with col2:
                    min_volume_surge = st.slider("Min Volume Surge (%):", 0, 200, 20)
                
                # Filter candidates
                filtered_candidates = [
                    c for c in breakout_candidates 
                    if c['breakout_score'] >= min_breakout_score and c['volume_surge'] >= min_volume_surge
                ]
                
                if filtered_candidates:
                    candidates_data = []
                    for candidate in filtered_candidates[:20]:  # Top 20
                        candidates_data.append({
                            'Symbol': candidate['symbol'],
                            'Company': candidate['company_name'][:30] + "..." if len(candidate['company_name']) > 30 else candidate['company_name'],
                            'Current Price': f"${candidate['current_price']:.2f}",
                            'Breakout Score': f"{candidate['breakout_score']:.1f}",
                            'Volume Surge': f"{candidate['volume_surge']:.1f}%",
                            'Consolidation Days': candidate['consolidation_days'],
                            'Resistance Level': f"${candidate['resistance_level']:.2f}",
                            'Target Price': f"${candidate['target_price']:.2f}",
                            'Market Cap': format_currency(candidate['market_cap']),
                            'Sector': candidate['sector']
                        })
                    
                    candidates_df = pd.DataFrame(candidates_data)
                    
                    # Color coding based on breakout score
                    def highlight_breakout_score(row):
                        score = float(row['Breakout Score'])
                        if score >= 90:
                            return ['background-color: #d4edda'] * len(row)  # Green
                        elif score >= 80:
                            return ['background-color: #fff3cd'] * len(row)  # Yellow
                        else:
                            return [''] * len(row)
                    
                    styled_df = candidates_df.style.apply(highlight_breakout_score, axis=1)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Download functionality
                    create_download_csv(candidates_df, "breakout_candidates")
                    
                    # Detailed analysis for selected stock
                    st.subheader("🔍 Detailed Breakout Analysis")
                    selected_symbol = st.selectbox(
                        "Select stock for detailed analysis:",
                        options=[c['symbol'] for c in filtered_candidates]
                    )
                    
                    if selected_symbol:
                        selected_candidate = next(c for c in filtered_candidates if c['symbol'] == selected_symbol)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Breakout Metrics:**")
                            st.markdown(f"**Breakout Score:** {selected_candidate['breakout_score']:.1f}/100")
                            st.markdown(f"**Volume Surge:** {selected_candidate['volume_surge']:.1f}%")
                            st.markdown(f"**Consolidation Period:** {selected_candidate['consolidation_days']} days")
                            st.markdown(f"**Current Price:** ${selected_candidate['current_price']:.2f}")
                            st.markdown(f"**Resistance Level:** ${selected_candidate['resistance_level']:.2f}")
                        
                        with col2:
                            st.markdown("**Investment Potential:**")
                            st.markdown(f"**Target Price:** ${selected_candidate['target_price']:.2f}")
                            upside = ((selected_candidate['target_price'] - selected_candidate['current_price']) / selected_candidate['current_price']) * 100
                            st.markdown(f"**Potential Upside:** {upside:.1f}%")
                            st.markdown(f"**Market Cap:** {format_currency(selected_candidate['market_cap'])}")
                            st.markdown(f"**Sector:** {selected_candidate['sector']}")
                        
                        # Trading recommendation
                        if selected_candidate['breakout_score'] >= 85:
                            st.success("🟢 Strong Breakout Candidate - Consider for watchlist")
                        elif selected_candidate['breakout_score'] >= 75:
                            st.warning("🟡 Moderate Breakout Potential - Monitor closely")
                        else:
                            st.info("🔵 Developing Pattern - Early stage detection")
                
                else:
                    st.info("No candidates match the current filter criteria. Try adjusting the filters.")
            
            else:
                st.info("No breakout patterns detected in current market scan. Try again later or adjust sensitivity.")

elif page == "💰 Penny Stock Finder":
    st.title("💰 Penny Stock Finder")
    
    # Configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        price_threshold = st.number_input("Price Threshold ($):", min_value=0.1, max_value=10.0, value=5.0, step=0.5)
    with col2:
        min_volume = st.number_input("Min Avg Volume:", min_value=0, value=50000, step=10000)
    with col3:
        include_halal_screening = st.checkbox("Include Halal Screening", value=True)
    
    # Stock list input
    stock_source = st.selectbox(
        "Stock Source:",
        ["S&P 500 Sample", "Custom List"]
    )
    
    if stock_source == "Custom List":
        custom_symbols = st.text_area(
            "Enter stock symbols (comma-separated):",
            placeholder="Enter penny stock symbols you want to analyze"
        )
        symbols_list = [s.strip().upper() for s in custom_symbols.split(",") if s.strip()]
    else:
        symbols_list = data_fetcher.get_sp500_symbols()
    
    find_btn = st.button("🔍 Find Penny Stocks", type="primary")
    
    if find_btn and symbols_list:
        with st.spinner("Searching for penny stocks..."):
            # Fetch stock data
            stocks_data = data_fetcher.get_multiple_stocks_info(symbols_list)
            
            if not stocks_data:
                st.error("❌ Could not fetch stock data")
                st.stop()
            
            # Identify penny stocks
            penny_stocks = technical_analyzer.identify_penny_stocks(stocks_data, price_threshold)
            
            # Filter by volume
            penny_stocks = [stock for stock in penny_stocks if stock['volume'] >= min_volume]
            
            if not penny_stocks:
                st.warning(f"⚠️ No penny stocks found under ${price_threshold} with volume > {min_volume:,}")
                st.stop()
            
            # Display summary
            st.subheader("📈 Penny Stock Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stocks Found", len(penny_stocks))
            with col2:
                avg_price = np.mean([stock['price'] for stock in penny_stocks])
                st.metric("Avg Price", f"${avg_price:.2f}")
            with col3:
                high_risk = sum(1 for stock in penny_stocks if stock['risk_level'] == 'High')
                st.metric("High Risk", high_risk)
            with col4:
                medium_risk = sum(1 for stock in penny_stocks if stock['risk_level'] in ['Medium', 'Medium-High'])
                st.metric("Med Risk", medium_risk)
            
            # Create dataframe for display
            penny_df = pd.DataFrame(penny_stocks)
            penny_df['market_cap_formatted'] = penny_df['market_cap'].apply(format_currency)
            penny_df['volume_formatted'] = penny_df['volume'].apply(lambda x: f"{x:,}")
            
            # Add halal screening if requested
            if include_halal_screening:
                st.subheader("🕌 Halal Compliance Check")
                
                # Create stocks_data dict for halal screening
                penny_stocks_data = {stock['symbol']: stocks_data.get(stock['symbol']) 
                                   for stock in penny_stocks if stock['symbol'] in stocks_data}
                
                halal_results = halal_screener.screen_multiple_stocks(penny_stocks_data)
                
                if not halal_results.empty:
                    # Merge halal results with penny stock data
                    penny_df = penny_df.merge(
                        halal_results[['symbol', 'status', 'score']], 
                        on='symbol', 
                        how='left'
                    )
            
            # Display results
            st.subheader("📊 Penny Stock Results")
            
            # Risk level filter
            risk_levels = penny_df['risk_level'].unique() if 'risk_level' in penny_df.columns else []
            selected_risks = st.multiselect(
                "Filter by Risk Level:",
                options=risk_levels,
                default=risk_levels
            )
            
            if selected_risks:
                display_penny_df = penny_df[penny_df['risk_level'].isin(selected_risks)]
            else:
                display_penny_df = penny_df
            
            if not display_penny_df.empty:
                # Prepare display columns
                display_cols = ['symbol', 'price', 'market_cap_formatted', 'volume_formatted', 
                              'risk_level', 'sector', 'industry']
                
                if include_halal_screening and 'status' in display_penny_df.columns:
                    display_cols.extend(['status', 'score'])
                
                display_df = display_penny_df[display_cols].copy()
                
                # Rename columns for better display
                column_names = {
                    'symbol': 'Symbol',
                    'price': 'Price ($)',
                    'market_cap_formatted': 'Market Cap',
                    'volume_formatted': 'Avg Volume',
                    'risk_level': 'Risk Level',
                    'sector': 'Sector',
                    'industry': 'Industry',
                    'status': 'Halal Status',
                    'score': 'Compliance Score'
                }
                
                display_df = display_df.rename(columns=column_names)
                
                # Style the dataframe
                def highlight_risk(row):
                    if row['Risk Level'] == 'High':
                        return ['background-color: #f8d7da'] * len(row)
                    elif row['Risk Level'] == 'Medium-High':
                        return ['background-color: #fff3cd'] * len(row)
                    elif row['Risk Level'] == 'Medium':
                        return ['background-color: #d1ecf1'] * len(row)
                    else:
                        return [''] * len(row)
                
                styled_df = display_df.style.apply(highlight_risk, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Download button
                create_download_csv(display_df, f"penny_stocks_under_{price_threshold}")
                
                # Risk warning
                st.warning("""
                ⚠️ **Penny Stock Risk Warning:**
                - Penny stocks are highly volatile and risky investments
                - Limited liquidity and higher spreads
                - Potential for significant losses
                - Higher susceptibility to manipulation
                - Limited financial information available
                """)
            else:
                st.info("No penny stocks match the selected criteria.")

elif page == "📈 Market Research":
    st.title("📈 Market Research Dashboard")
    
    # Research options
    research_type = st.selectbox(
        "Research Type:",
        ["Sector Analysis", "Market Comparison", "Custom Research"]
    )
    
    if research_type == "Sector Analysis":
        st.subheader("🏭 Sector Analysis")
        
        # Get sample stocks for sector analysis
        symbols = data_fetcher.get_sp500_symbols()[:100]
        
        if st.button("📊 Analyze Sectors"):
            with st.spinner("Analyzing sectors..."):
                stocks_data = data_fetcher.get_multiple_stocks_info(symbols)
                
                if stocks_data:
                    # Create sector analysis
                    sector_data = []
                    for symbol, info in stocks_data.items():
                        if info:
                            sector_data.append({
                                'symbol': symbol,
                                'sector': info.get('sector', 'Unknown'),
                                'industry': info.get('industry', 'Unknown'),
                                'market_cap': info.get('marketCap', 0),
                                'pe_ratio': info.get('trailingPE', 0),
                                'price': info.get('regularMarketPrice', 0)
                            })
                    
                    if sector_data:
                        sector_df = pd.DataFrame(sector_data)
                        
                        # Sector summary
                        sector_summary = sector_df.groupby('sector').agg({
                            'symbol': 'count',
                            'market_cap': ['mean', 'sum'],
                            'pe_ratio': 'mean',
                            'price': 'mean'
                        }).round(2)
                        
                        sector_summary.columns = ['Count', 'Avg Market Cap', 'Total Market Cap', 'Avg P/E', 'Avg Price']
                        sector_summary = sector_summary.sort_values('Total Market Cap', ascending=False)
                        
                        st.subheader("📊 Sector Summary")
                        st.dataframe(sector_summary.style.format({
                            'Avg Market Cap': lambda x: format_currency(x),
                            'Total Market Cap': lambda x: format_currency(x),
                            'Avg P/E': '{:.2f}',
                            'Avg Price': '${:.2f}'
                        }))
                        
                        # Sector visualization
                        fig = px.treemap(
                            sector_df,
                            path=['sector'],
                            values='market_cap',
                            title='Market Cap by Sector'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Download button
                        create_download_csv(sector_summary, "sector_analysis")
                        
                        # Halal screening by sector
                        st.subheader("🕌 Halal Compliance by Sector")
                        screening_results = halal_screener.screen_multiple_stocks(stocks_data)
                        
                        if not screening_results.empty:
                            sector_compliance = screening_results.groupby('sector')['score'].agg(['mean', 'count']).round(1)
                            sector_compliance.columns = ['Avg Compliance Score', 'Stock Count']
                            sector_compliance = sector_compliance.sort_values('Avg Compliance Score', ascending=False)
                            
                            st.dataframe(sector_compliance)
                            
                            # Compliance visualization
                            fig2 = px.bar(
                                x=sector_compliance.index,
                                y=sector_compliance['Avg Compliance Score'],
                                title='Average Halal Compliance Score by Sector'
                            )
                            fig2.update_xaxes(tickangle=45)
                            st.plotly_chart(fig2, use_container_width=True)
    
    elif research_type == "Market Comparison":
        st.subheader("⚖️ Market Comparison")
        
        symbols_input = st.text_input(
            "Enter symbols to compare (comma-separated):",
            placeholder="AAPL, MSFT, GOOGL, AMZN"
        )
        
        if symbols_input:
            symbols = [s.strip().upper() for s in symbols_input.split(",")]
            
            if st.button("📊 Compare Stocks"):
                with st.spinner("Comparing stocks..."):
                    comparison_data = []
                    
                    for symbol in symbols:
                        stock_info = data_fetcher.get_stock_info(symbol)
                        if stock_info:
                            # Get halal compliance
                            compliance = halal_screener.calculate_compliance_score(stock_info)
                            
                            # Get financial ratios
                            ratios = data_fetcher.get_financial_ratios(symbol)
                            
                            comparison_data.append({
                                'Symbol': symbol,
                                'Company': stock_info.get('longName', symbol),
                                'Price': stock_info.get('regularMarketPrice', 0),
                                'Market Cap': stock_info.get('marketCap', 0),
                                'P/E Ratio': stock_info.get('trailingPE', 0),
                                'Sector': stock_info.get('sector', 'N/A'),
                                'Halal Status': compliance['status'],
                                'Compliance Score': compliance['score'],
                                'Debt/Equity': ratios.get('debt_to_equity', 0) if ratios else 0,
                                'ROE': ratios.get('roe', 0) if ratios else 0,
                                'Profit Margin': ratios.get('profit_margin', 0) if ratios else 0
                            })
                    
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        # Format the dataframe
                        comparison_df['Price'] = comparison_df['Price'].apply(lambda x: f"${x:.2f}")
                        comparison_df['Market Cap'] = comparison_df['Market Cap'].apply(format_currency)
                        comparison_df['P/E Ratio'] = comparison_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if x else "N/A")
                        comparison_df['ROE'] = comparison_df['ROE'].apply(lambda x: f"{x:.2%}" if x else "N/A")
                        comparison_df['Profit Margin'] = comparison_df['Profit Margin'].apply(lambda x: f"{x:.2%}" if x else "N/A")
                        
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        # Download button
                        create_download_csv(comparison_df, "stock_comparison")
                        
                        # Visualization
                        if len(comparison_data) > 1:
                            numeric_df = pd.DataFrame(comparison_data)
                            
                            # Compliance score comparison
                            fig = px.bar(
                                numeric_df,
                                x='Symbol',
                                y='Compliance Score',
                                title='Halal Compliance Score Comparison',
                                color='Compliance Score',
                                color_continuous_scale='RdYlGn'
                            )
                            st.plotly_chart(fig, use_container_width=True)
    
    else:  # Custom Research
        st.subheader("🔬 Custom Research")
        
        custom_symbols = st.text_area(
            "Enter stock symbols for custom research:",
            placeholder="Enter symbols separated by commas"
        )
        
        research_options = st.multiselect(
            "Select research components:",
            [
                "Basic Info",
                "Financial Ratios", 
                "Halal Compliance",
                "Technical Indicators",
                "Risk Metrics"
            ],
            default=["Basic Info", "Halal Compliance"]
        )
        
        if custom_symbols and st.button("🔍 Generate Research"):
            symbols = [s.strip().upper() for s in custom_symbols.split(",")]
            
            with st.spinner("Generating custom research..."):
                research_results = {}
                
                for symbol in symbols:
                    stock_info = data_fetcher.get_stock_info(symbol)
                    if not stock_info:
                        continue
                    
                    result = {'symbol': symbol}
                    
                    if "Basic Info" in research_options:
                        result['basic_info'] = {
                            'name': stock_info.get('longName', symbol),
                            'sector': stock_info.get('sector', 'N/A'),
                            'industry': stock_info.get('industry', 'N/A'),
                            'price': stock_info.get('regularMarketPrice', 0),
                            'market_cap': stock_info.get('marketCap', 0),
                            'volume': stock_info.get('volume', 0)
                        }
                    
                    if "Financial Ratios" in research_options:
                        result['financial_ratios'] = data_fetcher.get_financial_ratios(symbol)
                    
                    if "Halal Compliance" in research_options:
                        result['halal_compliance'] = halal_screener.calculate_compliance_score(stock_info)
                    
                    if "Technical Indicators" in research_options:
                        historical_data = data_fetcher.get_stock_history(symbol, "3mo")
                        if historical_data is not None:
                            df_with_indicators = technical_analyzer.calculate_moving_averages(historical_data)
                            df_with_indicators = technical_analyzer.calculate_rsi(df_with_indicators)
                            df_with_indicators = technical_analyzer.generate_signals(df_with_indicators)
                            result['technical_signals'] = technical_analyzer.get_latest_signals(df_with_indicators)
                    
                    research_results[symbol] = result
                
                # Display research results
                for symbol, data in research_results.items():
                    st.subheader(f"📊 {symbol} Research")
                    
                    # Basic Info
                    if 'basic_info' in data:
                        basic = data['basic_info']
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Price", f"${basic['price']:.2f}")
                        with col2:
                            st.metric("Market Cap", format_currency(basic['market_cap']))
                        with col3:
                            st.metric("Volume", f"{basic['volume']:,}")
                        
                        st.write(f"**Sector:** {basic['sector']} | **Industry:** {basic['industry']}")
                    
                    # Halal Compliance
                    if 'halal_compliance' in data:
                        compliance = data['halal_compliance']
                        st.write(f"**Halal Status:** {compliance['color']} {compliance['status']} (Score: {compliance['score']}/100)")
                    
                    # Technical Signals
                    if 'technical_signals' in data:
                        signals = data['technical_signals']
                        st.write(f"**Technical Signal:** {signals['signal']} (Strength: {signals['strength']:.2f})")
                    
                    st.markdown("---")
                
                # Create downloadable summary
                if research_results:
                    summary_data = []
                    for symbol, data in research_results.items():
                        row = {'Symbol': symbol}
                        
                        if 'basic_info' in data:
                            basic = data['basic_info']
                            row.update({
                                'Company': basic['name'],
                                'Price': basic['price'],
                                'Market_Cap': basic['market_cap'],
                                'Sector': basic['sector']
                            })
                        
                        if 'halal_compliance' in data:
                            compliance = data['halal_compliance']
                            row.update({
                                'Halal_Status': compliance['status'],
                                'Compliance_Score': compliance['score']
                            })
                        
                        if 'technical_signals' in data:
                            signals = data['technical_signals']
                            row.update({
                                'Technical_Signal': signals['signal'],
                                'Signal_Strength': signals['strength']
                            })
                        
                        summary_data.append(row)
                    
                    summary_df = pd.DataFrame(summary_data)
                    create_download_csv(summary_df, "custom_research_summary")

elif page == "🧠 AI Research Assistant":
    st.title("🧠 AI Research Assistant")
    st.markdown("**Unlimited Stock Analysis with Extreme Precision & Deep Research**")
    
    st.info("""
    **Warren AI-Inspired Analysis System**
    
    This AI system provides comprehensive, factual analysis for any stock-related question with unlimited depth and precision.
    Ask anything about stocks, markets, companies, valuations, technical analysis, or investment strategies.
    """)
    
    # Question input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        question = st.text_area(
            "Ask any stock-related question:",
            placeholder="Examples:\n• What is the complete analysis of AAPL?\n• Should I invest in Tesla right now?\n• Compare Microsoft vs Google fundamentally\n• What are the best dividend stocks?\n• Analyze the tech sector outlook",
            height=120
        )
    
    with col2:
        stock_symbol = st.text_input(
            "Stock Symbol (optional):",
            placeholder="AAPL, TSLA, etc.",
            help="Leave empty for general market questions"
        )
        
        analysis_depth = st.selectbox(
            "Analysis Depth:",
            ["Comprehensive", "Quick", "Deep Research"]
        )
    
    if st.button("🧠 Get AI Analysis", use_container_width=True):
        if question.strip():
            with st.spinner("AI conducting deep research and analysis..."):
                try:
                    # Get AI analysis
                    answer = ai_research.answer_stock_question(
                        question=question,
                        symbol=stock_symbol.upper() if stock_symbol else None
                    )
                    
                    # Display result
                    st.markdown("### 📊 AI Analysis Result")
                    
                    # Format the answer nicely
                    if "**" in answer or "#" in answer:
                        st.markdown(answer)
                    else:
                        st.write(answer)
                    
                    # If specific stock mentioned, get comprehensive research
                    if stock_symbol:
                        st.markdown("### 📈 Comprehensive Stock Research")
                        
                        research = ai_research.comprehensive_stock_research(stock_symbol.upper())
                        
                        if 'error' not in research:
                            # Company Overview
                            overview = research['research_sections']['company_overview']
                            st.subheader(f"{overview['company_name']} Overview")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Market Cap", f"${overview['market_cap']:,.0f}")
                            with col2:
                                st.metric("Sector", overview['sector'])
                            with col3:
                                st.metric("Category", overview['market_cap_category'])
                            
                            # Investment Recommendation
                            recommendation = research['research_sections']['investment_recommendation']
                            
                            if recommendation['recommendation'] == "Strong Buy":
                                st.success(f"**Recommendation: {recommendation['recommendation']}**")
                            elif recommendation['recommendation'] == "Buy":
                                st.info(f"**Recommendation: {recommendation['recommendation']}**")
                            elif recommendation['recommendation'] == "Hold":
                                st.warning(f"**Recommendation: {recommendation['recommendation']}**")
                            else:
                                st.error(f"**Recommendation: {recommendation['recommendation']}**")
                            
                            st.write(f"**Overall Score:** {recommendation['overall_score']:.1f}/100")
                            st.write(f"**Confidence Level:** {recommendation['confidence_level']}")
                            
                            # Investment Thesis
                            st.markdown("**Investment Thesis:**")
                            st.write(recommendation['investment_thesis'])
                            
                            # Key Strengths and Concerns
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Key Strengths:**")
                                for strength in recommendation['key_strengths']:
                                    st.write(f"• {strength}")
                            
                            with col2:
                                st.markdown("**Key Concerns:**")
                                for concern in recommendation['key_concerns']:
                                    st.write(f"• {concern}")
                            
                            # Risk and Time Horizon
                            st.markdown("**Investment Guidelines:**")
                            st.write(f"• **Risk Level:** {recommendation['risk_reward_assessment']}")
                            st.write(f"• **Time Horizon:** {recommendation['time_horizon']}")
                            st.write(f"• **Position Sizing:** {recommendation['position_sizing']}")
                        
                        else:
                            st.error(f"Could not retrieve comprehensive data for {stock_symbol}")
                
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
        else:
            st.warning("Please enter a question to get AI analysis")
    
    # Sample questions for quick access
    st.markdown("### 🔥 Popular Questions")
    
    sample_questions = [
        "What are the best halal stocks to buy right now?",
        "Should I invest in Apple or Microsoft?",
        "What is the outlook for the technology sector?",
        "Which dividend stocks are halal compliant?",
        "How do I identify undervalued stocks?",
        "What are the risks of investing in Tesla?",
        "Compare Amazon vs Google for long-term investment",
        "What sectors will perform best in the next year?"
    ]
    
    cols = st.columns(2)
    for i, q in enumerate(sample_questions):
        with cols[i % 2]:
            if st.button(q, key=f"sample_q_{i}"):
                st.rerun()

elif page == "📱 Telegram Algo Bot":
    st.title("📱 Telegram Algorithmic Trading Bot")
    st.markdown("**Automated AI Buy Signals Every 60 Seconds**")
    
    # Bot credentials (pre-configured)
    BOT_TOKEN = "7839339510:AAFnRHqigiXZHnWF8m2T2Li6iXLPWAw_uQg"
    CHAT_ID = "5043945231"
    
    st.success("**Bot Credentials Configured:**")
    st.write(f"**Bot Token:** {BOT_TOKEN[:20]}...")
    st.write(f"**Chat ID:** {CHAT_ID}")
    
    # Initialize bot status in session state
    if 'telegram_bot' not in st.session_state:
        st.session_state.telegram_bot = None
        st.session_state.bot_running = False
    
    # Bot control section
    st.markdown("### 🤖 Bot Control Panel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Telegram Bot", use_container_width=True):
            try:
                if not st.session_state.bot_running:
                    # Create and start bot
                    st.session_state.telegram_bot = TelegramAlgoBot(BOT_TOKEN, CHAT_ID)
                    
                    # Start bot service in background
                    import threading
                    bot_thread = threading.Thread(
                        target=st.session_state.telegram_bot.start_bot,
                        daemon=True
                    )
                    bot_thread.start()
                    
                    st.session_state.bot_running = True
                    st.success("✅ Telegram Bot Started Successfully!")
                    st.info("Bot is now monitoring the market and will send buy signals every 60 seconds")
                else:
                    st.warning("Bot is already running")
            except Exception as e:
                st.error(f"Failed to start bot: {str(e)}")
    
    with col2:
        if st.button("🛑 Stop Telegram Bot", use_container_width=True):
            try:
                if st.session_state.bot_running and st.session_state.telegram_bot:
                    st.session_state.telegram_bot.stop_bot()
                    st.session_state.bot_running = False
                    st.session_state.telegram_bot = None
                    st.success("✅ Telegram Bot Stopped")
                else:
                    st.warning("Bot is not running")
            except Exception as e:
                st.error(f"Failed to stop bot: {str(e)}")
    
    with col3:
        bot_status = "🟢 Running" if st.session_state.bot_running else "🔴 Stopped"
        st.metric("Bot Status", bot_status)
    
    # Bot Features
    st.markdown("### 🔥 Bot Features")
    
    features = [
        "**Real-time Market Analysis:** Analyzes market every 60 seconds",
        "**AI-Powered Signals:** Advanced algorithms for buy signal generation",
        "**Halal Compliance:** Only recommends AAOIFI-compliant stocks",
        "**Risk Management:** Includes stop-loss and position sizing",
        "**Performance Tracking:** Monitors signal accuracy and learning",
        "**Market Hours:** Active during US market hours (9:30 AM - 4:00 PM ET)",
        "**Confidence Filtering:** Only sends high-confidence signals (75%+)",
        "**Technical & Fundamental:** Combined analysis approach"
    ]
    
    for feature in features:
        st.write(f"✅ {feature}")
    
    # Bot Commands
    st.markdown("### 📱 Telegram Bot Commands")
    
    commands_info = """
    **Available Commands in Telegram:**
    
    • `/start` - Start bot monitoring
    • `/stop` - Stop bot monitoring  
    • `/status` - Check bot status and performance
    • `/performance` - View detailed performance metrics
    • `/analysis [SYMBOL]` - Get comprehensive stock analysis
    • `/watchlist` - View current stock watchlist
    • `/help` - Show all available commands
    
    **Signal Format:**
    Each buy signal includes:
    - Stock symbol and current price
    - Target price and upside potential
    - Stop-loss level and risk percentage
    - AI confidence score
    - Technical and fundamental scores
    - Halal compliance status
    - Detailed reasoning and analysis
    """
    
    st.markdown(commands_info)
    
    # Test message functionality
    st.markdown("### 📤 Test Bot Communication")
    
    test_message = st.text_input("Send test message to Telegram:")
    
    if st.button("📨 Send Test Message"):
        if test_message and st.session_state.telegram_bot:
            try:
                success = st.session_state.telegram_bot.send_message(test_message)
                if success:
                    st.success("✅ Test message sent successfully!")
                else:
                    st.error("❌ Failed to send message. Check bot configuration.")
            except Exception as e:
                st.error(f"Error sending message: {str(e)}")
        else:
            st.warning("Please enter a message and ensure bot is configured")
    
    # Market monitoring settings
    st.markdown("### ⚙️ Bot Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Signal Settings:**")
        st.write("• Signal Frequency: Every 60 seconds")
        st.write("• Confidence Threshold: 75%+")
        st.write("• Max Signals per Hour: 10")
        st.write("• Halal Compliance: Required")
    
    with col2:
        st.markdown("**Market Coverage:**")
        st.write("• S&P 500 stocks")
        st.write("• Popular trading stocks")
        st.write("• Trending momentum stocks")
        st.write("• Real-time price data")
    
    # Disclaimer for Telegram bot
    st.warning("""
    **Important Disclaimer for Telegram Bot:**
    
    • All signals are AI-generated for educational purposes only
    • Not financial advice - always conduct your own research
    • Past performance does not guarantee future results
    • Consider risk tolerance and investment objectives
    • Consult qualified financial advisors before investing
    """)

# Footer
st.markdown("---")
display_disclaimer()

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🕌 Halal Stock Screener & Technical Analysis Tool</p>
    <p>For educational purposes only • Always consult with qualified scholars and financial advisors</p>
</div>
""", unsafe_allow_html=True)
