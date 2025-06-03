import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io

# Import custom modules
from data_fetcher import DataFetcher
from halal_screener import HalalScreener
from technical_analysis import TechnicalAnalyzer

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
    return DataFetcher(), HalalScreener(), TechnicalAnalyzer()

data_fetcher, halal_screener, technical_analyzer = get_analyzers()

# Sidebar navigation
st.sidebar.title("🕌 Halal Stock Analysis")
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Navigate to:",
    [
        "🏠 Home",
        "🔍 Single Stock Analysis", 
        "📊 Halal Stock Screener",
        "💰 Penny Stock Finder",
        "📈 Market Research"
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

# Footer
st.markdown("---")
display_disclaimer()

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🕌 Halal Stock Screener & Technical Analysis Tool</p>
    <p>For educational purposes only • Always consult with qualified scholars and financial advisors</p>
</div>
""", unsafe_allow_html=True)
