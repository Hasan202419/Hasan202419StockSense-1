"""
Global constants and configuration for StockSense application.
Centralizes all magic numbers, thresholds, and configuration values.
"""

# =============================================================================
# API & DATA FETCHING CONFIGURATION
# =============================================================================
CACHE_TTL_SHORT = 300  # 5 minutes for volatile data
CACHE_TTL_MEDIUM = 900  # 15 minutes for technical indicators
CACHE_TTL_LONG = 1800  # 30 minutes for historical data
API_TIMEOUT = 30  # seconds
API_MAX_RETRIES = 3
API_RETRY_BACKOFF_BASE = 2  # seconds

# Stock universe limits
S_P_500_LIMIT = 100  # Number of S&P 500 stocks to analyze
DEFAULT_LOOKBACK_PERIOD = 252  # Trading days (1 year)

# =============================================================================
# ISLAMIC COMPLIANCE SCREENING THRESHOLDS
# =============================================================================
# Debt ratios
MAX_DEBT_TO_EQUITY_RATIO = 1.0  # Maximum debt to equity
MAX_LEVERAGE_RATIO = 2.0  # Maximum leverage

# Interest/Riba screening
MAX_INTEREST_INCOME_PERCENTAGE = 5  # Max interest income as % of revenue
MAX_INTEREST_EXPENSE_PERCENTAGE = 5  # Max interest expense as % of revenue

# Haram industry exclusions
HARAM_INDUSTRIES = {
    "alcohol",
    "gambling",
    "tobacco",
    "weapons",
    "conventional banking",
    "insurance",
    "pork",
    "adult entertainment",
}

# =============================================================================
# TECHNICAL ANALYSIS THRESHOLDS
# =============================================================================
# RSI (Relative Strength Index)
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_PERIOD = 14

# MACD (Moving Average Convergence Divergence)
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

# Bollinger Bands
BB_PERIOD = 20
BB_STD_DEV = 2

# Moving Averages
MA_SHORT_PERIOD = 20
MA_MEDIUM_PERIOD = 50
MA_LONG_PERIOD = 200

# Volume thresholds
MIN_VOLUME_THRESHOLD = 1_000_000  # Minimum daily trading volume

# =============================================================================
# AI TRADING SYSTEM THRESHOLDS
# =============================================================================
# Position sizing
DEFAULT_POSITION_SIZE = 0.05  # 5% of portfolio per position
MIN_POSITION_SIZE = 0.01  # 1% minimum
MAX_POSITION_SIZE = 0.15  # 15% maximum
MAX_CONCURRENT_POSITIONS = 10

# Risk management
DEFAULT_STOP_LOSS_PERCENTAGE = 0.08  # 8% stop loss
DEFAULT_PROFIT_TARGET_PERCENTAGE = 0.20  # 20% profit target
MIN_PROFIT_TARGET = 0.05  # 5% minimum profit target
RISK_REWARD_RATIO = 1.0 / 2.5  # Risk 1 to win 2.5

# Trading signal thresholds
CONFIDENCE_THRESHOLD_HIGH = 0.75  # >75% confidence = strong signal
CONFIDENCE_THRESHOLD_MEDIUM = 0.60  # 60-75% = moderate signal
CONFIDENCE_THRESHOLD_LOW = 0.40  # 40-60% = weak signal

# =============================================================================
# SENTIMENT ANALYSIS THRESHOLDS
# =============================================================================
SENTIMENT_POSITIVE_THRESHOLD = 0.60
SENTIMENT_NEGATIVE_THRESHOLD = 0.40
SENTIMENT_NEUTRAL_RANGE = (0.40, 0.60)

# =============================================================================
# AUTONOMOUS ANALYZER SETTINGS
# =============================================================================
MIN_HISTORICAL_DATA_POINTS = 60  # Minimum bars needed for analysis
TREND_CONFIRMATION_BARS = 3  # Bars needed to confirm trend change
VOLUME_SPIKE_MULTIPLIER = 1.5  # Volume must be 1.5x average

# =============================================================================
# TELEGRAM BOT CONFIGURATION
# =============================================================================
BOT_POLLING_INTERVAL = 5  # seconds
BOT_CHECK_INTERVAL = 60  # seconds between signal checks
BOT_MAX_MESSAGE_LENGTH = 4096  # Telegram API limit
BOT_SIGNAL_COOLDOWN = 300  # seconds between signals for same stock

# =============================================================================
# PERPETUAL AI TRADER SETTINGS
# =============================================================================
MONITOR_INTERVAL = 60  # seconds
REBALANCE_INTERVAL = 3600  # 1 hour
MAX_DRAWDOWN_ALLOWED = 0.15  # 15% maximum drawdown
MIN_WIN_RATE = 0.50  # 50% win rate minimum

# =============================================================================
# DATA QUALITY THRESHOLDS
# =============================================================================
MIN_PRICE = 0.10  # Minimum stock price to consider
MAX_PRICE = 10000.00  # Maximum stock price to consider
MIN_MARKET_CAP_MILLIONS = 100  # Minimum market cap in millions
MAX_DATA_GAP_DAYS = 10  # Maximum gap allowed in price data

# =============================================================================
# UI/DISPLAY SETTINGS
# =============================================================================
DEFAULT_CHART_HEIGHT = 500
DEFAULT_CHART_WIDTH = 1200
DECIMAL_PRECISION = 2  # Decimal places for display
PERCENTAGE_PRECISION = 1  # Decimal places for percentages

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "stocksense.log"
LOG_MAX_BYTES = 10_485_760  # 10 MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# =============================================================================
# ERROR HANDLING & WARNINGS
# =============================================================================
WARNINGS_AS_ERRORS = False  # Convert warnings to errors in strict mode
SAFE_MODE_ENABLED = True  # Enable additional safety checks
