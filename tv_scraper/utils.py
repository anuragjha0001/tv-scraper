"""Utility Functions"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union

UTC = timezone.utc

VALID_INTERVALS = [
    '1m', '3m', '5m', '15m', '30m', '45m',
    '1H', '2H', '3H', '4H',
    '1D', '1W', '1M'
]

INTERVAL_SECONDS = {
    '1m': 60, '3m': 180, '5m': 300, '15m': 900,
    '30m': 1800, '45m': 2700,
    '1H': 3600, '2H': 7200, '3H': 10800, '4H': 14400,
    '1D': 86400, '1W': 604800, '1M': 2592000,
}

INTERVAL_MINUTES = {
    '1m': 1, '3m': 3, '5m': 5, '15m': 15,
    '30m': 30, '45m': 45,
    '1H': 60, '2H': 120, '3H': 180, '4H': 240,
    '1D': 1440, '1W': 10080, '1M': 43200,
}

INTERVAL_LABELS = {k: k for k in VALID_INTERVALS}


def parse_date(date_input=None):
    if date_input is None:
        return None
    if isinstance(date_input, datetime):
        return date_input.replace(tzinfo=UTC) if date_input.tzinfo is None else date_input.astimezone(UTC)
    if isinstance(date_input, (int, float)):
        if date_input > 1e12:
            date_input = date_input / 1000
        return datetime.fromtimestamp(date_input, UTC)
    if isinstance(date_input, str):
        date_input = date_input.strip()
        try:
            dt = datetime.fromisoformat(date_input)
            return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)
        except:
            pass
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(date_input, fmt).replace(tzinfo=UTC)
            except:
                continue
    raise ValueError(f"Cannot parse date: {date_input}")


def validate_interval(interval):
    interval = interval.strip()
    mapping = {'1min': '1m', '5min': '5m', '15min': '15m', '30min': '30m',
               '1h': '1H', '4h': '4H', '1d': '1D', '1w': '1W'}
    interval = mapping.get(interval.lower(), interval)
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval: {interval}")
    return interval


def default_start(interval="1D", days_back=30):
    now = datetime.now(UTC)
    if interval in ['1m', '3m', '5m']:
        return now - timedelta(days=2)
    elif interval in ['15m', '30m', '45m']:
        return now - timedelta(days=7)
    elif interval in ['1H', '2H', '3H', '4H']:
        return now - timedelta(days=14)
    return now - timedelta(days=days_back)
