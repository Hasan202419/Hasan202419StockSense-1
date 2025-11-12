"""
Shared utility functions for StockSense application.
Provides input validation, data processing, and common operations.
"""

import time
import re
from typing import Optional, List, Any, Callable, TypeVar
from functools import wraps
import logging
from logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate a stock symbol format.

    Args:
        symbol (str): Stock symbol to validate

    Returns:
        bool: True if symbol is valid, False otherwise
    """
    if not isinstance(symbol, str):
        logger.warning(f"Symbol must be a string, got {type(symbol)}")
        return False

    symbol = symbol.strip().upper()

    # Must be 1-5 characters, alphanumeric plus hyphen
    if not re.match(r"^[A-Z0-9\-]{1,5}$", symbol):
        logger.warning(f"Invalid symbol format: {symbol}")
        return False

    return True


def validate_price(price: float, name: str = "price") -> bool:
    """
    Validate a price value.

    Args:
        price (float): Price to validate
        name (str): Name of the price field for logging

    Returns:
        bool: True if price is valid, False otherwise
    """
    try:
        price_float = float(price)
        if price_float <= 0:
            logger.warning(f"{name} must be positive, got {price_float}")
            return False
        return True
    except (ValueError, TypeError):
        logger.warning(f"Invalid {name}: {price}")
        return False


def validate_percentage(value: float, name: str = "percentage") -> bool:
    """
    Validate a percentage value (0-100 or 0-1).

    Args:
        value (float): Percentage to validate
        name (str): Name of the percentage field for logging

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        val = float(value)
        if not (0 <= val <= 1) and not (0 <= val <= 100):
            logger.warning(f"{name} must be between 0-1 or 0-100, got {val}")
            return False
        return True
    except (ValueError, TypeError):
        logger.warning(f"Invalid {name}: {value}")
        return False


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitize and normalize a stock symbol.

    Args:
        symbol (str): Raw stock symbol

    Returns:
        str: Sanitized symbol (uppercase, stripped)
    """
    if not isinstance(symbol, str):
        return ""
    return symbol.strip().upper()


def retry_with_backoff(
    max_retries: int = 3,
    backoff_base: int = 2,
    timeout: int = 30,
) -> Callable:
    """
    Decorator for automatic retry with exponential backoff.

    Args:
        max_retries (int): Maximum number of retry attempts
        backoff_base (int): Base for exponential backoff calculation
        timeout (int): Timeout between retries in seconds

    Returns:
        Callable: Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = backoff_base**attempt
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )

            return None

        return wrapper

    return decorator


def safe_dict_get(
    data: dict, key: str, default: Any = None, key_type: type = None
) -> Any:
    """
    Safely get a value from a dictionary with type validation.

    Args:
        data (dict): Dictionary to read from
        key (str): Key to retrieve
        default (Any): Default value if key not found
        key_type (type): Expected type of the value

    Returns:
        Any: Value if found and valid, default otherwise
    """
    try:
        if not isinstance(data, dict):
            logger.warning(f"Expected dict, got {type(data)}")
            return default

        value = data.get(key, default)

        if value is None:
            return default

        if key_type is not None and not isinstance(value, key_type):
            logger.warning(
                f"Value for key '{key}' has type {type(value)}, expected {key_type}"
            )
            return default

        return value
    except Exception as e:
        logger.error(f"Error getting key '{key}' from dict: {e}")
        return default


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    Format a decimal value as a percentage string.

    Args:
        value (float): Value to format (0-1 or 0-100)
        decimal_places (int): Number of decimal places

    Returns:
        str: Formatted percentage string
    """
    try:
        if value > 1:
            value = value / 100
        percentage = value * 100
        return f"{percentage:.{decimal_places}f}%"
    except Exception as e:
        logger.error(f"Error formatting percentage: {e}")
        return "N/A"


def format_currency(value: float, decimal_places: int = 2) -> str:
    """
    Format a value as currency.

    Args:
        value (float): Value to format
        decimal_places (int): Number of decimal places

    Returns:
        str: Formatted currency string
    """
    try:
        return f"${value:,.{decimal_places}f}"
    except Exception as e:
        logger.error(f"Error formatting currency: {e}")
        return "N/A"


def get_s_p_500_symbols() -> List[str]:
    """
    Get list of S&P 500 stock symbols.

    Returns:
        List[str]: List of stock symbols
    """
    # This is the core S&P 500 symbol list that should be used across the app
    return [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "TESLA",
        "META",
        "TSLA",
        "BRK.B",
        "JNJ",
        "V",
        "WMT",
        "JPM",
        "PG",
        "DIS",
        "MA",
        "HD",
        "PYPL",
        "ADBE",
        "MKL",
        "NFLX",
        "INTC",
        "BAC",
        "CSCO",
        "XOM",
        "KO",
        "PFE",
        "ABT",
        "CVX",
        "MRK",
        "PEP",
        "TMO",
        "CRM",
        "IBM",
        "GE",
        "CMCSA",
        "LLY",
        "ABBV",
        "MMM",
        "ACN",
        "UPS",
        "COP",
        "LIN",
        "VZ",
        "CAT",
        "TXN",
        "AMD",
        "WBA",
        "MCD",
        "MU",
        "TMUS",
        "SPY",
        "QQQ",
        "IWM",
        "VTI",
        "AGG",
        "BND",
        "GLD",
        "TLT",
        "EEM",
        "GOVT",
        "HYG",
        "LQD",
        "EMB",
        "VXUS",
        "VTIAX",
        "SCHB",
        "SCHF",
        "SCHE",
        "SCHA",
        "SCHD",
        "SCHG",
        "SCHH",
        "SCHJ",
        "SCHK",
        "SCHL",
        "SCHM",
        "SCHN",
        "SCHO",
        "SCHP",
        "SCHQ",
        "SCHR",
        "SCHS",
        "SCHT",
        "SCHU",
        "SCHV",
        "SCHW",
        "SCHX",
        "SCHY",
        "SCHZ",
        "VOO",
        "VTV",
        "VTI",
        "VUG",
        "VBK",
        "VB",
        "VBR",
        "VSS",
        "VEA",
        "VXUS",
        "VTIAX",
        "VGIT",
        "VGSH",
        "VGSLX",
        "VIG",
        "VYMI",
        "VYAX",
        "VOOV",
    ]


def get_safe_value(
    obj: Any, attr: str, default: Any = None, expected_type: type = None
) -> Any:
    """
    Safely get an attribute from an object with type validation.

    Args:
        obj (Any): Object to read from
        attr (str): Attribute name
        default (Any): Default value if attribute not found
        expected_type (type): Expected type of the value

    Returns:
        Any: Attribute value if found and valid, default otherwise
    """
    try:
        if not hasattr(obj, attr):
            logger.debug(f"Object has no attribute '{attr}'")
            return default

        value = getattr(obj, attr)

        if value is None:
            return default

        if expected_type is not None and not isinstance(value, expected_type):
            logger.warning(
                f"Attribute '{attr}' has type {type(value)}, expected {expected_type}"
            )
            return default

        return value
    except Exception as e:
        logger.error(f"Error getting attribute '{attr}': {e}")
        return default
