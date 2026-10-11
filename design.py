"""EntryLens presentation layer. Financial calculations live in analysis.py."""
import streamlit as st

RED = '#ff3049'
WHITE = '#f4f4f5'


def apply_design():
    st.markdown('''<style>
    .stApp, .stApp p, .stApp label, .stApp button, .stApp input {font-family:"Avenir Next", Avenir, "Segoe UI", sans-serif;}
    .stApp {background: #08090c; color:#f4f4f5;}
    [data-testid="stHeader"] {background:#08090c;}
    [data-testid="stSidebar"] {background:#101116; border-right:1px solid #262830;}
    .block-container {max-width:1440px; padding-top:4.2rem; padding-bottom:3rem;}
    [data-testid="stSidebar"] label {font-size:13px;}
    [data-baseweb="tab-list"] {overflow-x:auto;}
    [data-testid="stDataFrame"] {border:1px solid #252730; border-radius:4px;}
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {gap:1rem;}
    h3 {font-size:1.15rem !important; padding-top:0 !important; padding-bottom:.25rem !important;}
    h1,h2,h3 {letter-spacing:-.04em;}
    [data-testid="stMetric"] {background:linear-gradient(145deg,#191a21,#111218); border:1px solid #2a2b34; border-top:2px solid #ff3049; padding:12px 16px; border-radius:5px; min-height:96px;}
    [data-testid="stMetricLabel"] {color:#aeb0bd; font-size:.85rem;}
    [data-testid="stMetricValue"] {font-weight:600; letter-spacing:-.05em; font-variant-numeric:tabular-nums;}
    [data-baseweb="tab-list"] {gap:4px; border-bottom:1px solid #292b34; margin:8px 0 8px;}
    [data-baseweb="tab"] {padding:9px 12px; height:auto; border-radius:4px 4px 0 0;}
    [aria-selected="true"][data-baseweb="tab"] {background:#241219; color:#ff6173;}
    [data-testid="stPlotlyChart"] {border:1px solid #262830; border-radius:5px; overflow:hidden;}
    [data-testid="stExpander"] {border-radius:5px; border-color:#292b34;}
    [data-testid="stDownloadButton"] button {background:#ff3049; color:white; border:0; border-radius:4px; font-weight:600; padding:10px 20px;}
    .el-topbar {position:fixed; top:0; left:0; right:0; height:56px; z-index:999990; background:#08090c; border-bottom:1px solid #252730; display:flex; align-items:center; padding:0 22px; pointer-events:none; box-sizing:border-box;}
    .el-topbar .el-brand {margin:0; font-size:22px; gap:9px;}
    .el-topbar .el-mark {padding:4px 8px; font-size:15px;}
    .el-topbar .el-pill {font-size:9px;}
    [data-testid="stSidebar"] > div:first-child {padding-top:56px;}
    @media(max-width:700px) {.el-topbar {padding-left:50px;} .el-topbar .el-pill {display:none;} }
    .el-brand {display:flex; align-items:center; gap:10px; font-size:24px; font-weight:700; letter-spacing:-.055em; margin-bottom:8px;}
    .el-mark {background:#ff3049; color:white; border-radius:4px; padding:7px 10px; font-size:18px;}
    .el-pill {font-size:10px; color:#ff7d8b; background:#291219; border:1px solid #5c2230; padding:5px 9px; border-radius:3px; letter-spacing:.13em; margin-left:8px;}
    .el-eyebrow {color:#ff6173; font-size:11px; letter-spacing:.2em; font-weight:700;}
    .el-hero {padding:0 0 12px;}
    .el-hero h1 {font-size:clamp(25px,2.6vw,36px); line-height:1.15; padding:0 !important; margin:10px 0 12px !important; font-weight:600; max-width:900px;}
    .el-hero h1 span {color:#ff3049;}
    .el-hero p {color:#b0b2bf; font-size:14px; max-width:900px; line-height:1.4; margin-bottom:0;}
    .el-notice {margin:8px 0 12px; padding:12px 16px; border:1px solid #57303a; border-left:3px solid #ff3049; border-radius:5px; background:#211319; color:#eddce0; font-size:13px; line-height:1.5;}
    .el-notice strong {color:#ff8a99; letter-spacing:.06em; font-size:11px; margin-right:10px;}
    .el-footer {margin-top:30px; border-top:1px solid #252730; padding-top:18px; color:#9194a5; font-size:12px;}
    @media(max-width:700px) {.block-container{padding:4.2rem 1rem 2rem;} .el-hero h1{font-size:27px;} }
    </style>''', unsafe_allow_html=True)
    st.markdown('''<div class="el-topbar"><div class="el-brand"><span class="el-mark">↗</span> EntryLens <span class="el-pill">RESEARCH STUDIO</span></div></div>
    <div class="el-hero"><div class="el-eyebrow">TIMING / GROWTH / RISK</div>
    <h1>Your entry point. <span>A different perspective.</span></h1>
    <p>A headline return tells one story. Explore how timing changes compound growth, drawdowns, and the road to recovery.</p></div>''', unsafe_allow_html=True)


def polished(fig):
    fig.update_layout(template='plotly_dark', paper_bgcolor='#111218', plot_bgcolor='#111218',
                      font=dict(family='Avenir Next, Avenir, Segoe UI, sans-serif',color='#d9dbe4',size=12),
                      colorway=[RED,WHITE,'#8c909f'], margin=dict(l=25,r=25,t=45,b=35),
                      height=330, hovermode='closest',
                      legend=dict(orientation='h',yanchor='bottom',y=1.03,x=0,title_text=''),
                      hoverlabel=dict(bgcolor='#252730',font_color=WHITE))
    fig.update_xaxes(gridcolor='#1e2028',zerolinecolor='#444652')
    fig.update_yaxes(gridcolor='#1e2028',zerolinecolor='#444652')
    return fig
