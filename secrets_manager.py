
import os
import streamlit as st
from typing import Dict, Optional

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
