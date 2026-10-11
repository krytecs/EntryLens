"""Download daily adjusted prices; keep provider failures explicit."""
import re
from datetime import timedelta, datetime, timezone
import pandas as pd
from analysis import validate


def normalize_ticker(symbol):
    symbol = symbol.strip().upper()
    if not re.fullmatch(r'[A-Z0-9^][A-Z0-9.^=\-]{0,19}', symbol):
        raise ValueError('Enter one valid ticker, such as SPY, QQQ, AAPL, or BRK-B.')
    return symbol


def fetch_prices(symbol, start, end, factory=None):
    symbol = normalize_ticker(symbol)
    if start >= end:
        raise ValueError('The download start date must precede the end date.')
    if factory is None:
        import yfinance as yf
        factory = yf.Ticker
    try:
        frame = factory(symbol).history(start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
            interval='1d', auto_adjust=True, actions=False, timeout=20, raise_errors=True)
    except Exception as exc:
        raise ValueError(f'Could not load {symbol}. Check the ticker and connection; the provider may be unavailable or rate-limiting requests. Try again later or upload a CSV.') from exc
    if frame is None or frame.empty or 'Close' not in frame:
        raise ValueError(f'No daily prices returned for {symbol} in this date range.')
    dates = pd.DatetimeIndex(frame.index)
    if dates.tz is not None:
        dates = dates.tz_localize(None)
    prices = validate(pd.DataFrame({'date': dates, 'adjusted_close': frame.Close.to_numpy()}))
    prices = prices.loc[start.isoformat():end.isoformat()]
    if len(prices) < 2:
        raise ValueError(f'{symbol} has fewer than two observations in this range.')
    meta = {'ticker': symbol, 'source':'Yahoo Finance via yfinance', 'adjustment':'auto_adjust=True: provider-adjusted close',
            'retrieved_utc':datetime.now(timezone.utc).isoformat(), 'requested_start':str(start), 'requested_end':str(end),
            'observed_start':str(prices.index[0].date()), 'observed_end':str(prices.index[-1].date()), 'observations':len(prices)}
    return prices, meta
