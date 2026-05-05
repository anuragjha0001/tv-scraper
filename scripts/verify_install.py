#!/usr/bin/env python3
"""Verify TV Scraper installation"""
import sys

def main():
    print("🔍 Verifying TV Scraper installation...")
    try:
        import tv_scraper
        print(f"✅ tv_scraper v{tv_scraper.__version__}")
        print(f"   Author: {tv_scraper.__author__}")
        return 0
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
