"""
TV Scraper - TradingView Historical Data Fetcher
=================================================
A lightweight library to fetch historical price data from TradingView
with support for multiple output formats.

Author: Anurag Jha
Email: anuragjha507@gmail.com
GitHub: https://github.com/anuragjha0001/tv-scraper

Quick Start:
    from tv_scraper import TvDatafeed
    tv = TvDatafeed()
    df = tv.get("BTCUSDT")
"""

__version__ = "0.1.0"
__author__ = "Anurag Jha"
__email__ = "anuragjha507@gmail.com"
__github__ = "https://github.com/anuragjha0001/tv-scraper"

from .core import TvDatafeed

__all__ = ["TvDatafeed"]
