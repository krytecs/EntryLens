# EntryLens

**How much does an investment's apparent performance depend on when you invested?**

EntryLens is a Python/Streamlit research dashboard comparing headline CAGR with the distribution of historical entry-date outcomes. It includes matched benchmark comparisons, drawdowns, recovery status, a holding-period heatmap, and CSV exports. Also includes date-range controls, a starting-investment input, custom/best/worst entry paths, dollar-value and drawdown charts, CAGR threshold frequencies, percentile summaries, and downloadable research snapshots.

## Installation

Open a terminal inside this folder and run:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the localhost address printed in the terminal. Stop with Control-C.

## Ticker loading

Choose **Load tickers**, enter an asset (default SPY) and an optional benchmark (default QQQ), select download dates, and click **Load market data**. Prices come from Yahoo Finance through yfinance, with `auto_adjust=True`. The end date is inclusive in the interface. Actual availability depends on the ticker and provider.

Successful downloads are cached for one hour. Source metadata records requested and observed dates, adjustment mode, and retrieval timestamp. Form changes take effect only after successful submission. Provider outages, rate limits, and unavailable symbols produce an error rather than synthetic replacement data. CSV loading remains available.

Review provider terms before sharing or redistributing market data. yfinance is an unofficial research interface; do not assume its data is licensed for a public hosted deployment.

## Data

The default demo is explicitly **synthetic**, generated with seed 42. It is not a historical asset and cannot substantiate investment conclusions. Upload your own CSV with `date,adjusted_close`; for example:

```csv
date,adjusted_close
2020-01-02,100.0
2020-01-03,101.0
```

This two-row example illustrates the format only; rolling results require years of data. Use daily adjusted prices from a source you are authorized to access. Record provider, ticker, download date, date range, and adjustment convention. Do not redistribute restricted data. An optional benchmark CSV uses the same format. Asset and benchmark are restricted to shared dates, without filling missing prices.

## Method

- Evaluate every eligible observed entry date.
- Exit on the first observation on or after the calendar anniversary, at most seven calendar days later.
- Annualize using actual elapsed days / 365.2425.
- Maximum drawdown is the minimum of price / running peak - 1 within each window.
- Recovery time is measured from the peak before the deepest drawdown to its first subsequent recovery. Unrecovered observations have no fabricated recovery time.
- Heatmap cells show median CAGR by entry year and horizon; recent years can have only partially eligible entry dates.
- No flows, fees, taxes, inflation, or execution assumptions. Supplied adjustment conventions determine whether dividends are represented.
- Overlapping windows are dependent. Historical frequencies are not forecasts. Observed-data drawdowns can miss intraday losses or losses inside gaps.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Deployment

Deploy with Streamlit Community Cloud using `app.py` as the entrypoint and `requirements.txt` for dependencies. Use Python 3.12, matching the tested environment. Keep virtual environments and secrets out of the repository.

## Roadmap

- Inflation-adjusted outcomes.
- Explicit transaction-cost modeling.
- Monthly-contribution analysis using XIRR.

These features are not implemented in the current version.
