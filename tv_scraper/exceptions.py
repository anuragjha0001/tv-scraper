"""
Custom Exceptions
=================
Exception hierarchy for TV Scraper errors.
"""

class TvScraperError(Exception):
    """Base exception for all TV Scraper errors"""
    pass

class ConnectionError(TvScraperError):
    """Raised when WebSocket connection fails"""
    pass

class NoDataError(TvScraperError):
    """Raised when no data is returned for a symbol"""
    pass

class InvalidSymbolError(TvScraperError):
    """Raised when symbol format is invalid"""
    pass

class FormatError(TvScraperError):
    """Raised when output format is invalid or unsupported"""
    pass

class ParseError(TvScraperError):
    """Raised when response parsing fails"""
    pass


__all__ = [
    'TvScraperError',
    'ConnectionError',
    'NoDataError',
    'InvalidSymbolError',
    'FormatError',
    'ParseError',
]
