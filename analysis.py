"""Calendar-based entry-window analysis. No deposits or withdrawals."""
import numpy as np
import pandas as pd


def validate(frame):
    if not {'date', 'adjusted_close'} <= set(frame.columns):
        raise ValueError('CSV needs date and adjusted_close columns.')
    dates = pd.to_datetime(frame['date'], errors='coerce', utc=True).dt.tz_convert(None).dt.normalize()
    values = pd.to_numeric(frame['adjusted_close'], errors='coerce')
    if dates.isna().any() or values.isna().any() or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError('Dates must be valid; prices must be finite and positive.')
    if dates.duplicated().any():
        raise ValueError('Duplicate dates are not allowed.')
    if len(frame) < 2:
        raise ValueError('At least two observations are required.')
    return pd.Series(values.to_numpy(), index=pd.DatetimeIndex(dates), name='price').sort_index()


def cagr(series):
    years = (series.index[-1] - series.index[0]).days / 365.2425
    if years <= 0:
        raise ValueError('Positive elapsed time is required.')
    return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)


def path_metrics(series):
    values = series.to_numpy()
    peaks = np.maximum.accumulate(values)
    dd = values / peaks - 1
    trough = int(np.argmin(dd))
    depth = float(dd[trough])
    peak = int(np.flatnonzero(values[:trough + 1] == peaks[trough])[-1])
    recovery = np.flatnonzero(values[trough + 1:] >= peaks[trough])
    if depth == 0:
        days, status = 0, 'No drawdown'
    elif len(recovery):
        end = trough + 1 + int(recovery[0])
        days, status = (series.index[end] - series.index[peak]).days, 'Recovered'
    else:
        days, status = np.nan, 'Unrecovered at window end'
    return {'cagr': cagr(series), 'max_drawdown': depth,
            'recovery_days': days, 'recovery_status': status}


def windows(series, years, benchmark=None):
    if years < 1 or int(years) != years:
        raise ValueError('Holding period must be a positive whole number of years.')
    if benchmark is not None:
        aligned = pd.concat([series, benchmark], axis=1, join='inner').dropna()
        series, benchmark = aligned.iloc[:, 0], aligned.iloc[:, 1]
    rows = []
    for start in range(len(series)):
        target = series.index[start] + pd.DateOffset(years=int(years))
        end = int(series.index.searchsorted(target))
        if end >= len(series):
            break
        # Avoid treating a large data gap as an ordinary next trading day.
        if (series.index[end] - target).days > 7:
            continue
        segment = series.iloc[start:end + 1]
        row = {'start': segment.index[0], 'end': segment.index[-1], **path_metrics(segment)}
        if benchmark is not None:
            row['benchmark_cagr'] = cagr(benchmark.iloc[start:end + 1])
            row['excess_cagr'] = row['cagr'] - row['benchmark_cagr']
        rows.append(row)
    return pd.DataFrame(rows)


def demo():
    """Invented data for interface exploration, never historical market evidence."""
    dates = pd.bdate_range('2005-01-03', '2025-12-31')
    rng = np.random.default_rng(42)
    market = rng.normal(.00028, .009, len(dates))
    market[(dates >= '2008-09-01') & (dates <= '2009-03-01')] -= .0025
    asset = .8 * market + rng.normal(.00010, .006, len(dates))
    return (pd.Series(100 * np.exp(np.cumsum(asset)), index=dates),
            pd.Series(100 * np.exp(np.cumsum(market)), index=dates))
