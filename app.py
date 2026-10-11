import json
from datetime import date
import pandas as pd
import streamlit as st
import plotly.express as px
from analysis import validate, cagr, windows, demo, path_metrics
from market_data import fetch_prices
from design import apply_design, polished, RED, WHITE

st.set_page_config(page_title='EntryLens', page_icon='📈', layout='wide')
apply_design()

@st.cache_data(ttl=3600, show_spinner=False)
def cached_prices(symbol, start, end):
    return fetch_prices(symbol, start, end)

provenance = None
with st.sidebar:
    st.markdown('### Experiment settings')
    st.caption('Choose your data. Explore your timing.')
    mode = st.radio('Data source', ['Synthetic demonstration', 'Load tickers', 'Upload historical CSV'])
    if mode == 'Load tickers':
        with st.form('ticker_loader'):
            symbol = st.text_input('Asset ticker', 'SPY')
            benchmark_symbol = st.text_input('Benchmark ticker (optional)', 'QQQ')
            download_start = st.date_input('Download start', date(2000,1,1), max_value=date.today())
            download_end = st.date_input('Download end', date.today(), max_value=date.today())
            submitted = st.form_submit_button('Load market data', type='primary')
        st.caption('Daily adjusted prices · Cached for one hour · Historical data, not a live quote feed.')
    years = st.select_slider('Holding period (years)', options=[1, 2, 3, 5, 7, 10], value=5)
    uploaded = st.file_uploader('Asset CSV', type='csv') if mode == 'Upload historical CSV' else None
    reference = st.file_uploader('Optional benchmark CSV', type='csv') if mode == 'Upload historical CSV' else None
    capital = st.number_input('Starting investment ($)', min_value=100.0, max_value=100000000.0, value=10000.0, step=1000.0)
    target = st.number_input('CAGR threshold (%)', min_value=-100.0, max_value=200.0, value=8.0, step=1.0)
    st.caption('CSV columns: date, adjusted_close. One row per observation. Use consistently adjusted prices.')
if mode == 'Synthetic demonstration':
    asset, benchmark = demo()
    st.markdown('<div class="el-notice"><strong>SYNTHETIC DEMO</strong>Invented prices for exploring the interface. These are not actual assets or historical investment results.</div>', unsafe_allow_html=True)
elif mode == 'Load tickers':
    if submitted:
        try:
            with st.spinner('Loading market data…'):
                loaded_asset, asset_meta = cached_prices(symbol.strip().upper(), download_start, download_end)
                loaded_benchmark, benchmark_meta = (cached_prices(benchmark_symbol.strip().upper(), download_start, download_end)
                    if benchmark_symbol.strip() else (None, None))
            st.session_state['market_bundle'] = (loaded_asset, loaded_benchmark, asset_meta, benchmark_meta)
        except (ValueError, ImportError) as exc:
            st.error(str(exc))
            st.info('No new dataset was loaded. Correct the inputs and submit again.'); st.stop()
    if 'market_bundle' not in st.session_state:
        st.info('Enter your tickers in the sidebar and click Load market data.'); st.stop()
    asset, benchmark, asset_meta, benchmark_meta = st.session_state['market_bundle']
    provenance = {'asset':asset_meta, 'benchmark':benchmark_meta}
    st.caption(f"Loaded: {asset_meta['ticker']}" + (f" · Benchmark: {benchmark_meta['ticker']}" if benchmark_meta else '') + ' · Yahoo Finance via yfinance')
    with st.expander('Data source and retrieval details'):
        st.json(provenance)
        st.download_button('Export source metadata', json.dumps(provenance, indent=2), 'entrylens-data-source.json', 'application/json')
        st.caption('The displayed dataset changes only after a successful Load market data submission. Cached retrieval timestamps describe the original fetch.')
else:
    if uploaded is None:
        st.info('Upload a CSV to begin. Switch to synthetic demonstration to explore the interface.')
        st.stop()
    try:
        asset = validate(pd.read_csv(uploaded))
        benchmark = validate(pd.read_csv(reference)) if reference else None
    except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        st.error(str(exc)); st.stop()
if benchmark is not None:
    common = pd.concat([asset, benchmark], axis=1, join='inner').dropna()
    if len(common) < 2:
        st.error('Asset and benchmark need at least two shared dates.'); st.stop()
    asset, benchmark = common.iloc[:, 0], common.iloc[:, 1]
    # Matching uses shared dates; documented in Method and limitations.
with st.sidebar:
    selected_range = st.date_input('Analysis date range', value=(asset.index[0].date(), asset.index[-1].date()), min_value=asset.index[0].date(), max_value=asset.index[-1].date())
if len(selected_range) != 2:
    st.info('Select both a start date and an end date.'); st.stop()
