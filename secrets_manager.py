
import os
import streamlit as st
from typing import Dict, Optional
import requests

class SecretsManager:
    """Manage API keys and sensitive configuration"""
    
    def __init__(self):
        self.required_secrets = {
            'ALPHA_VANTAGE_API_KEY': 'For advanced market data and news sentiment',
            'FINNHUB_API_KEY': 'For real-time stock data and insider trading info',
            'POLYGON_API_KEY': 'For options flow and unusual volume detection',
            'NEWS_API_KEY': 'For news sentiment analysis and spike detection',
            'QUANDL_API_KEY': 'For economic calendar and macro data',
            'TELEGRAM_BOT_TOKEN': 'For Telegram trading alerts',
            'TELEGRAM_CHAT_ID': 'For Telegram message destination',
            'OPENAI_API_KEY': 'For advanced AI analysis (optional)',
            'RAPIDAPI_KEY': 'For additional financial data sources'
        }
        
        self.optional_secrets = {
            'DISCORD_WEBHOOK_URL': 'For Discord trading alerts',
            'SLACK_WEBHOOK_URL': 'For Slack trading notifications',
            'EMAIL_API_KEY': 'For email alerts',
            'TWILIO_API_KEY': 'For SMS alerts'
        }
    
    def check_secrets_configuration(self) -> Dict[str, bool]:
        """Check which secrets are configured"""
        status = {}
        
        for key in self.required_secrets.keys():
            status[key] = bool(os.getenv(key))
        
        for key in self.optional_secrets.keys():
            status[key] = bool(os.getenv(key))
        
        return status
    
    def get_secret(self, key: str) -> Optional[str]:
        """Safely get a secret value"""
        return os.getenv(key)
    
    def display_secrets_status(self):
        """Display secrets configuration status in Streamlit"""
        st.subheader("🔐 API Keys & Secrets Configuration")
        
        status = self.check_secrets_configuration()
        
        st.markdown("### Required APIs")
        for key, description in self.required_secrets.items():
            is_configured = status.get(key, False)
            icon = "✅" if is_configured else "❌"
            st.markdown(f"{icon} **{key}**: {description}")
        
        st.markdown("### Optional APIs")
        for key, description in self.optional_secrets.items():
            is_configured = status.get(key, False)
            icon = "✅" if is_configured else "⭕"
            st.markdown(f"{icon} **{key}**: {description}")
        
        # Configuration instructions
        st.markdown("### 🛠️ Configuration Instructions")
        st.info("""
        **To configure secrets:**
        1. Go to the Secrets tab in your Replit workspace
        2. Add each API key as a new secret
        3. Use the exact key names shown above
        4. Get API keys from respective providers:
           - Alpha Vantage: alphavantage.co
           - Finnhub: finnhub.io
           - Polygon: polygon.io
           - News API: newsapi.org
           - Quandl: data.nasdaq.com
        """)
        
        return status
    
    def get_configured_capabilities(self) -> Dict[str, bool]:
        """Return available system capabilities based on configured secrets"""
        status = self.check_secrets_configuration()
        
        capabilities = {
            'advanced_market_data': status.get('ALPHA_VANTAGE_API_KEY', False),
            'real_time_data': status.get('FINNHUB_API_KEY', False),
            'options_flow_analysis': status.get('POLYGON_API_KEY', False),
            'news_sentiment': status.get('NEWS_API_KEY', False),
            'economic_calendar': status.get('QUANDL_API_KEY', False),
            'telegram_alerts': status.get('TELEGRAM_BOT_TOKEN', False) and status.get('TELEGRAM_CHAT_ID', False),
            'ai_enhanced_analysis': status.get('OPENAI_API_KEY', False),
            'discord_alerts': status.get('DISCORD_WEBHOOK_URL', False),
            'email_alerts': status.get('EMAIL_API_KEY', False)
        }
        
        return capabilities
    
    def setup_api_key_guide(self):
        """Provide step-by-step API key setup guide"""
        st.markdown("### 🚀 Complete API Key Setup Guide")
        
        with st.expander("📋 Step 1: Access Replit Secrets", expanded=True):
            st.markdown("""
            1. **Find the Secrets tab** in your Replit workspace sidebar
            2. **Click on 'Secrets'** (lock icon 🔐)
            3. **Click '+ New Secret'** to add each API key
            
            **Important:** Use the EXACT key names shown below (case-sensitive)
            """)
        
        with st.expander("🔑 Step 2: Get Your API Keys", expanded=False):
            api_sources = {
                'ALPHA_VANTAGE_API_KEY': {
                    'website': 'alphavantage.co',
                    'description': 'FREE - Get real-time stock data, technical indicators',
                    'signup': 'Sign up → Get API Key → Copy key'
                },
                'FINNHUB_API_KEY': {
                    'website': 'finnhub.io',
                    'description': 'FREE - Real-time market data, insider trading data',
                    'signup': 'Register → Dashboard → API Keys → Copy'
                },
                'NEWS_API_KEY': {
                    'website': 'newsapi.org',
                    'description': 'FREE - News sentiment analysis for stocks',
                    'signup': 'Get API Key → Copy your key'
                },
                'TELEGRAM_BOT_TOKEN': {
                    'website': 'Telegram @BotFather',
                    'description': 'FREE - Create bot for trading alerts',
                    'signup': 'Message @BotFather → /newbot → Copy token'
                },
                'POLYGON_API_KEY': {
                    'website': 'polygon.io',
                    'description': 'Advanced options flow and volume analysis',
                    'signup': 'Sign up → Get API Key'
                }
            }
            
            for key, info in api_sources.items():
                st.markdown(f"**{key}**")
                st.write(f"• Website: {info['website']}")
                st.write(f"• Purpose: {info['description']}")
                st.write(f"• Setup: {info['signup']}")
                st.markdown("---")
        
        with st.expander("⚙️ Step 3: Configure Secrets in Replit", expanded=False):
            st.markdown("""
            **For each API key:**
            
            1. Go to **Secrets** tab in Replit
            2. Click **+ New Secret**
            3. Enter **Key name** exactly as shown below
            4. Paste your **API key value**
            5. Click **Add Secret**
            
            **Essential Configuration:**
            """)
            
            required_keys = [
                "ALPHA_VANTAGE_API_KEY",
                "FINNHUB_API_KEY", 
                "NEWS_API_KEY",
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_CHAT_ID"
            ]
            
            for key in required_keys:
                st.code(f"Key: {key}\nValue: [Your API Key Here]")
    
    def test_all_apis(self):
        """Test all configured API connections"""
        st.markdown("### 🧪 API Connection Testing")
        
        test_results = {}
        status = self.check_secrets_configuration()
        
        # Test Alpha Vantage
        if status.get('ALPHA_VANTAGE_API_KEY'):
            try:
                api_key = self.get_secret('ALPHA_VANTAGE_API_KEY')
                test_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={api_key}"
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200 and 'Global Quote' in response.text:
                    test_results['Alpha Vantage'] = "✅ Connected Successfully"
                else:
                    test_results['Alpha Vantage'] = "❌ Invalid API Key or Quota Exceeded"
            except:
                test_results['Alpha Vantage'] = "❌ Connection Failed"
        else:
            test_results['Alpha Vantage'] = "⚪ Not Configured"
        
        # Test Finnhub
        if status.get('FINNHUB_API_KEY'):
            try:
                api_key = self.get_secret('FINNHUB_API_KEY')
                test_url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={api_key}"
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    test_results['Finnhub'] = "✅ Connected Successfully"
                else:
                    test_results['Finnhub'] = "❌ Invalid API Key"
            except:
                test_results['Finnhub'] = "❌ Connection Failed"
        else:
            test_results['Finnhub'] = "⚪ Not Configured"
        
        # Test News API
        if status.get('NEWS_API_KEY'):
            try:
                api_key = self.get_secret('NEWS_API_KEY')
                test_url = f"https://newsapi.org/v2/everything?q=apple&apiKey={api_key}&pageSize=1"
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    test_results['News API'] = "✅ Connected Successfully"
                else:
                    test_results['News API'] = "❌ Invalid API Key"
            except:
                test_results['News API'] = "❌ Connection Failed"
        else:
            test_results['News API'] = "⚪ Not Configured"
        
        # Test Telegram Bot
        if status.get('TELEGRAM_BOT_TOKEN'):
            try:
                bot_token = self.get_secret('TELEGRAM_BOT_TOKEN')
                test_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                response = requests.get(test_url, timeout=10)
                if response.status_code == 200:
                    test_results['Telegram Bot'] = "✅ Bot Token Valid"
                else:
                    test_results['Telegram Bot'] = "❌ Invalid Bot Token"
            except:
                test_results['Telegram Bot'] = "❌ Connection Failed"
        else:
            test_results['Telegram Bot'] = "⚪ Not Configured"
        
        # Display results
        for api_name, result in test_results.items():
            st.write(f"**{api_name}:** {result}")
        
        return test_results
    
    def generate_sample_secrets(self):
        """Generate sample secrets configuration"""
        st.markdown("### 📝 Sample Secrets Configuration")
        st.markdown("Copy these exact key names to your Replit Secrets:")
        
        sample_config = """
# Core Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here
NEWS_API_KEY=your_news_api_key_here

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Advanced APIs (Optional)
POLYGON_API_KEY=your_polygon_key_here
QUANDL_API_KEY=your_quandl_key_here
OPENAI_API_KEY=your_openai_key_here

# Notification APIs (Optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_here
SLACK_WEBHOOK_URL=your_slack_webhook_here
"""
        
        st.code(sample_config, language='bash')
        
        st.info("""
        💡 **Pro Tip:** Start with these 3 essential APIs for maximum functionality:
        1. **ALPHA_VANTAGE_API_KEY** - Free real-time market data
        2. **FINNHUB_API_KEY** - Free comprehensive stock data  
        3. **NEWS_API_KEY** - Free news sentiment analysis
        
        These will unlock 80% of the advanced features!
        """)
    
    def validate_api_key_format(self, key_name: str, key_value: str) -> bool:
        """Validate API key format"""
        if not key_value or len(key_value.strip()) < 10:
            return False
        
        # Basic format validation
        if key_name == 'ALPHA_VANTAGE_API_KEY':
            return len(key_value) >= 16 and key_value.isalnum()
        elif key_name == 'FINNHUB_API_KEY':
            return len(key_value) >= 20
        elif key_name == 'TELEGRAM_BOT_TOKEN':
            return ':' in key_value and len(key_value) > 40
        elif key_name == 'TELEGRAM_CHAT_ID':
            return key_value.isdigit() or key_value.startswith('-')
        
        return True
