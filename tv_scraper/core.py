"""Main TvDatafeed Class"""

import datetime, json, random, re, string, time
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from websocket import create_connection, WebSocketTimeoutException

from .exceptions import (
    TvScraperError, ConnectionError, NoDataError,
    InvalidSymbolError, FormatError, ParseError,
)
from .utils import (
    UTC, VALID_INTERVALS, INTERVAL_SECONDS, INTERVAL_LABELS,
    parse_date, validate_interval, default_start,
)
from .formatters import to_pandas, to_numpy, to_arrays, to_dict, to_json, to_csv


class TvDatafeed:
    """TradingView historical data fetcher."""
    
    WS_URL = "wss://prodata.tradingview.com/socket.io/websocket"
    TV_CHUNK = 5000
    
    _BAR_RE = re.compile(
        r'"v"\s*:\s*\[\s*'
        r'(\d{9,11}(?:\.\d+)?)'
        r'\s*,\s*([\d.eE+\-]+)'
        r'\s*,\s*([\d.eE+\-]+)'
        r'\s*,\s*([\d.eE+\-]+)'
        r'\s*,\s*([\d.eE+\-]+)'
        r'(?:\s*,\s*([\d.eE+\-]+))?'
        r'\s*\]'
    )
    _HB_RE = re.compile(r"~m~\d+~m~~h~\d+")
    _MSG_RE = re.compile(r"~m~\d+~m~")
    
    VALID_FORMATS = ["pandas", "numpy", "arrays", "dict", "json", "csv", "raw"]
    
    def __init__(self, auth_token="unauthorized_user_token", max_retries=3, timeout=10):
        self.token = auth_token
        self.max_retries = max_retries
        self.timeout = timeout
        self.ws = None
        self.ws_headers = json.dumps({"Origin": "https://prodata.tradingview.com"})
    
    def get(self, symbol, exchange="BINANCE", interval="1D", start=None, end=None, output_format="pandas", **format_kwargs):
        if not symbol:
            raise InvalidSymbolError(f"Invalid symbol: {symbol}")
        
        symbol = symbol.strip().upper()
        exchange = exchange.strip().upper()
        interval = validate_interval(interval)
        output_format = output_format.lower().strip()
        
        if output_format not in self.VALID_FORMATS:
            raise FormatError(f"Invalid format: '{output_format}'. Must be: {self.VALID_FORMATS}")
        
        start_dt = parse_date(start) if start else default_start(interval)
        end_dt = parse_date(end) if end else datetime.datetime.now(UTC)
        
        if start_dt >= end_dt:
            raise ValueError(f"start ({start_dt}) must be before end ({end_dt})")
        
        self._connect()
        try:
            tuples = self._fetch_bars(symbol, exchange, interval, start_dt, end_dt)
        finally:
            self._disconnect()
        
        if not tuples:
            raise NoDataError(f"No data for {exchange}:{symbol}")
        
        tuples = self._filter_and_dedupe(tuples, start_dt, end_dt)
        
        if output_format == "raw":
            return tuples
        
        return self._format_output(tuples, output_format, **format_kwargs)
    
    def get_multi(self, requests):
        if not requests:
            raise ValueError("At least one request required")
        
        self._connect()
        results = {}
        try:
            for req in requests:
                symbol = req.get("symbol")
                if not symbol:
                    continue
                try:
                    data = self.get(
                        symbol=symbol,
                        exchange=req.get("exchange", "BINANCE"),
                        interval=req.get("interval", "1D"),
                        start=req.get("start"),
                        end=req.get("end"),
                        output_format=req.get("output_format", "pandas"),
                    )
                    results[f"{req.get('exchange', 'BINANCE')}:{symbol}"] = data
                except Exception as e:
                    results[f"{req.get('exchange', 'BINANCE')}:{symbol}"] = {"error": str(e)}
        finally:
            self._disconnect()
        return results
    
    def fetch_raw(self, symbol, exchange="BINANCE", interval="1D", start=None, end=None):
        return self.get(symbol, exchange, interval, start, end, output_format="raw")
    
    def parse(self, raw_data):
        return self._parse_bars(raw_data)
    
    def _connect(self):
        for attempt in range(self.max_retries):
            try:
                self.ws = create_connection(self.WS_URL, headers=self.ws_headers, timeout=self.timeout)
                self._send("set_auth_token", [self.token])
                return
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Connection failed: {e}")
                time.sleep(1 * (attempt + 1))
    
    def _disconnect(self):
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
    
    def _send(self, func, args):
        body = json.dumps({"m": func, "p": args}, separators=(",", ":"))
        self.ws.send(f"~m~{len(body)}~m~{body}")
    
    @staticmethod
    def _session(prefix):
        return f"{prefix}_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
    
    def _fetch_bars(self, symbol, exchange, interval, start, end):
        full_symbol = f"{exchange}:{symbol}"
        iv_sec = INTERVAL_SECONDS[interval]
        now = datetime.datetime.now(UTC)
        
        gap = max(0, (now - end).total_seconds())
        rng = (end - start).total_seconds()
        smart_chunk = int(gap / iv_sec) + int(rng / iv_sec) + 10
        smart_chunk = min(smart_chunk, self.TV_CHUNK)
        
        all_rows = self._fetch_one(full_symbol, interval, smart_chunk)
        
        if all_rows:
            oldest = min(row[0] for row in all_rows)
            oldest_dt = datetime.datetime.fromtimestamp(oldest, UTC)
            if oldest_dt > start:
                still = int((oldest_dt - start).total_seconds() / iv_sec) + 10
                all_rows.extend(self._fetch_one(full_symbol, interval, min(still, self.TV_CHUNK)))
        
        return all_rows
    
    def _fetch_one(self, full_symbol, interval, n_bars):
        cs = self._session("cs")
        resolve_json = f'={{"symbol":"{full_symbol}","adjustment":"splits","session":"regular"}}'
        
        self._send("chart_create_session", [cs, ""])
        self._send("resolve_symbol", [cs, "symbol_1", resolve_json])
        self._send("create_series", [cs, "s1", "s1", "symbol_1", interval, n_bars])
        self._send("switch_timezone", [cs, "exchange"])
        
        all_rows = []
        triggers = {"timescale_update", "series_completed", "series_error"}
        start_time = time.time()
        
        while time.time() - start_time < 15:
            try:
                result = self.ws.recv()
            except WebSocketTimeoutException:
                continue
            except:
                break
            
            if "~h~" in result and self._HB_RE.match(result):
                self.ws.send(result)
                continue
            
            if cs not in result:
                continue
            
            if "series_error" in result:
                break
            
            new_rows = self._parse_bars(result, cs)
            if new_rows:
                all_rows.extend(new_rows)
            
            if any(t in result for t in triggers) and new_rows:
                break
        
        return all_rows
    
    def _parse_bars(self, raw, session_id=None):
        if session_id:
            segments = self._MSG_RE.split(raw)
            raw = " ".join(s for s in segments if session_id in s)
        
        rows = []
        for m in self._BAR_RE.findall(raw):
            ts = float(m[0])
            if not (946684800 <= ts <= 4102444800):
                continue
            rows.append((int(ts), float(m[1]), float(m[2]), float(m[3]), float(m[4]), float(m[5]) if m[5] else 0.0))
        return rows
    
    @staticmethod
    def _filter_and_dedupe(tuples, start, end):
        start_ts, end_ts = int(start.timestamp()), int(end.timestamp())
        filtered = [t for t in tuples if start_ts <= t[0] <= end_ts]
        seen = {}
        for t in filtered:
            if t[0] not in seen:
                seen[t[0]] = t
        return sorted(seen.values(), key=lambda x: x[0])
    
    def _format_output(self, tuples, output_format, **kwargs):
        formatters = {
            "pandas": to_pandas, "numpy": to_numpy, "arrays": to_arrays,
            "dict": to_dict, "json": to_json, "csv": to_csv,
        }
        return formatters[output_format](tuples, **kwargs)
    
    def __repr__(self):
        return f"TvDatafeed(connected={self.ws is not None}, timeout={self.timeout}s)"
    
    def __enter__(self):
        self._connect()
        return self
    
    def __exit__(self, *args):
        self._disconnect()
