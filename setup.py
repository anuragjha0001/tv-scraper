"""Fallback setup.py for older pip versions"""
from setuptools import setup, find_packages

setup(
    name="tv-scraper-py",
    version="0.1.0",
    author="Anurag Jha",
    author_email="anuragjha507@gmail.com",
    description="TradingView data scraper with multiple output formats",
    url="https://github.com/anuragjha0001/tv_scraper",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["websocket-client>=1.4.0"],
    extras_require={
        "pandas": ["pandas>=1.3.0"],
        "numpy": ["numpy>=1.20.0"],
        "ui": ["ipywidgets>=7.7.0"],
        "all": ["pandas>=1.3.0", "numpy>=1.20.0", "ipywidgets>=7.7.0"],
    },
)
