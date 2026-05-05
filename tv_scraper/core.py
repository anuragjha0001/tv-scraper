"""
Main TvDatafeed Class
=====================
Core class for fetching TradingView historical data.

To be implemented:
    - get()           : Universal fetch with multiple output formats
    - get_multi()     : Batch fetch multiple symbols
    - fetch_raw()     : Get raw WebSocket response
    - parse()         : Parse raw response to tuples
"""

class TvDatafeed:
    """
    Main class for fetching TradingView data.
    
    Planned API:
        tv = TvDatafeed()
        df = tv.get("BTCUSDT")
        arr = tv.get("BTCUSDT", output_format="numpy")
        data = tv.get("BTCUSDT", output_format="dict")
    """
    pass