asset = asset.loc[str(selected_range[0]):str(selected_range[1])]
if benchmark is not None:
    benchmark = benchmark.reindex(asset.index)
if len(asset) < 2:
    st.info('Choose a date range with at least two observations.'); st.stop()
if asset.index.to_series().diff().dt.days.max() > 7:
    st.warning('The data contains gaps longer than seven days. Sparse prices can understate drawdowns and delay measured recovery.')
results = windows(asset, years, benchmark)
if results.empty:
    st.info('Not enough history for this holding period. Select a shorter period or upload more data.'); st.stop()
cols = st.columns(4)
cols[0].metric('Full-history CAGR', f'{cagr(asset):.1%}')
cols[1].metric(f'Median {years}-year CAGR', f'{results.cagr.median():.1%}')
cols[2].metric('Windows ending in a loss', f'{(results.cagr < 0).mean():.1%}')
cols[3].metric('Entry windows evaluated', f'{len(results):,}')
st.caption(f'{asset.index[0]:%Y-%m-%d} to {asset.index[-1]:%Y-%m-%d}. Full-history CAGR and rolling CAGR describe different horizons.')
a,b,c,d,e = st.tabs(['Entry dates', 'Risk & recovery', 'Holding periods', 'Your investment', 'Research summary'])
with a:
    st.markdown('### Timing changes the story')
    st.caption('Rolling CAGR by entry date · Red: asset · White: benchmark')
    columns = ['cagr'] + (['benchmark_cagr'] if benchmark is not None else [])
    chart = results.set_index('start')[columns].mul(100).rename(columns={'cagr':asset_meta['ticker'] if provenance else 'Asset', 'benchmark_cagr':benchmark_meta['ticker'] if provenance and benchmark_meta else 'Benchmark'})
    st.plotly_chart(polished(px.line(chart, color_discrete_sequence=[RED, WHITE], labels={'value':'CAGR (%)', 'start':'Entry date', 'variable':'Series'})), width='stretch')
    st.write(f'Historical range: **{results.cagr.min():.1%} to {results.cagr.max():.1%}**.')
    if benchmark is not None:
        st.write(f'Asset beat benchmark in **{(results.excess_cagr > 0).mean():.1%}** of matched windows.')
    st.plotly_chart(polished(px.histogram(results.assign(cagr_percent=results.cagr * 100), x='cagr_percent', nbins=40, color_discrete_sequence=[RED], labels={'cagr_percent':'Window CAGR (%)'})), width='stretch')
with b:
    st.markdown('### What did that growth cost you?')
    st.caption('Compare compound growth with the deepest loss experienced along the way.')
    view = results.assign(cagr_percent=results.cagr * 100, loss_percent=-results.max_drawdown * 100)
    st.plotly_chart(polished(px.scatter(view, x='loss_percent', y='cagr_percent', color='recovery_status', color_discrete_map={'Recovered':WHITE, 'Unrecovered at window end':RED, 'No drawdown':'#8c909f'}, opacity=.65, hover_data=['start','end','recovery_days'], labels={'loss_percent':'Maximum drawdown magnitude (%)','cagr_percent':'CAGR (%)'})), width='stretch')
    st.caption('Recovery measures time from the peak preceding the deepest drawdown until that peak is regained, within each window. Unrecovered means the window ended before recovery; it does not mean recovery never occurred.')
with c:
    st.markdown('### The bigger picture')
    st.caption('Scan entry years and holding periods in one view.')
    parts=[]
    for horizon in [1,2,3,5,7,10]:
        table=windows(asset,horizon)
        if not table.empty:
            table['entry_year']=table.start.dt.year
            grouped=table.groupby('entry_year').cagr.median().mul(100)
            parts.append(grouped.rename(horizon))
    matrix=pd.concat(parts,axis=1).T
    st.plotly_chart(polished(px.imshow(matrix, aspect='auto', color_continuous_scale=['#ff354d','#1c1d25','#ffffff'], color_continuous_midpoint=0, labels={'x':'Entry year','y':'Holding years','color':'Median CAGR (%)'})), width='stretch')
    st.caption('Each cell is the median across eligible entry dates in that year. Blank cells lack completed windows; recent years can contain partial sets of eligible dates.')
with d:
    st.markdown('### Follow one entry date')
    st.caption('See the journey behind an individual outcome. Dollar values use your chosen starting investment.')
    choice = st.radio('Choose an entry', ['Custom date', 'Best CAGR', 'Worst CAGR', 'Deepest drawdown'], horizontal=True)
    if choice == 'Custom date':
        requested = st.date_input('Entry date', value=results.start.iloc[0].date(), min_value=results.start.iloc[0].date(), max_value=results.start.iloc[-1].date())
        eligible = results[results.start >= pd.Timestamp(requested)]
        row = eligible.iloc[0] if not eligible.empty else results.iloc[-1]
    else:
        idx = results.cagr.idxmax() if choice == 'Best CAGR' else results.cagr.idxmin() if choice == 'Worst CAGR' else results.max_drawdown.idxmin()
        row = results.loc[idx]
    segment = asset.loc[row.start:row.end]
    wealth = pd.DataFrame({'Asset': capital * segment / segment.iloc[0]})
    if benchmark is not None:
        ref = benchmark.loc[row.start:row.end]
        wealth['Benchmark'] = capital * ref / ref.iloc[0]
    st.caption(f'Observed entry: {row.start:%Y-%m-%d} · Exit: {row.end:%Y-%m-%d}')
    k = st.columns(3)
    k[0].metric('Ending asset value', f'${wealth.Asset.iloc[-1]:,.0f}')
    k[1].metric('Window CAGR', f'{row.cagr:.1%}')
    k[2].metric('Maximum drawdown', f'{row.max_drawdown:.1%}')
    st.plotly_chart(polished(px.line(wealth, color_discrete_sequence=[RED,WHITE], labels={'value':'Investment value ($)','variable':'Series','index':'Date'})), width='stretch')
    drawdowns = (wealth / wealth.cummax() - 1) * 100
    st.plotly_chart(polished(px.line(drawdowns, color_discrete_sequence=[RED,WHITE], labels={'value':'Drawdown (%)','variable':'Series','index':'Date'})), width='stretch')
    st.caption(f"Recovery status: {row.recovery_status}. " + (f'Peak-to-recovery: {int(row.recovery_days)} calendar days.' if pd.notna(row.recovery_days) else 'No recovery was observed before this window ended.'))
    st.download_button('Export selected investment path', wealth.to_csv(index_label='date'), 'entrylens-investment-path.csv', 'text/csv')
with e:
    st.markdown('### From chart to finding')
    st.caption('A factual summary of the current dataset and settings. These observations are not predictions.')
    frequency = (results.cagr >= target / 100).mean()
    recovered = results.recovery_status.eq('Recovered').sum()
    unrecovered = results.recovery_status.str.startswith('Unrecovered').sum()
    quantiles = results.cagr.quantile([.1,.25,.5,.75,.9])
    st.dataframe(pd.DataFrame({'Percentile':['10th','25th','Median','75th','90th'], 'CAGR (%)':quantiles.to_numpy()*100}).style.format({'CAGR (%)':'{:.2f}'}), hide_index=True, width='stretch')
    st.write(f'**{frequency:.1%}** of eligible windows met or exceeded your **{target:.1f}% CAGR threshold**.')
    st.write(f'**{unrecovered:,}** windows ended before recovery from their deepest drawdown; **{recovered:,}** recovered within the window.')
    summary = f'''EntryLens research snapshot
Data: {'SYNTHETIC DEMONSTRATION — not market evidence' if mode == 'Synthetic demonstration' else json.dumps(provenance) if provenance else 'User-uploaded CSV — source must be documented separately'}
Analysis period: {asset.index[0]:%Y-%m-%d} to {asset.index[-1]:%Y-%m-%d}
Holding period: {years} calendar years
Eligible overlapping windows: {len(results)}
Median CAGR: {results.cagr.median():.2%}
CAGR range: {results.cagr.min():.2%} to {results.cagr.max():.2%}
Windows ending at a loss: {(results.cagr < 0).mean():.2%}
Fraction meeting {target:.1f}% threshold: {frequency:.2%}
Unrecovered deepest drawdowns at window end: {unrecovered}
No flows, fees, taxes, or inflation adjustment. Overlapping windows are dependent. Historical frequencies are not forecasts.
'''
    st.download_button('Download research snapshot', summary, 'entrylens-research.txt', 'text/plain')
    with st.expander('Inspect every entry window'):
        st.dataframe(results, hide_index=True, width='stretch')

with st.expander('Method and limitations'):
    st.write('CAGR = (ending price / starting price)^(365.2425 / elapsed calendar days) − 1. Each window ends on the first observation on or after its calendar anniversary, at most seven days later. No interpolation or forward filling.')
    st.write('Benchmark comparisons use shared observation dates only.')
    st.write('No deposits, withdrawals, taxes, fees, inflation adjustment, or execution simulation. Adjusted-price results depend on the supplied data convention. Drawdowns use observed prices only. Overlapping windows are dependent observations, and historical fractions are not forecasts or independent probabilities.')
st.download_button('Download window results', results.to_csv(index=False), 'entrylens-results.csv', 'text/csv')

st.markdown('<div class="el-footer">EntryLens / Explore the past. Question the headline. &nbsp; • &nbsp; Historical outcomes are not forecasts.</div>', unsafe_allow_html=True)
