"""
LTV Analysis Engine — Professional Banking Dashboard
=====================================================
A redesigned, production-grade Loan-to-Value analysis platform.

Design language
---------------
- Slate / Indigo banking palette
- Inter typography (with tabular numerals for figures)
- 4-tab navigation: Dashboard · Portfolio · Analysis · Reports
- Sidebar acts as the "quick-add" workbench
- Plotly charts for collateral allocation & LTV visualization
- Bulk Excel import / Excel export + PDF report export

Run with
--------
    streamlit run app.py
"""

# ============================================================
# 📦 IMPORTS
# ============================================================
import io
import copy
from html import escape as esc
from datetime import datetime

import streamlit as st
import pandas as pd
from weasyprint import HTML
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


# ============================================================
# ⚙️ PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="LTV Analysis Engine",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 🎨 GLOBAL STYLES
# ============================================================
GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg-page:        #F4F6FB;
        --bg-card:        #FFFFFF;
        --bg-elevated:    #FFFFFF;
        --bg-subtle:      #F8FAFC;
        --bg-dark:        #0F172A;
        --bg-darker:      #020617;
        --bg-indigo:      #4F46E5;
        --bg-indigo-soft: #EEF2FF;
        --border:         #E2E8F0;
        --border-strong:  #CBD5E1;
        --text-primary:   #0F172A;
        --text-secondary: #475569;
        --text-muted:     #94A3B8;
        --text-inverse:   #FFFFFF;
        --success:        #059669;
        --success-bg:     #D1FAE5;
        --warning:        #D97706;
        --warning-bg:     #FEF3C7;
        --danger:         #DC2626;
        --danger-bg:      #FEE2E2;
        --info:           #2563EB;
        --info-bg:        #DBEAFE;
        --purple:         #7C3AED;
        --purple-bg:      #EDE9FE;
        --shadow-sm:      0 1px 2px 0 rgb(0 0 0 / 0.04);
        --shadow:         0 1px 3px 0 rgb(15 23 42 / 0.06), 0 1px 2px -1px rgb(15 23 42 / 0.04);
        --shadow-md:      0 4px 6px -1px rgb(15 23 42 / 0.06), 0 2px 4px -2px rgb(15 23 42 / 0.04);
        --shadow-lg:      0 10px 15px -3px rgb(15 23 42 / 0.08), 0 4px 6px -4px rgb(15 23 42 / 0.04);
        --radius:         10px;
        --radius-lg:      14px;
        --radius-xl:      18px;
    }

    /* ---------- Base ---------- */
    html, body, [class*="css"], .stMarkdown, .stText, p, span, label, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    .block-container { max-width: 100% !important; padding-top: 0 !important; padding-bottom: 2rem !important; }
    .main { background: var(--bg-page) !important; }
    header[data-testid="stHeader"] { background: transparent !important; }
    #MainMenu, footer { visibility: hidden; }
    ::selection { background: var(--bg-indigo); color: white; }

    /* ---------- Sidebar (workbench) ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: 1px solid var(--bg-darker) !important;
        box-shadow: 4px 0 24px rgb(15 23 42 / 0.10);
    }
    [data-testid="stSidebar"] * { color: #E2E8F0; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-weight: 700; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] input {
        background: rgba(255, 255, 255, 0.96) !important;
        color: #0F172A !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        border: none !important;
    }
    [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] svg { color: #475569 !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown { color: #CBD5E1 !important; }
    [data-testid="stSidebar"] .stCheckbox label span { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255, 255, 255, 0.10) !important; margin: 1rem 0 !important; }

    /* Sidebar buttons */
    [data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.6rem 1rem !important;
        box-shadow: 0 2px 8px rgb(79 70 229 / 0.35) !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgb(79 70 229 / 0.55) !important;
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
    }
    [data-testid="stSidebar"] div.stButton > button:active { transform: translateY(0) !important; }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: none !important;
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
    }

    /* ---------- Inputs (main) ---------- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea {
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
        padding: 0.6rem 0.85rem !important;
        font-size: 0.9rem !important;
        background: white !important;
        color: var(--text-primary) !important;
        transition: all 0.15s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: var(--bg-indigo) !important;
        box-shadow: 0 0 0 3px rgb(79 70 229 / 0.12) !important;
        outline: none !important;
    }
    div[data-testid="stNumberInput"] button {
        background: var(--bg-subtle) !important;
        border-color: var(--border) !important;
        color: var(--text-secondary) !important;
    }
    div[data-testid="stFileUploader"] section {
        background: var(--bg-subtle) !important;
        border: 2px dashed var(--border-strong) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem !important;
    }
    div[data-testid="stFileUploader"] section:hover { border-color: var(--bg-indigo) !important; }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        background: white !important;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0 !important;
        border: 1px solid var(--border) !important;
        border-bottom: none !important;
        padding: 0.4rem 0.6rem 0 0.6rem !important;
        box-shadow: var(--shadow-sm) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        padding: 0.85rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: var(--text-secondary) !important;
        border-radius: var(--radius) var(--radius) 0 0 !important;
        transition: all 0.15s ease !important;
        margin: 0 !important;
    }
    .stTabs [data-baseweb="tab"]:hover { color: var(--text-primary) !important; background: var(--bg-subtle) !important; }
    .stTabs [aria-selected="true"] {
        background: var(--bg-indigo) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgb(79 70 229 / 0.25) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: white !important;
        border: 1px solid var(--border) !important;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg) !important;
        padding: 1.75rem !important;
        box-shadow: var(--shadow) !important;
    }

    /* ---------- Buttons (main area) ---------- */
    div.stButton > button {
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        padding: 0.55rem 1.1rem !important;
        border: 1px solid var(--border) !important;
        background: white !important;
        color: var(--text-primary) !important;
        transition: all 0.15s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    div.stButton > button:hover {
        border-color: var(--bg-indigo) !important;
        color: var(--bg-indigo) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 2px 8px rgb(79 70 229 / 0.35) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
        color: white !important;
        box-shadow: 0 6px 18px rgb(79 70 229 / 0.50) !important;
    }

    /* ---------- Dataframe ---------- */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stDataFrame"] iframe { border-radius: var(--radius) !important; }

    /* ---------- Alerts / Info boxes ---------- */
    .stAlert { border-radius: var(--radius) !important; border: none !important; padding: 0.85rem 1rem !important; }
    div[data-testid="stAlert"] { border-left: 4px solid !important; }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader, [data-testid="stExpander"] details summary {
        background: var(--bg-subtle) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }
    [data-testid="stExpander"] details { border: none !important; }
    [data-testid="stExpander"] details > div { border: 1px solid var(--border) !important;
                                                border-top: none !important; border-radius: 0 0 var(--radius) var(--radius) !important; }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: var(--bg-page); }
    ::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ============================================================
# 🎨 REUSABLE COMPONENT CSS
# ============================================================
COMPONENT_CSS = """
<style>
    /* Top header bar */
    .top-header {
        background: white;
        border-bottom: 1px solid var(--border);
        padding: 0.85rem 1.75rem;
        margin: -1rem -1rem 1.25rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow-sm);
    }
    .brand { display: flex; align-items: center; gap: 0.85rem; }
    .brand-icon {
        width: 42px; height: 42px;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.35rem;
        box-shadow: 0 4px 14px rgb(79 70 229 / 0.35);
    }
    .brand-text { line-height: 1.15; }
    .brand-name { font-size: 1.1rem; font-weight: 700; color: #0F172A; letter-spacing: -0.02em; }
    .brand-tag { font-size: 0.7rem; color: #64748B; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; }

    .header-actions { display: flex; align-items: center; gap: 0.85rem; }
    .user-pill {
        display: flex; align-items: center; gap: 0.55rem;
        background: var(--bg-subtle);
        border: 1px solid var(--border);
        border-radius: 99px;
        padding: 0.3rem 0.85rem 0.3rem 0.3rem;
    }
    .user-avatar {
        width: 28px; height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        color: white; font-weight: 700; font-size: 0.72rem;
        display: flex; align-items: center; justify-content: center;
    }
    .user-name { font-size: 0.82rem; font-weight: 600; color: #0F172A; }

    /* Section heading */
    .section-head {
        display: flex; align-items: center; justify-content: space-between;
        margin: 0 0 1.25rem 0;
    }
    .section-title { font-size: 1.45rem; font-weight: 700; color: #0F172A; letter-spacing: -0.025em; margin: 0; }
    .section-sub { font-size: 0.85rem; color: #64748B; margin-top: 0.15rem; }
    .section-title-row { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.2rem; }
    .section-icon {
        width: 36px; height: 36px; border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
        background: var(--bg-indigo-soft); color: var(--bg-indigo);
    }
    .section-icon.success { background: var(--success-bg); color: var(--success); }
    .section-icon.warning { background: var(--warning-bg); color: var(--warning); }
    .section-icon.danger  { background: var(--danger-bg);  color: var(--danger); }
    .section-icon.purple  { background: var(--purple-bg);  color: var(--purple); }
    .section-icon.neutral { background: var(--bg-subtle);  color: var(--text-secondary); }

    /* KPI Cards */
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .kpi-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.4rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
    .kpi-card::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: var(--bg-indigo);
    }
    .kpi-card.success::before { background: var(--success); }
    .kpi-card.warning::before { background: var(--warning); }
    .kpi-card.danger::before  { background: var(--danger); }
    .kpi-card.purple::before  { background: var(--purple); }
    .kpi-card.neutral::before { background: var(--text-muted); }

    .kpi-label { font-size: 0.72rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem; }
    .kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 1.65rem; font-weight: 700; color: #0F172A; line-height: 1.1; letter-spacing: -0.02em; }
    .kpi-meta { display: flex; align-items: center; gap: 0.35rem; font-size: 0.75rem; font-weight: 600; margin-top: 0.5rem; }
    .kpi-meta.pos  { color: var(--success); }
    .kpi-meta.neg  { color: var(--danger); }
    .kpi-meta.neu  { color: var(--text-muted); }

    /* Status banner */
    .status-banner {
        padding: 1.1rem 1.5rem;
        border-radius: var(--radius-lg);
        font-weight: 700;
        font-size: 0.95rem;
        margin: 0.25rem 0 1.25rem 0;
        display: flex; align-items: center; justify-content: center; gap: 0.6rem;
        border: 1px solid;
    }
    .status-pass {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-color: #6EE7B7; color: #065F46;
        box-shadow: 0 4px 16px rgb(5 150 105 / 0.15);
    }
    .status-fail {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-color: #FCA5A5; color: #991B1B;
        box-shadow: 0 4px 16px rgb(220 38 38 / 0.15);
    }
    .status-warn {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-color: #FCD34D; color: #92400E;
        box-shadow: 0 4px 16px rgb(217 119 6 / 0.15);
    }
    .status-dot { width: 10px; height: 10px; border-radius: 50%; }
    .status-pass .status-dot { background: var(--success); box-shadow: 0 0 0 4px rgb(5 150 105 / 0.20); }
    .status-fail .status-dot { background: var(--danger);  box-shadow: 0 0 0 4px rgb(220 38 38 / 0.20); }
    .status-warn .status-dot { background: var(--warning); box-shadow: 0 0 0 4px rgb(217 119 6 / 0.20); }

    /* Badges */
    .badge { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; font-weight: 700; padding: 0.22rem 0.55rem; border-radius: 99px; letter-spacing: 0.01em; }
    .badge-id    { background: var(--bg-indigo-soft); color: #3730A3; font-family: 'JetBrains Mono', monospace; font-weight: 600; }
    .badge-pass  { background: var(--success-bg); color: #065F46; }
    .badge-fail  { background: var(--danger-bg);  color: #991B1B; }
    .badge-warn  { background: var(--warning-bg); color: #92400E; }
    .badge-info  { background: var(--info-bg);    color: #1E40AF; }
    .badge-purple{ background: var(--purple-bg);  color: #5B21B6; }
    .badge-neutral { background: #F1F5F9; color: #475569; }
    .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

    /* Surplus pill */
    .pill { display: inline-block; font-size: 0.72rem; font-weight: 700; padding: 0.22rem 0.55rem; border-radius: 6px; }
    .pill-pos  { background: var(--success-bg); color: #065F46; }
    .pill-neg  { background: var(--danger-bg);  color: #991B1B; }
    .pill-na   { background: #F1F5F9; color: #475569; }

    /* LTV Gauge bar */
    .ltv-bar-wrap {
        margin-top: 0.4rem; height: 6px; background: var(--border); border-radius: 99px; overflow: hidden; position: relative;
    }
    .ltv-bar-fill { height: 100%; border-radius: 99px; transition: width 0.4s ease; }
    .ltv-bar-fill.ok   { background: linear-gradient(90deg, #10B981, #059669); }
    .ltv-bar-fill.warn { background: linear-gradient(90deg, #FBBF24, #D97706); }
    .ltv-bar-fill.fail { background: linear-gradient(90deg, #F87171, #DC2626); }
    .ltv-bar-fill.idle { background: #94A3B8; }

    /* Facility card */
    .fac-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.1rem 1.2rem;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        height: 100%;
    }
    .fac-card:hover { box-shadow: var(--shadow-md); }
    .fac-card-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
    .fac-type { font-size: 0.85rem; font-weight: 700; color: #0F172A; }
    .fac-mode { font-size: 0.7rem; color: #64748B; font-weight: 500; }
    .fac-ac { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 600; color: #4338CA; background: var(--bg-indigo-soft); display: inline-block; padding: 0.1rem 0.4rem; border-radius: 5px; margin-bottom: 0.5rem; }
    .fac-coll { font-size: 0.72rem; color: #64748B; margin-bottom: 0.55rem; min-height: 1rem; }
    .fac-ltv { font-family: 'JetBrains Mono', monospace; font-size: 1.45rem; font-weight: 700; line-height: 1; margin-bottom: 0.2rem; }
    .fac-ltv.ok   { color: var(--success); }
    .fac-ltv.warn { color: var(--warning); }
    .fac-ltv.fail { color: var(--danger); }
    .fac-ltv.idle { color: var(--text-muted); }
    .fac-meta { font-size: 0.7rem; color: #64748B; margin-bottom: 0.55rem; }

    /* Empty state */
    .empty-state { text-align: center; padding: 3rem 1.5rem; background: var(--bg-subtle); border-radius: var(--radius-lg); border: 1px dashed var(--border-strong); margin: 1.5rem 0; }
    .empty-icon { font-size: 2.5rem; margin-bottom: 0.85rem; opacity: 0.7; }
    .empty-title { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem; }
    .empty-sub { font-size: 0.85rem; color: #64748B; max-width: 460px; margin: 0 auto; line-height: 1.55; }

    /* Feature row (used in onboarding) */
    .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
    .feature-card { background: white; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.25rem; box-shadow: var(--shadow-sm); transition: all 0.2s ease; }
    .feature-card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }
    .feature-num { width: 32px; height: 32px; border-radius: 9px; background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; font-weight: 800; font-size: 0.85rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.85rem; }
    .feature-title { font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 0.35rem; }
    .feature-desc  { font-size: 0.8rem; color: #64748B; line-height: 1.55; }

    /* Item list (sidebar) */
    .item-list-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 9px;
        padding: 0.55rem 0.7rem;
        margin-bottom: 0.4rem;
        font-size: 0.8rem;
        color: #E2E8F0;
    }
    .item-list-card .name { font-weight: 600; color: white; }
    .item-list-card .meta { font-size: 0.72rem; color: #94A3B8; font-family: 'JetBrains Mono', monospace; margin-top: 0.1rem; }
    .item-list-card .tag { display: inline-block; font-size: 0.62rem; font-weight: 700; padding: 0.05rem 0.4rem; border-radius: 4px; margin-right: 0.4rem; }
    .item-list-card .tag.pool     { background: rgba(96, 165, 250, 0.18); color: #93C5FD; }
    .item-list-card .tag.assigned { background: rgba(251, 191, 36, 0.18); color: #FCD34D; }
    .item-list-card .tag.tieup    { background: rgba(167, 139, 250, 0.18); color: #C4B5FD; }
    .item-list-card .tag.override { background: rgba(248, 113, 113, 0.18); color: #FCA5A5; }

    /* Notice strip */
    .notice-strip {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 1px solid #FCD34D;
        border-radius: var(--radius);
        padding: 0.75rem 1rem;
        font-size: 0.82rem;
        color: #78350F;
        margin-bottom: 1rem;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .notice-strip.info {
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        border-color: #93C5FD; color: #1E40AF;
    }

    /* Hide default multiselect arrows etc. */
    .stCheckbox { padding-bottom: 0 !important; }

    @media (max-width: 768px) {
        .top-header { padding: 0.75rem 1rem; }
        .brand-tag { display: none; }
        .stTabs [data-baseweb="tab"] { padding: 0.7rem 0.8rem !important; font-size: 0.8rem !important; }
        .stTabs [data-baseweb="tab-panel"] { padding: 1rem !important; }
    }
</style>
"""


# ============================================================
# 🔐 AUTHENTICATION
# ============================================================
def _check_credentials(username: str, password: str) -> bool:
    try:
        pw_section = st.secrets["passwords"]
        for key in pw_section:
            if str(key).strip() == str(username).strip():
                if str(pw_section[key]).strip() == str(password).strip():
                    return True
        return False
    except Exception:
        return False


def _show_login() -> None:
    """Render the polished login screen."""
    st.markdown(COMPONENT_CSS, unsafe_allow_html=True)
    st.markdown("""
    <style>
        .login-wrap {
            min-height: calc(100vh - 4rem);
            display: flex; align-items: center; justify-content: center;
            background:
                radial-gradient(1200px 600px at 10% 0%, rgba(99, 102, 241, 0.20), transparent 60%),
                radial-gradient(900px 500px at 90% 100%, rgba(124, 58, 237, 0.18), transparent 60%),
                linear-gradient(145deg, #F8FAFC 0%, #EEF2FF 100%);
        }
        .login-card {
            width: 100%; max-width: 440px;
            background: white;
            border-radius: 18px;
            box-shadow:
                0 1px 2px rgb(15 23 42 / 0.06),
                0 12px 36px rgb(79 70 229 / 0.15),
                0 32px 80px rgb(79 70 229 / 0.10);
            border: 1px solid #E2E8F0;
            overflow: hidden;
        }
        .login-hero {
            background: linear-gradient(135deg, #4F46E5 0%, #6D28D9 50%, #7C3AED 100%);
            padding: 2rem 2rem 1.5rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .login-hero::before {
            content: ''; position: absolute; top: -50%; left: -30%;
            width: 160%; height: 160%;
            background: radial-gradient(ellipse, rgba(255,255,255,0.12) 0%, transparent 60%);
            pointer-events: none;
        }
        .login-logo {
            width: 60px; height: 60px;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 14px;
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 1.85rem;
            margin-bottom: 0.85rem;
            position: relative;
            z-index: 1;
        }
        .login-name {
            font-size: 1.5rem; font-weight: 800; color: white;
            letter-spacing: -0.03em; margin-bottom: 0.25rem;
            position: relative; z-index: 1;
        }
        .login-tag {
            font-size: 0.72rem; color: rgba(255, 255, 255, 0.75);
            font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em;
            position: relative; z-index: 1;
        }
        .login-body { padding: 2rem; }
        .login-title { font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 0.3rem; }
        .login-sub { font-size: 0.83rem; color: #64748B; line-height: 1.55; margin-bottom: 1.25rem; }
        .login-label { display: block; font-size: 0.78rem; font-weight: 600; color: #334155; margin-bottom: 0.4rem; }
        .login-sec {
            display: flex; justify-content: space-between; align-items: center;
            margin-top: 1.5rem; padding-top: 1.25rem;
            border-top: 1px solid #E2E8F0;
            font-size: 0.7rem; color: #94A3B8;
        }
        .login-sec-item { display: flex; align-items: center; gap: 0.35rem; font-weight: 500; }
        .login-sec-dot { width: 6px; height: 6px; border-radius: 50%; background: #10B981; }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.markdown("""
        <div class="login-card">
            <div class="login-hero">
                <div class="login-logo">🏦</div>
                <div class="login-name">LTV Analysis Engine</div>
                <div class="login-tag">Institutional Lending Platform</div>
            </div>
            <div class="login-body">
                <div class="login-title">Welcome back</div>
                <div class="login-sub">Sign in with your institutional credentials to access the portfolio.</div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="login-label">Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            "u", placeholder="e.g. credit.officer", key="_login_u",
            label_visibility="collapsed", autocomplete="username",
        )
        st.markdown('<span class="login-label" style="margin-top:1rem; display:block;">Password</span>', unsafe_allow_html=True)
        password = st.text_input(
            "p", placeholder="Enter password", type="password",
            key="_login_p", label_visibility="collapsed",
            autocomplete="current-password",
        )

        clicked = st.button("Sign In", key="_login_btn", type="primary", use_container_width=True)

        err = st.session_state.get("_login_error", "")
        if err:
            st.markdown(
                f'<div style="background:#FEF2F2; border:1px solid #FECACA; '
                f'border-radius:8px; padding:0.7rem 0.9rem; margin-top:0.85rem; '
                f'font-size:0.8rem; color:#B91C1C; font-weight:500;">⚠ {err}</div>',
                unsafe_allow_html=True,
            )

        st.markdown("""
                <div class="login-sec">
                    <div class="login-sec-item"><span class="login-sec-dot"></span>TLS Secured</div>
                    <div class="login-sec-item"><span class="login-sec-dot"></span>Audit Ready</div>
                    <div class="login-sec-item"><span class="login-sec-dot"></span>v2.0</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if clicked:
            u, p = str(username).strip(), str(password).strip()
            if not u:
                st.session_state["_login_error"] = "Username is required."
                st.rerun()
            elif not p:
                st.session_state["_login_error"] = "Password is required."
                st.rerun()
            elif _check_credentials(u, p):
                st.session_state["authenticated"] = True
                st.session_state["auth_username"] = u
                st.session_state["_login_error"] = ""
                st.rerun()
            else:
                st.session_state["_login_error"] = (
                    f'Invalid credentials for "{u}". Please verify and try again.'
                )
                st.rerun()


# Auth gate
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    _show_login()
    st.stop()


# ============================================================
# 📋 CONSTANTS
# ============================================================
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",                "Max LTV%": 60.0, "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "HP Loan",                  "Max LTV%": 60.0, "Unsecured": False},
    {"Loan Type": "HP Loan Commercial",       "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "HP Loan (Used)",           "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "HP Loan Commercial-EV",    "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "First Time Home Buyer",    "Max LTV%": 80.0, "Unsecured": False},
    {"Loan Type": "Personal Term Loan (PTL)", "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "Education Loan",           "Max LTV%": 50.0, "Unsecured": False},
    {"Loan Type": "Professional T/L",         "Max LTV%": None, "Unsecured": False},
    {"Loan Type": "Professional OD",          "Max LTV%": None, "Unsecured": False},
    {"Loan Type": "Cash Credit facility",     "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Short Term Facility",      "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Permanent WC Loan",        "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Business Term Loan",       "Max LTV%": 70.0, "Unsecured": False},
    {"Loan Type": "Personal OD",              "Max LTV%": 50.0, "Unsecured": False},
]

LOAN_TYPE_PREFIXES = {
    "Home Loan":                "HL",
    "Mortgage Loan":            "ML",
    "HP Loan":                  "HP",
    "HP Loan Commercial":       "HPC",
    "HP Loan (Used)":           "HPU",
    "HP Loan Commercial-EV":    "HPEV",
    "First Time Home Buyer":    "FTB",
    "Personal Term Loan (PTL)": "PTL",
    "Education Loan":           "EDL",
    "Professional T/L":         "PRTL",
    "Professional OD":          "PROD",
    "Cash Credit facility":     "CC",
    "Short Term Facility":      "STF",
    "Permanent WC Loan":        "PWC",
    "Business Term Loan":       "BTL",
    "Personal OD":              "POD",
}

PROFESSIONAL_OD_CAP       = 500_000.0
PROFESSIONAL_TL_CAP       = 1_500_000.0
PROFESSIONAL_COMBINED_CAP = 1_500_000.0


# ============================================================
# 🗂️ SESSION STATE INIT
# ============================================================
for _k, _v in [
    ("fmv_id_counter",     0),
    ("loan_id_counter",    0),
    ("loan_type_counters", {}),
    ("loans",              []),
    ("fmv_sources",        []),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

if "ltv_policy" not in st.session_state:
    st.session_state.ltv_policy = copy.deepcopy(DEFAULT_LTV_POLICY)


def _migrate_fmv_sources():
    for src in st.session_state.fmv_sources:
        if "id" not in src:
            src["id"] = _next_fmv_id()
        if "Owner" not in src:
            src["Owner"] = ""


def _migrate_loans():
    for loan in st.session_state.loans:
        if "collateral_mode" not in loan:
            loan["collateral_mode"] = "pool"
        elif loan["collateral_mode"] == "both":
            loan["collateral_mode"] = (
                "assigned" if loan.get("assigned_collateral_ids") else "pool"
            )
        if "assigned_collateral_ids" not in loan:
            loan["assigned_collateral_ids"] = []
        if "_loan_id" not in loan:
            loan["_loan_id"] = st.session_state.loan_id_counter
            st.session_state.loan_id_counter += 1
        if "loan_account_id" not in loan:
            loan["loan_account_id"] = _generate_loan_account_id(loan.get("Loan Type", "LN"))
        if "tied_property_ids" not in loan:
            loan["tied_property_ids"] = []
        if "override_ltv" not in loan:
            loan["override_ltv"] = False


# ============================================================
# 🛠️ HELPERS
# ============================================================
def get_policy_dict() -> dict:
    return {
        p["Loan Type"]: (None if p["Unsecured"] else p["Max LTV%"])
        for p in st.session_state.ltv_policy
    }


def _next_fmv_id() -> int:
    fid = st.session_state.fmv_id_counter
    st.session_state.fmv_id_counter += 1
    return fid


def _generate_loan_account_id(loan_type: str) -> str:
    prefix = LOAN_TYPE_PREFIXES.get(loan_type, "LN")
    if prefix not in st.session_state.loan_type_counters:
        st.session_state.loan_type_counters[prefix] = 0
    st.session_state.loan_type_counters[prefix] += 1
    return f"{prefix}{st.session_state.loan_type_counters[prefix]:03d}"


def _get_collateral_names(cids, fmv_sources) -> list:
    id_to_plot = {s["id"]: s["Plot"] for s in fmv_sources}
    return [id_to_plot[cid] for cid in cids if cid in id_to_plot]


def _get_assigned_in_use() -> set:
    return {
        cid
        for loan in st.session_state.loans
        for cid in loan.get("assigned_collateral_ids", [])
        if loan.get("collateral_mode") == "assigned"
    }


def _get_tied_in_use() -> dict:
    result = {}
    for loan in st.session_state.loans:
        for cid in loan.get("tied_property_ids", []):
            result.setdefault(cid, []).append(
                loan.get("loan_account_id", loan["Loan Type"])
            )
    return result


def _portfolio_has_ties() -> bool:
    return any(loan.get("tied_property_ids") for loan in st.session_state.loans)


def _loan_is_ltv_exempt(loan: dict) -> bool:
    """Determine LTV exemption."""
    policy = get_policy_dict()
    if policy.get(loan.get("Loan Type")) is None:
        return True
    if loan.get("override_ltv", False):
        return True
    has_assigned = (
        loan.get("collateral_mode") == "assigned"
        and bool(loan.get("assigned_collateral_ids"))
    )
    if loan.get("tied_property_ids") and not has_assigned:
        return True
    return False


def _all_loans_ltv_exempt() -> bool:
    if not st.session_state.loans:
        return False
    for loan in st.session_state.loans:
        if not _loan_is_ltv_exempt(loan):
            return False
    return True


def _check_professional_caps(l_type: str, l_amt: float, existing_loans: list):
    if l_type not in ("Professional OD", "Professional T/L"):
        return True, ""
    existing_od = sum(l["Principal"] for l in existing_loans if l["Loan Type"] == "Professional OD")
    existing_tl = sum(l["Principal"] for l in existing_loans if l["Loan Type"] == "Professional T/L")
    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)
    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, f"Professional OD total (Rs. {new_od:,.0f}) exceeds cap of Rs. {PROFESSIONAL_OD_CAP:,.0f}."
    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, f"Professional T/L total (Rs. {new_tl:,.0f}) exceeds cap of Rs. {PROFESSIONAL_TL_CAP:,.0f}."
    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, f"Combined Professional OD+T/L (Rs. {(new_od+new_tl):,.0f}) exceeds combined cap of Rs. {PROFESSIONAL_COMBINED_CAP:,.0f}."
    return True, ""


_migrate_fmv_sources()
_migrate_loans()


# ============================================================
# 🧮 LTV CALCULATION ENGINE
# ============================================================
def run_portfolio_ltv(loans, fmv_sources):
    policy      = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if "id" in s]
    fmv_id_set  = {s["id"] for s in fmv_sources}

    def is_exempt(loan):
        return _loan_is_ltv_exempt(loan)

    collateral_usage = {s["id"]: [] for s in fmv_sources}
    for loan in loans:
        if loan.get("collateral_mode") == "assigned" and not is_exempt(loan):
            for cid in loan.get("assigned_collateral_ids", []):
                if cid in collateral_usage:
                    collateral_usage[cid].append(loan["_loan_id"])

    assigned_collateral_ids = {cid for cid, users in collateral_usage.items() if users}
    pool_collateral_ids     = fmv_id_set - assigned_collateral_ids
    collateral_fmv_map      = {s["id"]: s["Amount"] for s in fmv_sources}

    loan_collateral_shares = {loan["_loan_id"]: {} for loan in loans}
    for cid in assigned_collateral_ids:
        user_loan_ids = collateral_usage[cid]
        cid_fmv       = collateral_fmv_map.get(cid, 0.0)
        if len(user_loan_ids) == 1:
            lid = user_loan_ids[0]
            if lid in loan_collateral_shares:
                loan_collateral_shares[lid][cid] = cid_fmv
        else:
            sharing_loans = [l for l in loans if l["_loan_id"] in user_loan_ids]
            total_p       = sum(l["Principal"] for l in sharing_loans)
            for sl in sharing_loans:
                share = (
                    cid_fmv * (sl["Principal"] / total_p)
                    if total_p > 0 else cid_fmv / len(sharing_loans)
                )
                if sl["_loan_id"] in loan_collateral_shares:
                    loan_collateral_shares[sl["_loan_id"]][cid] = share

    loan_assigned_fmv = {
        loan["_loan_id"]: (
            sum(loan_collateral_shares.get(loan["_loan_id"], {}).values())
            if (loan.get("collateral_mode") == "assigned" and not is_exempt(loan)) else 0.0
        )
        for loan in loans
    }

    pool_fmv = sum(s["Amount"] for s in fmv_sources if s["id"] in pool_collateral_ids)

    def waterfall_sort_key(loan):
        max_ltv = policy.get(loan["Loan Type"])
        if max_ltv is None:
            return (2, 0)
        return (0 if max_ltv <= 50 else 1, -loan["Principal"])

    pool_participating = [
        l for l in loans
        if not is_exempt(l)
        and policy.get(l["Loan Type"]) is not None
        and l.get("collateral_mode", "pool") == "pool"
    ]
    pool_sorted    = sorted(pool_participating, key=waterfall_sort_key)
    remaining_pool = pool_fmv
    pool_alloc     = {}
    last_idx       = len(pool_sorted) - 1

    for i, loan in enumerate(pool_sorted):
        lid     = loan["_loan_id"]
        max_ltv = policy.get(loan["Loan Type"])
        if max_ltv is None:
            pool_alloc[lid] = 0.0
            continue
        principal   = loan["Principal"]
        req_total   = principal / (max_ltv / 100.0)
        allocated   = remaining_pool if i == last_idx else min(req_total, remaining_pool)
        pool_alloc[lid] = allocated
        remaining_pool  = max(0.0, remaining_pool - allocated)

    total_fmv = sum(s["Amount"] for s in fmv_sources)
    results   = []

    for loan in loans:
        lid       = loan["_loan_id"]
        lt        = loan["Loan Type"]
        principal = loan["Principal"]
        mode      = loan.get("collateral_mode", "pool")
        exempt    = is_exempt(loan)
        max_ltv   = policy.get(lt)

        exempt_reason = None
        if max_ltv is None:
            exempt_reason = "policy"
        elif loan.get("override_ltv", False):
            exempt_reason = "override"
        elif loan.get("tied_property_ids") and not (
            mode == "assigned" and bool(loan.get("assigned_collateral_ids"))
        ):
            exempt_reason = "tieup"

        if exempt:
            results.append({
                **loan,
                "Max LTV%": None, "Assigned FMV": 0.0, "Pool FMV": 0.0,
                "Total FMV": 0.0, "LTV%": None, "Pass_Status": True,
                "Is_Unsecured": True, "Collateral_Mode": mode,
                "Collateral_Names": [], "Shared_Collateral_Ids": [],
                "No_FMV_Error": False, "Exempt_Reason": exempt_reason,
            })
            continue

        assigned_fmv_val = loan_assigned_fmv.get(lid, 0.0)
        pool_fmv_val     = pool_alloc.get(lid, 0.0)
        total_alloc      = assigned_fmv_val + pool_fmv_val

        if total_alloc <= 0:
            ltv_pct      = None
            passes       = False
            no_fmv_error = True
        else:
            ltv_pct      = principal / total_alloc * 100.0
            passes       = ltv_pct <= max_ltv
            no_fmv_error = False

        assigned_coll_names = _get_collateral_names(
            loan.get("assigned_collateral_ids", []), fmv_sources
        )
        shared_cids = [
            cid for cid in loan.get("assigned_collateral_ids", [])
            if len(collateral_usage.get(cid, [])) > 1
        ]
        results.append({
            **loan,
            "Max LTV%": max_ltv, "Assigned FMV": assigned_fmv_val,
            "Pool FMV": pool_fmv_val, "Total FMV": total_alloc,
            "LTV%": ltv_pct, "Pass_Status": passes, "Is_Unsecured": False,
            "Collateral_Mode": mode, "Collateral_Names": assigned_coll_names,
            "Shared_Collateral_Ids": shared_cids, "No_FMV_Error": no_fmv_error,
            "Exempt_Reason": None,
        })

    secured_results         = [r for r in results if not r["Is_Unsecured"]]
    total_secured_principal = sum(r["Principal"] for r in secured_results)
    total_exposure          = sum(r["Principal"] for r in results)
    total_alloc_fmv         = sum(r["Total FMV"] for r in secured_results)
    wtd_ltv = (
        total_secured_principal / total_alloc_fmv * 100.0
        if total_alloc_fmv > 0 else 0.0
    )
    aggregate_ltv = (
        total_secured_principal / total_fmv * 100.0 if total_fmv > 0 else 0.0
    )
    overall_pass = all(r["Pass_Status"] for r in results)

    return results, {
        "total_fmv": total_fmv,
        "pool_fmv": pool_fmv,
        "remaining_pool": remaining_pool,
        "total_exposure": total_exposure,
        "total_secured_principal": total_secured_principal,
        "total_alloc_fmv": total_alloc_fmv,
        "wtd_ltv": wtd_ltv,
        "aggregate_ltv": aggregate_ltv,
        "overall_pass": overall_pass,
        "collateral_usage": collateral_usage,
        "assigned_collateral_ids": assigned_collateral_ids,
        "pool_collateral_ids": pool_collateral_ids,
    }


# ============================================================
# 📄 PDF REPORT GENERATION
# ============================================================
_PDF_CSS = """
@page {
    size: A4;
    margin: 16mm 14mm 18mm 14mm;
    @bottom-left   { content: "LTV Analysis Engine"; font-size: 7.5pt; color: #666666; }
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 7.5pt; color: #666666; }
    @bottom-right  { content: "__DATE_STR__"; font-size: 7.5pt; color: #666666; }
}
* { box-sizing: border-box; }
body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9pt; color: #1a1a1a; line-height: 1.35;
}
h1 { font-size: 15pt; margin: 0 0 4px 0; text-transform: uppercase; color: #002060; letter-spacing: 0.4px; }
h2 { font-size: 10.5pt; margin: 0 0 14px 0; color: #444444; font-weight: normal; border-bottom: 1px solid #000; padding-bottom: 6px; }
h3 { font-size: 10pt; margin: 18px 0 8px 0; color: #002060; text-transform: uppercase; letter-spacing: 0.3px;
     border-bottom: 1px solid #cccccc; padding-bottom: 3px; }
.header-table { width: 100%; margin-bottom: 16px; }
.header-table td { vertical-align: top; font-size: 9pt; }
.summary-box { border: 1px solid #000; padding: 10px 14px; margin-bottom: 6px; background: #fbfbfb; }
.status-line { font-weight: bold; font-size: 9.5pt; margin-bottom: 10px; }
.status-pass { color: #1a7a1a; } .status-fail { color: #b00000; }
.kv-table { width: 62%; font-size: 9pt; border-collapse: collapse; }
.kv-table td { padding: 2px 0; }
.kv-table td.kv-value { text-align: right; }
.kv-table tr.kv-total td { font-weight: bold; padding-top: 6px; border-top: 1px solid #ccc; }
table.data-table { width: 100%; border-collapse: collapse; margin-bottom: 4px; table-layout: fixed; }
table.data-table thead { display: table-header-group; }
table.data-table tr { page-break-inside: avoid; }
table.data-table th, table.data-table td { padding: 5px 7px; text-align: left; vertical-align: middle; }
table.data-table th { border-top: 1.4px solid #000; border-bottom: 1.4px solid #000; font-weight: bold;
                       font-size: 7.6pt; text-transform: uppercase; letter-spacing: 0.2px; }
table.data-table td { border-bottom: 0.75px solid #e3e3e3; font-size: 8.6pt; }
table.data-table td.center { white-space: nowrap; }
table.data-table tbody tr:nth-child(even) td { background: #f8f8fa; }
table.data-table tr.aggregate-row td { border-top: 1.4px solid #000; border-bottom: 1.4px solid #000;
                                        font-weight: bold; background: #eeeeee !important; }
.right  { text-align: right !important; }
.center { text-align: center !important; }
.muted  { color: #777777; }
.pass   { color: #1a7a1a; font-weight: bold; }
.fail   { color: #b00000; font-weight: bold; }
.exempt { color: #8a6d00; font-weight: bold; }
.tieup  { color: #5b2a86; font-weight: bold; }
.unsec  { color: #555555; font-weight: bold; }
.note { margin-top: 8px; font-size: 7.8pt; color: #666666; font-style: italic; }
"""


def generate_pdf(client_name, results, fmv_sources, summary) -> bytes:
    total_fmv       = summary["total_fmv"]
    total_exposure  = summary["total_exposure"]
    aggregate_ltv   = summary["aggregate_ltv"]
    overall_pass    = summary["overall_pass"]
    total_secured_p = summary["total_secured_principal"]
    has_tied_pdf    = any(r.get("tied_property_ids") for r in results)
    assigned_ids    = summary["assigned_collateral_ids"]
    date_str        = datetime.now().strftime("%B %d, %Y")

    tied_in_use = {}
    for loan in st.session_state.loans:
        for cid in loan.get("tied_property_ids", []):
            tied_in_use.setdefault(cid, []).append(
                loan.get("loan_account_id", loan.get("Loan Type", ""))
            )

    fmv_rows_html = []
    for i, src in enumerate(fmv_sources):
        fid   = src.get("id", i)
        ctype = "ASSIGNED" if fid in assigned_ids else "POOL"
        owner = esc(src.get("Owner", "") or "N/A")
        plot  = esc(src.get("Plot", ""))
        tied_cell = ""
        if has_tied_pdf:
            tied_list = tied_in_use.get(fid, [])
            tied_txt  = esc(", ".join(tied_list)) if tied_list else "N/A"
            tied_cell = f'<td class="muted">{tied_txt}</td>'
        fmv_rows_html.append(f"""
            <tr>
                <td>{plot}</td>
                <td>{ctype}</td>
                <td>{owner}</td>
                {tied_cell}
                <td class="right">{src.get("Amount", 0.0):,.0f}</td>
            </tr>""")

    fmv_colspan = 4 if has_tied_pdf else 3
    fmv_tied_header = "<th>Tied A/C</th>" if has_tied_pdf else ""
    if has_tied_pdf:
        fmv_colgroup = ('<colgroup><col style="width:30%"><col style="width:13%"><col style="width:21%">'
                         '<col style="width:12%"><col style="width:24%"></colgroup>')
    else:
        fmv_colgroup = ('<colgroup><col style="width:36%"><col style="width:15%"><col style="width:25%">'
                         '<col style="width:24%"></colgroup>')
    fmv_table_html = f"""
    <table class="data-table">
        {fmv_colgroup}
        <thead>
            <tr>
                <th>Property Reference</th><th>Collateral Type</th><th>Owner</th>
                {fmv_tied_header}
                <th class="right">Fair Market Value (Rs.)</th>
            </tr>
        </thead>
        <tbody>
            {''.join(fmv_rows_html)}
            <tr class="aggregate-row">
                <td colspan="{fmv_colspan}" class="right">TOTAL</td>
                <td class="right">{total_fmv:,.0f}</td>
            </tr>
        </tbody>
    </table>"""

    def display_sort(r):
        m = r.get("Max LTV%")
        if m is None:
            return (2, 0)
        return (0 if m <= 50 else 1, -(r.get("Principal", 0)))

    EXEMPT_LABEL = {
        "override": ("OVERRIDE", "exempt"),
        "tieup":    ("TIE-UP",   "tieup"),
        "policy":   ("UNSECURED","unsec"),
    }

    fac_rows_html = []
    for row in sorted(results, key=display_sort):
        is_unsec      = row.get("Is_Unsecured", False)
        no_fmv_err    = row.get("No_FMV_Error", False)
        max_ltv       = row.get("Max LTV%")
        ltv_val       = row.get("LTV%")
        exempt_reason = row.get("Exempt_Reason")

        if is_unsec:
            ltv_text, ltv_class = EXEMPT_LABEL.get(exempt_reason, ("EXEMPT", "unsec"))
        elif no_fmv_err:
            ltv_text, ltv_class = "NO FMV", "fail"
        elif ltv_val is None:
            ltv_text, ltv_class = "N/A", "muted"
        else:
            ltv_text  = f"{ltv_val:.2f}%"
            ltv_class = "pass" if row["Pass_Status"] else "fail"

        max_disp   = "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%"
        total_disp = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"

        if is_unsec or max_ltv is None:
            surplus_disp, surplus_class = "N/A", "muted"
        elif no_fmv_err:
            surplus_disp, surplus_class = "No FMV", "fail"
        else:
            req_fmv = row["Principal"] / (max_ltv / 100.0)
            sv      = row.get("Total FMV", 0.0) - req_fmv
            surplus_disp  = f"+{sv:,.0f}" if sv >= 0 else f"({abs(sv):,.0f})"
            surplus_class = "pass" if sv >= 0 else "fail"

        status       = "PASS" if row["Pass_Status"] else "FAIL"
        status_class = "pass" if row["Pass_Status"] else "fail"

        has_both = (
            not is_unsec
            and bool(row.get("tied_property_ids"))
            and row.get("collateral_mode") == "assigned"
            and bool(row.get("assigned_collateral_ids"))
        )
        tied_note_pdf = " [+Tie-up]" if has_both else ""

        fac_rows_html.append(f"""
            <tr>
                <td>{esc(str(row.get('loan_account_id', 'N/A')))}</td>
                <td>{esc(row['Loan Type'])}{esc(tied_note_pdf)}</td>
                <td class="right">{row['Principal']:,.0f}</td>
                <td class="right">{total_disp}</td>
                <td class="right {ltv_class}">{ltv_text}</td>
                <td class="right">{max_disp}</td>
                <td class="right {surplus_class}">{surplus_disp}</td>
                <td class="center {status_class}">{status}</td>
            </tr>""")

    agg_status_class = "pass" if overall_pass else "fail"
    agg_status_text  = "PASS" if overall_pass else "FAIL"

    fac_table_html = f"""
    <table class="data-table">
        <colgroup>
            <col style="width:10%"><col style="width:22%"><col style="width:14%"><col style="width:14%">
            <col style="width:11%"><col style="width:9%"><col style="width:14%"><col style="width:6%">
        </colgroup>
        <thead>
            <tr>
                <th>A/C No.</th><th>Facility Type</th>
                <th class="right">Principal (Rs.)</th>
                <th class="right">Total FMV (Rs.)</th>
                <th class="right">LTV%</th>
                <th class="right">Max LTV%</th>
                <th class="right">Surplus / (Shortfall)</th>
                <th class="center">Status</th>
            </tr>
        </thead>
        <tbody>
            {''.join(fac_rows_html)}
            <tr class="aggregate-row">
                <td colspan="2">AGGREGATE (ALL FACILITIES)</td>
                <td class="right">{total_exposure:,.0f}</td>
                <td class="right">{total_fmv:,.0f}</td>
                <td class="right">{aggregate_ltv:.2f}%</td>
                <td class="right">N/A</td>
                <td class="right">N/A</td>
                <td class="center {agg_status_class}">{agg_status_text}</td>
            </tr>
        </tbody>
    </table>"""

    overridden_loans = [r for r in results if r.get("override_ltv") or r.get("tied_property_ids")]
    register_html    = ""
    if overridden_loans:
        fmv_id_map = {s["id"]: s for s in fmv_sources}
        REG_LABEL  = {
            "override": ("MANUAL OVERRIDE",  "exempt"),
            "tieup":    ("TIE-UP PROPERTIES","tieup"),
            "policy":   ("POLICY EXEMPT",    "unsec"),
        }
        reg_rows_html = []
        for row in overridden_loans:
            exempt_reason = row.get("Exempt_Reason", "")
            is_active_ltv = not row.get("Is_Unsecured", False)
            if is_active_ltv and row.get("tied_property_ids"):
                label, cls = "ADDL. SECURITY", "muted"
            else:
                label, cls = REG_LABEL.get(exempt_reason, ("EXEMPT", "unsec"))

            tied_names, tied_fmv_total = [], 0.0
            for cid in row.get("tied_property_ids", []):
                src = fmv_id_map.get(cid)
                if src:
                    tied_names.append(src.get("Plot", ""))
                    tied_fmv_total += src.get("Amount", 0.0)
            tied_props_str = esc(", ".join(tied_names)) if tied_names else "-"
            tied_fmv_str   = f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "N/A"
            reg_rows_html.append(f"""
                <tr>
                    <td>{esc(str(row.get('loan_account_id', 'N/A')))}</td>
                    <td>{esc(row['Loan Type'])}</td>
                    <td class="right">Rs. {row['Principal']:,.0f}</td>
                    <td class="{cls}">{label}</td>
                    <td>{tied_props_str}</td>
                    <td class="right">{tied_fmv_str}</td>
                </tr>""")

        register_html = f"""
        <h3>LTV Override &amp; Tied Properties Register</h3>
        <table class="data-table">
            <colgroup>
                <col style="width:9%"><col style="width:16%"><col style="width:14%">
                <col style="width:16%"><col style="width:28%"><col style="width:17%">
            </colgroup>
            <thead>
                <tr>
                    <th>A/C No.</th><th>Facility Type</th>
                    <th class="right">Principal (Rs.)</th>
                    <th>Type</th>
                    <th>Tied Properties</th>
                    <th class="right">Tied FMV (Rs.)</th>
                </tr>
            </thead>
            <tbody>{''.join(reg_rows_html)}</tbody>
        </table>
        <p class="note">Overridden and tie-up only facilities are excluded from LTV calculation.
        Facilities with both assigned collateral and tie-up properties calculate LTV normally;
        tie-up serves as additional security only. Manual overrides require credit-authority sign-off.</p>
        """

    status_class = "status-pass" if overall_pass else "status-fail"
    status_text  = ("PORTFOLIO APPROVED &mdash; All Facilities Within LTV Limits" if overall_pass
                     else "PORTFOLIO DECLINED &mdash; One or More Facilities Exceed Maximum LTV")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LTV Analysis Report</title>
<style>{_PDF_CSS.replace('__DATE_STR__', date_str)}</style>
</head>
<body>
    <h1>LTV Analysis Report</h1>
    <h2>Loan-to-Value Assessment</h2>
    <table class="header-table">
        <tr>
            <td><strong>Client Name:</strong> {esc(client_name)}</td>
            <td class="right"><strong>Analysis Date:</strong> {date_str}</td>
        </tr>
    </table>
    <h3>Executive Summary</h3>
    <div class="summary-box">
        <div class="status-line {status_class}">STATUS: {status_text}</div>
        <table class="kv-table">
            <tr><td>Total Secured Exposure:</td><td class="kv-value">Rs. {total_secured_p:,.2f}</td></tr>
            <tr><td>Total Loan Exposure (All Facilities):</td><td class="kv-value">Rs. {total_exposure:,.2f}</td></tr>
            <tr><td>Total Collateral FMV:</td><td class="kv-value">Rs. {total_fmv:,.2f}</td></tr>
            <tr class="kv-total"><td>Aggregate LTV%:</td><td class="kv-value">{aggregate_ltv:.2f}%</td></tr>
        </table>
    </div>
    <h3>Collateral &amp; Fair Market Value Sources</h3>
    {fmv_table_html}
    <h3>Facility LTV Breakdown</h3>
    {fac_table_html}
    {register_html}
</body>
</html>"""
    return HTML(string=html_content).write_pdf()


# ============================================================
# 📊 EXCEL EXPORT
# ============================================================
def export_portfolio_excel(results, fmv_sources, summary) -> bytes:
    """Generate a multi-sheet Excel export of the portfolio analysis."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Summary sheet
        summary_data = {
            "Metric": [
                "Total FMV", "Pool FMV", "Remaining Pool FMV",
                "Total Exposure", "Total Secured Principal", "Total Allocated FMV",
                "Weighted Avg LTV%", "Aggregate LTV%", "Portfolio Status",
                "Number of Facilities", "Number of Properties",
                "Analysis Date",
            ],
            "Value": [
                summary["total_fmv"], summary["pool_fmv"], summary["remaining_pool"],
                summary["total_exposure"], summary["total_secured_principal"],
                summary["total_alloc_fmv"], summary["wtd_ltv"], summary["aggregate_ltv"],
                "PASS" if summary["overall_pass"] else "FAIL",
                len(st.session_state.loans), len(fmv_sources),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ],
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

        # Facilities sheet
        fac_rows = []
        for r in results:
            fac_rows.append({
                "A/C No.":         r.get("loan_account_id", "N/A"),
                "Facility Type":   r["Loan Type"],
                "Principal":       r["Principal"],
                "Mode":            r.get("Collateral_Mode", "pool"),
                "Assigned FMV":    r["Assigned FMV"],
                "Pool FMV":        r["Pool FMV"],
                "Total FMV":       r["Total FMV"],
                "LTV%":            r.get("LTV%") if r.get("LTV%") is not None else "N/A",
                "Max LTV%":        r.get("Max LTV%") if r.get("Max LTV%") is not None else "N/A",
                "Status":          "PASS" if r["Pass_Status"] else "FAIL",
                "Override":        "Yes" if r.get("override_ltv") else "No",
                "Tied Properties": len(r.get("tied_property_ids", [])),
                "Exempt Reason":   r.get("Exempt_Reason") or "-",
            })
        if fac_rows:
            pd.DataFrame(fac_rows).to_excel(writer, sheet_name="Facilities", index=False)

        # Properties sheet
        prop_rows = []
        for s in fmv_sources:
            prop_rows.append({
                "Property Reference": s.get("Plot", ""),
                "Owner":              s.get("Owner", ""),
                "FMV":                s.get("Amount", 0),
                "Type":               "Assigned" if s.get("id") in summary["assigned_collateral_ids"] else "Pool",
            })
        if prop_rows:
            pd.DataFrame(prop_rows).to_excel(writer, sheet_name="Properties", index=False)

    buf.seek(0)
    return buf.getvalue()


# ============================================================
# 📐 HEADER (top bar)
# ============================================================
def render_header():
    """Persistent top header with brand and user."""
    username = st.session_state.get("auth_username", "")
    initials = (username[:2].upper() if username else "U")
    st.markdown(f"""
    <div class="top-header">
        <div class="brand">
            <div class="brand-icon">🏦</div>
            <div class="brand-text">
                <div class="brand-name">LTV Analysis Engine</div>
                <div class="brand-tag">Institutional Lending Platform · v2.0</div>
            </div>
        </div>
        <div class="header-actions">
            <div class="user-pill">
                <div class="user-avatar">{initials}</div>
                <div class="user-name">{esc(username)}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 📐 SIDEBAR — Quick-Add Workbench
# ============================================================
def render_sidebar():
    """Sidebar acts as a quick-add workbench for properties and facilities."""
    with st.sidebar:
        st.markdown("### ⚡ Quick Add")
        st.markdown(
            "<div style='font-size:0.72rem; color:#94A3B8; margin-bottom:0.5rem; "
            "text-transform:uppercase; letter-spacing:0.08em; font-weight:600;'>Workbench</div>",
            unsafe_allow_html=True,
        )

        # ----- Add Property -----
        with st.expander("➕ Add Property", expanded=False):
            sb_plot  = st.text_input("Reference", placeholder="e.g. Plot 42-B, Sector 7",
                                      key="sb_plot", label_visibility="visible")
            sb_owner = st.text_input("Owner", placeholder="Owner name",
                                      key="sb_owner", label_visibility="visible")
            sb_fmv   = st.number_input("FMV (Rs.)", min_value=0.0, step=50000.0,
                                        key="sb_fmv_amt")
            if st.button("Add Property", key="sb_add_prop", type="primary"):
                if sb_fmv <= 0:
                    st.error("FMV must be greater than 0.")
                elif not sb_plot.strip():
                    st.error("Enter a property reference.")
                else:
                    fid = _next_fmv_id()
                    st.session_state.fmv_sources.append({
                        "id": fid, "Plot": sb_plot.strip(),
                        "Owner": sb_owner.strip(), "Amount": sb_fmv,
                    })
                    st.toast(f"✅ Added: {sb_plot.strip()}", icon="🏠")
                    st.rerun()

        # ----- Add Loan Facility -----
        with st.expander("➕ Add Facility", expanded=False):
            policy_dict    = get_policy_dict()
            loan_type_list = list(policy_dict.keys())

            if not loan_type_list:
                st.info("No facility types configured.")
            else:
                l_type = st.selectbox("Facility Type", loan_type_list, key="sb_loan_type")
                l_amt  = st.number_input("Principal (Rs.)", step=10000.0, min_value=0.0,
                                          key="sb_loan_principal")
                max_ltv_sel   = policy_dict.get(l_type)
                selected_colls, coll_mode, tie_up_colls, override_ltv = [], "pool", [], False

                if max_ltv_sel is not None:
                    override_ltv = st.checkbox(
                        "Override — no LTV required", value=False, key="sb_override_ltv",
                        help="Mark this facility as LTV-exempt (credit authority approval required).",
                    )
                    if not override_ltv:
                        use_dedicated = st.checkbox(
                            "Assign dedicated collateral?", value=False, key="sb_use_dedicated",
                            help="Link specific properties exclusively to this facility.",
                        )
                        coll_mode = "assigned" if use_dedicated else "pool"
                        if use_dedicated and st.session_state.fmv_sources:
                            already_assigned = _get_assigned_in_use()
                            coll_options = {}
                            for s in st.session_state.fmv_sources:
                                sid   = s.get("id")
                                base  = f"{s.get('Plot','?')} · Rs.{s.get('Amount',0):,.0f}"
                                label = f"[In Use] {base}" if sid in already_assigned else base
                                coll_options[label] = sid
                            sel_labels = st.multiselect("Select Collateral(s)",
                                                         options=list(coll_options.keys()),
                                                         key="sb_sel_colls")
                            selected_colls = [coll_options[lbl] for lbl in sel_labels]
                            overlap        = [c for c in selected_colls if c in already_assigned]
                            if overlap:
                                st.caption("⚠ Selected property already assigned — FMV will be split proportionally.")

                        use_tie_up = st.checkbox(
                            "Tie-up property (additional security)?", value=False,
                            key="sb_use_tie_up",
                            help=("Tied properties provide additional security. "
                                  "Without dedicated collateral, the facility becomes LTV-exempt."),
                        )
                        if use_tie_up and st.session_state.fmv_sources:
                            tie_options = {
                                f"{s.get('Plot','?')} · Rs.{s.get('Amount',0):,.0f}": s.get("id")
                                for s in st.session_state.fmv_sources
                            }
                            tie_sel      = st.multiselect("Select tied properties",
                                                           options=list(tie_options.keys()),
                                                           key="sb_tie_up_props")
                            tie_up_colls = [tie_options[lbl] for lbl in tie_sel]
                else:
                    st.caption("ℹ Unsecured facility — no collateral required.")

                if st.button("Add to Portfolio", key="sb_add_loan", type="primary"):
                    if l_amt <= 0:
                        st.error("Principal must be > 0.")
                    elif (coll_mode == "assigned" and not selected_colls
                          and not override_ltv and not tie_up_colls):
                        st.error("Select collateral, enable Override, or add tie-up.")
                    else:
                        cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
                        if not cap_ok:
                            st.error(f"Cap exceeded: {cap_msg}")
                        else:
                            actual_mode = coll_mode
                            actual_colls = selected_colls
                            if coll_mode == "assigned" and not selected_colls and tie_up_colls:
                                actual_mode = "pool"
                            ac_id = _generate_loan_account_id(l_type)
                            lid   = st.session_state.loan_id_counter
                            st.session_state.loan_id_counter += 1
                            st.session_state.loans.append({
                                "Loan Type":               l_type,
                                "Principal":               l_amt,
                                "_loan_id":                lid,
                                "loan_account_id":         ac_id,
                                "collateral_mode":         actual_mode,
                                "assigned_collateral_ids": actual_colls,
                                "tied_property_ids":       tie_up_colls,
                                "override_ltv":            override_ltv,
                            })
                            st.toast(f"✅ Added [{ac_id}] {l_type}", icon="💼")
                            st.rerun()

        # ----- Portfolio Snapshot -----
        if st.session_state.fmv_sources or st.session_state.loans:
            st.markdown("---")
            st.markdown("### 📋 Portfolio Snapshot")

            assigned_in_use = _get_assigned_in_use()
            tied_in_use_map = _get_tied_in_use()
            n_props = len(st.session_state.fmv_sources)
            n_loans = len(st.session_state.loans)
            total_fmv_all = sum(s["Amount"] for s in st.session_state.fmv_sources)
            st.markdown(
                f"<div style='background:rgba(79,70,229,0.15); border:1px solid rgba(79,70,229,0.3); "
                f"border-radius:10px; padding:0.7rem 0.85rem; margin-bottom:0.6rem; font-size:0.8rem;'>"
                f"<div style='display:flex; justify-content:space-between; margin-bottom:0.3rem;'>"
                f"<span style='color:#94A3B8;'>Properties</span>"
                f"<span style='color:white; font-weight:700;'>{n_props}</span></div>"
                f"<div style='display:flex; justify-content:space-between; margin-bottom:0.3rem;'>"
                f"<span style='color:#94A3B8;'>Facilities</span>"
                f"<span style='color:white; font-weight:700;'>{n_loans}</span></div>"
                f"<div style='display:flex; justify-content:space-between;'>"
                f"<span style='color:#94A3B8;'>Total FMV</span>"
                f"<span style='color:white; font-weight:700; font-family:JetBrains Mono,monospace;'>"
                f"Rs. {total_fmv_all:,.0f}</span></div></div>",
                unsafe_allow_html=True,
            )

            # Recent properties (latest 3)
            if st.session_state.fmv_sources:
                st.markdown(
                    "<div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase; "
                    "letter-spacing:0.08em; font-weight:600; margin:0.4rem 0 0.3rem;'>Properties</div>",
                    unsafe_allow_html=True,
                )
                for src in reversed(st.session_state.fmv_sources[-3:]):
                    sid   = src.get("id")
                    is_a  = sid in assigned_in_use
                    is_t  = sid in tied_in_use_map
                    tag   = "A" if is_a else ("T" if is_t else "P")
                    tag_class = "assigned" if is_a else ("tieup" if is_t else "pool")
                    st.markdown(
                        f"<div class='item-list-card'>"
                        f"<span class='tag {tag_class}'>[{tag}]</span>"
                        f"<span class='name'>{esc(src.get('Plot',''))}</span>"
                        f"<div class='meta'>Rs. {src.get('Amount',0):,.0f}"
                        + (f" · {src.get('Owner','')}" if src.get('Owner') else "")
                        + "</div></div>",
                        unsafe_allow_html=True,
                    )

            # Recent loans (latest 3)
            if st.session_state.loans:
                st.markdown(
                    "<div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase; "
                    "letter-spacing:0.08em; font-weight:600; margin:0.6rem 0 0.3rem;'>Facilities</div>",
                    unsafe_allow_html=True,
                )
                for loan in reversed(st.session_state.loans[-3:]):
                    ac_id = loan.get("loan_account_id", "?")
                    mode  = loan.get("collateral_mode", "pool")
                    tie_n = len(loan.get("tied_property_ids", []))
                    tag_class = ("assigned" if mode == "assigned"
                                 else ("override" if loan.get("override_ltv") else "pool"))
                    tag_letter = ("A" if mode == "assigned"
                                  else ("O" if loan.get("override_ltv") else "P"))
                    if tie_n and loan.get("override_ltv"):
                        tag_letter, tag_class = "O+T", "override"
                    elif tie_n and mode == "pool":
                        tag_letter, tag_class = "T", "tieup"
                    elif tie_n and mode == "assigned":
                        tag_letter, tag_class = "A+T", "assigned"

                    st.markdown(
                        f"<div class='item-list-card'>"
                        f"<span class='tag {tag_class}'>[{tag_letter}]</span>"
                        f"<span class='name'>{esc(loan['Loan Type'])}</span>"
                        f"<div class='meta'>{ac_id} · Rs. {loan['Principal']:,.0f}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        # ----- Footer actions -----
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Sign Out", key="sb_signout", type="secondary", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["auth_username"] = ""
                st.session_state["_login_error"]  = ""
                st.rerun()
        with col_b:
            if st.button("Reset All", key="sb_reset", type="secondary", use_container_width=True):
                for k in ["loans", "fmv_sources", "ltv_policy", "loan_id_counter",
                           "fmv_id_counter", "loan_type_counters", "generated_pdf",
                           "generated_pdf_name", "generated_excel"]:
                    if k in ["loans", "fmv_sources"]:
                        st.session_state[k] = []
                    elif k in ["loan_id_counter", "fmv_id_counter"]:
                        st.session_state[k] = 0
                    elif k == "loan_type_counters":
                        st.session_state[k] = {}
                    elif k == "ltv_policy":
                        st.session_state[k] = copy.deepcopy(DEFAULT_LTV_POLICY)
                    else:
                        st.session_state.pop(k, None)
                st.toast("🗑️ Portfolio reset.", icon="🧹")
                st.rerun()


# ============================================================
# 📐 KPI COMPONENTS
# ============================================================
def render_kpi_card(label: str, value: str, meta: str = "", kind: str = "neutral",
                     meta_icon: str = "") -> str:
    """Render a single KPI card and return HTML string."""
    meta_class = "neu"
    if meta.startswith("+") or "↑" in meta or "✓" in meta or "✅" in meta:
        meta_class = "pos"
    elif meta.startswith("-") or "↓" in meta or "✗" in meta or "⚠" in meta:
        meta_class = "neg"
    meta_html = f'<div class="kpi-meta {meta_class}">{meta_icon} {meta}</div>' if meta else ""
    return f"""
    <div class="kpi-card {kind}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {meta_html}
    </div>
    """


def render_kpi_grid(cards: list) -> str:
    return f'<div class="kpi-grid">{"".join(cards)}</div>'


def section_header(title: str, sub: str = "", icon: str = "📊", kind: str = "neutral") -> str:
    icon_class = "neutral"
    if kind in ("success", "warning", "danger", "purple"):
        icon_class = kind
    return f"""
    <div class="section-head">
        <div>
            <div class="section-title-row">
                <div class="section-icon {icon_class}">{icon}</div>
                <h2 class="section-title">{title}</h2>
            </div>
            {f'<div class="section-sub">{sub}</div>' if sub else ''}
        </div>
    </div>
    """


# ============================================================
# 🏠 TAB 1: DASHBOARD
# ============================================================
def render_dashboard(results, summary):
    total_fmv               = summary["total_fmv"]
    total_exposure          = summary["total_exposure"]
    total_secured_principal = summary["total_secured_principal"]
    wtd_ltv                 = summary["wtd_ltv"]
    aggregate_ltv           = summary["aggregate_ltv"]
    overall_pass            = summary["overall_pass"]

    secured  = [r for r in results if not r["Is_Unsecured"]]
    exempts  = [r for r in results if r["Is_Unsecured"] and r.get("Exempt_Reason") in ("override", "tieup")]
    failed   = [r for r in results if not r["Pass_Status"]]
    no_fmv   = [r for r in results if r.get("No_FMV_Error")]
    pool_fmv_val     = summary["pool_fmv"]
    assigned_fmv_val = total_fmv - pool_fmv_val
    remaining_pool   = summary["remaining_pool"]

    # ---- Status Banner ----
    if not results:
        pass  # empty state below
    elif overall_pass and not no_fmv:
        st.markdown(
            '<div class="status-banner status-pass">'
            '<span class="status-dot"></span>'
            'PORTFOLIO APPROVED — All Facilities Within LTV Limits'
            '</div>',
            unsafe_allow_html=True,
        )
    elif no_fmv:
        st.markdown(
            '<div class="status-banner status-warn">'
            '<span class="status-dot"></span>'
            f'ACTION REQUIRED — {len(no_fmv)} Facility(s) Have No Collateral Allocated'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-banner status-fail">'
            '<span class="status-dot"></span>'
            f'PORTFOLIO DECLINED — {len(failed)} Facility(s) Exceed Maximum LTV'
            '</div>',
            unsafe_allow_html=True,
        )

    # ---- KPI Grid ----
    wtd_kind = ("success" if wtd_ltv <= 50 else ("warning" if wtd_ltv <= 65 else "danger"))
    agg_kind = ("success" if aggregate_ltv <= 50 else ("warning" if aggregate_ltv <= 65 else "danger"))
    pass_count = len(secured) - len(failed)
    pass_kind  = ("success" if (len(secured) == 0 or pass_count == len(secured)) else "danger")

    cards = [
        render_kpi_card(
            "Total Exposure", f"Rs. {total_exposure:,.0f}",
            f"{len(st.session_state.loans)} facilities", "neutral", "💼",
        ),
        render_kpi_card(
            "Total Collateral FMV", f"Rs. {total_fmv:,.0f}",
            f"{len(st.session_state.fmv_sources)} properties", "purple", "🏠",
        ),
        render_kpi_card(
            "Weighted Avg LTV", f"{wtd_ltv:.2f}%",
            "Across allocated FMV", wtd_kind, "📐",
        ),
        render_kpi_card(
            "Aggregate LTV", f"{aggregate_ltv:.2f}%",
            f"Rs. {total_secured_principal:,.0f} / Rs. {total_fmv:,.0f}", agg_kind, "🎯",
        ),
        render_kpi_card(
            "Pool Remaining", f"Rs. {remaining_pool:,.0f}",
            f"of Rs. {pool_fmv_val:,.0f} pool FMV",
            ("success" if remaining_pool > 0 else "warning"), "💧",
        ),
        render_kpi_card(
            "Pass / Fail", f"{pass_count} / {len(failed)}",
            f"{len(exempts)} exempt", pass_kind,
            ("✅" if pass_count == len(secured) and len(secured) > 0 else "⚠"),
        ),
    ]
    st.markdown(render_kpi_grid(cards), unsafe_allow_html=True)

    # ---- Charts Row ----
    if results:
        chart_l, chart_r = st.columns([1.1, 1])

        # Collateral allocation donut
        with chart_l:
            st.markdown("#### Collateral Allocation", unsafe_allow_html=False)
            assigned_props = sum(1 for s in st.session_state.fmv_sources
                                 if s.get("id") in summary["assigned_collateral_ids"])
            pool_props     = len(st.session_state.fmv_sources) - assigned_props

            fig = go.Figure(data=[go.Pie(
                labels=["Assigned", "Pool"],
                values=[assigned_fmv_val if assigned_fmv_val > 0 else 0.0001,
                        pool_fmv_val     if pool_fmv_val     > 0 else 0.0001],
                hole=0.65,
                marker=dict(colors=["#4F46E5", "#10B981"], line=dict(color="#FFFFFF", width=3)),
                textinfo="label+percent",
                textposition="outside",
                textfont=dict(size=12, color="#0F172A", family="Inter"),
                hovertemplate="<b>%{label}</b><br>FMV: Rs. %{value:,.0f}<br>%{percent}<extra></extra>",
            )])
            fig.update_layout(
                showlegend=True, height=280, margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5,
                            font=dict(family="Inter", size=11, color="#475569")),
                annotations=[dict(
                    text=f"<b>{assigned_props + pool_props}</b><br><span style='font-size:10px; color:#64748B'>Properties</span>",
                    x=0.5, y=0.5, font_size=18, font_color="#0F172A", showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # LTV bar chart per facility
        with chart_r:
            st.markdown("#### LTV by Facility", unsafe_allow_html=False)
            secured_sorted = sorted(
                [r for r in results if not r["Is_Unsecured"]],
                key=lambda r: -(r.get("LTV%") or 0),
            )
            if secured_sorted:
                fac_labels = [f"{r.get('loan_account_id','?')}<br><span style='font-size:9px;color:#64748B'>{r['Loan Type'][:18]}</span>"
                              for r in secured_sorted]
                ltv_values  = [r.get("LTV%") or 0 for r in secured_sorted]
                max_ltv_vals = [r.get("Max LTV%") or 0 for r in secured_sorted]
                colors = ["#059669" if (r.get("LTV%") or 0) <= r.get("Max LTV%", 100) * 0.8
                          else ("#D97706" if (r.get("LTV%") or 0) <= r.get("Max LTV%", 100)
                                else "#DC2626")
                          for r in secured_sorted]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=fac_labels, y=ltv_values, name="Actual LTV%",
                    marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
                    text=[f"{v:.1f}%" for v in ltv_values],
                    textposition="outside", textfont=dict(size=10, family="Inter", color="#0F172A"),
                    hovertemplate="<b>%{x}</b><br>LTV: %{y:.2f}%<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=fac_labels, y=max_ltv_vals, name="Max LTV%",
                    mode="markers", marker=dict(symbol="line-ns-open", size=14,
                                                 color="#DC2626", line=dict(width=2)),
                    hovertemplate="Max: %{y:.0f}%<extra></extra>",
                ))
                fig.update_layout(
                    height=280, margin=dict(t=20, b=60, l=40, r=20),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter", size=10, color="#475569"),
                    yaxis=dict(title="LTV %", gridcolor="#E2E8F0", zeroline=False, ticksuffix="%"),
                    xaxis=dict(showgrid=False),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5,
                                font=dict(size=10)),
                    barmode="group",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No facilities with active LTV calculations.")

        # ---- Quick Stats Strip ----
        st.markdown("#### Portfolio Breakdown", unsafe_allow_html=False)
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown(f"""
            <div class="kpi-card neutral">
                <div class="kpi-label">Active Facilities</div>
                <div class="kpi-value">{len(secured)}</div>
                <div class="kpi-meta neu">LTV calculations applied</div>
            </div>""", unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="kpi-card purple">
                <div class="kpi-label">Exempt Facilities</div>
                <div class="kpi-value">{len(exempts)}</div>
                <div class="kpi-meta neu">Override or tie-up only</div>
            </div>""", unsafe_allow_html=True)
        with b3:
            st.markdown(f"""
            <div class="kpi-card success">
                <div class="kpi-label">Assigned FMV</div>
                <div class="kpi-value" style="font-size:1.3rem;">Rs. {assigned_fmv_val:,.0f}</div>
                <div class="kpi-meta neu">{assigned_props} dedicated properties</div>
            </div>""", unsafe_allow_html=True)
        with b4:
            st.markdown(f"""
            <div class="kpi-card success">
                <div class="kpi-label">Pool FMV</div>
                <div class="kpi-value" style="font-size:1.3rem;">Rs. {pool_fmv_val:,.0f}</div>
                <div class="kpi-meta neu">{pool_props} shared properties</div>
            </div>""", unsafe_allow_html=True)

        # ---- Recent Activity / Alerts ----
        if no_fmv or failed:
            st.markdown("#### ⚠ Alerts & Action Items", unsafe_allow_html=False)
            for r in no_fmv:
                st.markdown(
                    f'<div class="notice-strip"><span>🟠</span> '
                    f'<b>[{esc(r.get("loan_account_id","?"))}] {esc(r["Loan Type"])}</b> '
                    f'has no collateral allocated. Add properties or enable Override.</div>',
                    unsafe_allow_html=True,
                )
            for r in failed:
                ltv_val = r.get("LTV%")
                max_val = r.get("Max LTV%", 0)
                st.markdown(
                    f'<div class="notice-strip" style="background:linear-gradient(135deg,#FEE2E2 0%,#FECACA 100%); '
                    f'border-color:#FCA5A5; color:#991B1B;">'
                    f'<span>🔴</span> '
                    f'<b>[{esc(r.get("loan_account_id","?"))}] {esc(r["Loan Type"])}</b> '
                    f'LTV {ltv_val:.2f}% exceeds max of {max_val:.0f}%.</div>',
                    unsafe_allow_html=True,
                )


# ============================================================
# 📦 TAB 2: PORTFOLIO
# ============================================================
def render_portfolio(results, summary):
    has_ties      = _portfolio_has_ties()
    has_overrides = any(l.get("override_ltv") for l in st.session_state.loans)
    tied_in_use   = _get_tied_in_use()

    # ---- Properties Table ----
    st.markdown(section_header(
        "Collateral Properties",
        f"{len(st.session_state.fmv_sources)} properties · Rs. {sum(s['Amount'] for s in st.session_state.fmv_sources):,.0f} total FMV",
        "🏠", "neutral",
    ), unsafe_allow_html=True)

    if not st.session_state.fmv_sources:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🏠</div>
            <div class="empty-title">No properties added yet</div>
            <div class="empty-sub">Add collateral properties via the sidebar <b>Quick Add → Add Property</b>, or upload an Excel file in the <b>Reports</b> tab for bulk import.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Property editor
        prop_df_data = []
        assigned_coll_ids = summary["assigned_collateral_ids"]
        for i, src in enumerate(st.session_state.fmv_sources):
            sid     = src.get("id")
            owners  = _get_assigned_in_use()
            tied_n  = len(tied_in_use.get(sid, []))
            n_assigned_uses = len([
                ln for ln in st.session_state.loans
                if ln.get("collateral_mode") == "assigned" and sid in ln.get("assigned_collateral_ids", [])
            ])
            n_shared = max(0, n_assigned_uses - 1)
            prop_df_data.append({
                "Ref":           src.get("Plot", ""),
                "Owner":         src.get("Owner", "") or "—",
                "FMV (Rs.)":     f"{src.get('Amount', 0):,.0f}",
                "Type":          "Assigned" if sid in assigned_coll_ids else "Pool",
                "Used By":       n_assigned_uses if n_assigned_uses > 0 else "Pool",
                "Shared With":   n_shared if n_shared > 0 else "—",
                "Tied":          tied_n if tied_n > 0 else "—",
                "_id":           sid,
            })
        prop_df = pd.DataFrame(prop_df_data)
        edited = st.data_editor(
            prop_df.drop(columns=["_id"]),
            hide_index=True, use_container_width=True,
            column_config={
                "FMV (Rs.)": st.column_config.TextColumn("FMV (Rs.)", disabled=True),
                "Type":      st.column_config.TextColumn("Type",     disabled=True),
                "Used By":   st.column_config.TextColumn("Used By",  disabled=True),
                "Shared With": st.column_config.TextColumn("Shared", disabled=True),
                "Tied":      st.column_config.TextColumn("Tied",     disabled=True),
            },
            disabled=["Type", "Used By", "Shared With", "Tied"],
            key="prop_editor", height=min(420, 80 + len(prop_df_data) * 38),
        )

        # Delete buttons
        with st.expander("Manage Properties", expanded=False):
            for i, src in enumerate(st.session_state.fmv_sources):
                c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
                with c1:
                    st.markdown(f"**{src.get('Plot','?')}**")
                with c2:
                    st.caption(src.get("Owner", "") or "No owner")
                with c3:
                    st.markdown(f"`Rs. {src.get('Amount',0):,.0f}`")
                with c4:
                    if st.button("Remove", key=f"del_p_{src.get('id')}"):
                        sid = src.get("id")
                        st.session_state.fmv_sources = [
                            s for s in st.session_state.fmv_sources if s.get("id") != sid
                        ]
                        for loan in st.session_state.loans:
                            for field in ("assigned_collateral_ids", "tied_property_ids"):
                                lst = loan.get(field, [])
                                if sid in lst:
                                    lst.remove(sid)
                        st.toast("🗑️ Property removed.", icon="🗑️")
                        st.rerun()

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ---- Facilities Table ----
    st.markdown(section_header(
        "Loan Facilities",
        f"{len(st.session_state.loans)} facilities · Rs. {sum(l['Principal'] for l in st.session_state.loans):,.0f} total exposure",
        "💼", "neutral",
    ), unsafe_allow_html=True)

    if not st.session_state.loans:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">💼</div>
            <div class="empty-title">No facilities in the portfolio</div>
            <div class="empty-sub">Add loan facilities via the sidebar <b>Quick Add → Add Facility</b>. Each facility can use assigned collateral, draw from the pool, use tie-up properties, or be marked LTV-exempt.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        fac_df_data = []
        for loan in st.session_state.loans:
            res = next((r for r in results if r.get("_loan_id") == loan.get("_loan_id")), None)
            if not res:
                continue
            mode_lbl = {"pool": "Pool", "assigned": "Assigned"}.get(loan.get("collateral_mode", "pool"), "Pool")
            if loan.get("override_ltv"):
                mode_lbl = "Override"
            flags = []
            if loan.get("tied_property_ids"):
                if loan.get("collateral_mode") == "assigned" and loan.get("assigned_collateral_ids"):
                    flags.append("Tie-up (Addl.)")
                else:
                    flags.append("Tie-up (Exempt)")
            fac_df_data.append({
                "A/C No.":      loan.get("loan_account_id", "N/A"),
                "Facility":     loan["Loan Type"],
                "Principal":    f"Rs. {loan['Principal']:,.0f}",
                "Mode":         mode_lbl,
                "LTV%":         (f"{res['LTV%']:.2f}%" if res.get("LTV%") is not None else (
                                  "Override" if loan.get("override_ltv") else
                                  ("Tie-up Exempt" if loan.get("tied_property_ids") and not (loan.get("collateral_mode") == "assigned" and loan.get("assigned_collateral_ids")) else "N/A")
                                )),
                "Max LTV":      (f"{res.get('Max LTV%'):.0f}%" if res.get("Max LTV%") is not None else "N/A"),
                "Surplus":      _format_surplus(res),
                "Status":       "PASS" if res["Pass_Status"] else "FAIL",
                "Flags":        " · ".join(flags) if flags else "—",
            })
        st.dataframe(pd.DataFrame(fac_df_data), hide_index=True, use_container_width=True,
                     height=min(420, 80 + len(fac_df_data) * 38))

        # ---- Facility manager ----
        with st.expander("Manage Facilities", expanded=False):
            for loan in st.session_state.loans:
                c1, c2, c3, c4 = st.columns([1.5, 3, 2, 1])
                ac_id = loan.get("loan_account_id", "?")
                with c1:
                    st.markdown(f"<span class='badge badge-id'>{ac_id}</span>", unsafe_allow_html=True)
                with c2:
                    badges = []
                    if loan.get("override_ltv"):
                        badges.append('<span class="badge badge-warn">Override</span>')
                    if loan.get("tied_property_ids"):
                        has_both = loan.get("collateral_mode") == "assigned" and bool(loan.get("assigned_collateral_ids"))
                        if has_both:
                            badges.append('<span class="badge badge-purple">Tie-up (Addl.)</span>')
                        else:
                            badges.append('<span class="badge badge-purple">Tie-up (Exempt)</span>')
                    badges_html = " ".join(badges) if badges else ""
                    st.markdown(
                        f"**{loan['Loan Type']}** · Rs. {loan['Principal']:,.0f} {badges_html}",
                        unsafe_allow_html=True,
                    )
                with c3:
                    names = _get_collateral_names(loan.get("assigned_collateral_ids", []),
                                                   st.session_state.fmv_sources)
                    label = ", ".join(names[:2]) + ("…" if len(names) > 2 else "") if names else "Pool"
                    tied_n = len(loan.get("tied_property_ids", []))
                    if tied_n:
                        label += f" + {tied_n} tied"
                    st.caption(label or "Pool")
                with c4:
                    if st.button("Remove", key=f"rm_l_{loan['_loan_id']}"):
                        st.session_state.loans = [
                            l for l in st.session_state.loans if l["_loan_id"] != loan["_loan_id"]
                        ]
                        st.toast("🗑️ Facility removed.", icon="🗑️")
                        st.rerun()


def _format_surplus(res) -> str:
    if res.get("Is_Unsecured"):
        return "N/A"
    if res.get("No_FMV_Error"):
        return "No FMV"
    max_ltv = res.get("Max LTV%")
    if max_ltv is None:
        return "N/A"
    req_fmv = res["Principal"] / (max_ltv / 100.0)
    sv = res.get("Total FMV", 0.0) - req_fmv
    return f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"


# ============================================================
# 📈 TAB 3: ANALYSIS
# ============================================================
def render_analysis(results, summary):
    has_ties      = _portfolio_has_ties()
    has_overrides = any(l.get("override_ltv") for l in st.session_state.loans)

    st.markdown(section_header(
        "LTV Analysis",
        "Per-facility LTV calculations, waterfall allocation, and visual breakdowns",
        "📐", "purple",
    ), unsafe_allow_html=True)

    if not results:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <div class="empty-title">No data to analyze</div>
            <div class="empty-sub">Add properties and facilities to see detailed LTV analysis.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    secured = [r for r in results if not r["Is_Unsecured"]]
    exempts = [r for r in results if r["Is_Unsecured"] and r.get("Exempt_Reason") in ("override", "tieup")]

    # ---- Facility Cards Grid ----
    if secured or exempts:
        st.markdown("#### Facility Breakdown", unsafe_allow_html=False)
        all_visual = secured + exempts
        cards_html = ""
        for i, row in enumerate(all_visual):
            ac_id  = row.get("loan_account_id", "?")
            is_unsec = row.get("Is_Unsecured", False)
            ltv       = row.get("LTV%")
            max_ltv   = row.get("Max LTV%") or 100
            no_fmv_err = row.get("No_FMV_Error", False)
            exempt_reason = row.get("Exempt_Reason")

            if is_unsec:
                if exempt_reason == "override":
                    badge_html = '<span class="badge badge-warn">Override</span>'
                    ltv_text   = "Overridden"
                    ltv_class  = "idle"
                    bar_cls    = "idle"
                    pill_text  = "No LTV Required"
                    pill_cls   = "pill-na"
                else:
                    badge_html = '<span class="badge badge-purple">Tie-up Exempt</span>'
                    ltv_text   = "Tie-up Exempt"
                    ltv_class  = "idle"
                    bar_cls    = "idle"
                    pill_text  = "No LTV Required"
                    pill_cls   = "pill-na"
            elif no_fmv_err or ltv is None:
                badge_html = '<span class="badge badge-fail">No FMV</span>'
                ltv_text   = "—"
                ltv_class  = "fail"
                bar_cls    = "fail"
                pill_text  = "No collateral allocated"
                pill_cls   = "pill-neg"
            else:
                pct_bar = min((ltv / max_ltv) * 100, 100)
                badge_html = ('<span class="badge badge-pass">Pass</span>' if row["Pass_Status"]
                              else '<span class="badge badge-fail">Fail</span>')
                ltv_text = f"{ltv:.2f}%"
                ltv_class = "ok" if ltv <= max_ltv * 0.85 else ("warn" if ltv <= max_ltv else "fail")
                bar_cls = ltv_class
                sv = row.get("Total FMV", 0.0) - row["Principal"] / (max_ltv / 100.0)
                pill_text = (f"Surplus Rs. {sv:,.0f}" if sv >= 0 else f"Short Rs. {abs(sv):,.0f}")
                pill_cls  = ("pill-pos" if sv >= 0 else "pill-neg")

            mode     = row.get("Collateral_Mode", "pool")
            mode_lbl = "Pool" if mode == "pool" else "Assigned"
            if row.get("override_ltv"):
                mode_lbl = "Override"
            has_both = (not is_unsec and row.get("tied_property_ids")
                        and mode == "assigned" and bool(row.get("assigned_collateral_ids")))
            if has_both:
                mode_lbl += " + Tied"
            coll_names = row.get("Collateral_Names", [])
            coll_text  = (", ".join(coll_names[:2]) + ("…" if len(coll_names) > 2 else "")
                          if coll_names else "Pool")

            if is_unsec or no_fmv_err or ltv is None:
                bar_pct = 100
            else:
                bar_pct = min((ltv / max_ltv) * 100, 100)

            cards_html += f"""
            <div class="fac-card">
                <div class="fac-card-head">
                    <div class="fac-type">{esc(row['Loan Type'])}</div>
                    {badge_html}
                </div>
                <div class="fac-ac">{ac_id}</div>
                <div class="fac-coll">{esc(mode_lbl)} · {esc(coll_text)}</div>
                <div class="fac-ltv {ltv_class}">{ltv_text}</div>
                <div class="fac-meta">Max: {max_ltv:.0f}% · FMV: Rs.{row['Total FMV']:,.0f}</div>
                <span class="pill {pill_cls}">{pill_text}</span>
                <div class="ltv-bar-wrap"><div class="ltv-bar-fill {bar_cls}" style="width:{bar_pct:.1f}%"></div></div>
            </div>
            """

        # Use Streamlit columns for proper grid layout
        n = len(all_visual) + 1
        n_cols = min(n, 4)
        cols = st.columns(n_cols)
        for i, row in enumerate(all_visual):
            with cols[i % n_cols]:
                # Render same card via Streamlit markdown for that one item
                ac_id  = row.get("loan_account_id", "?")
                is_unsec = row.get("Is_Unsecured", False)
                ltv       = row.get("LTV%")
                max_ltv   = row.get("Max LTV%") or 100
                no_fmv_err = row.get("No_FMV_Error", False)
                exempt_reason = row.get("Exempt_Reason")

                if is_unsec:
                    if exempt_reason == "override":
                        badge_html = '<span class="badge badge-warn">Override</span>'
                        ltv_text   = "Overridden"
                        ltv_class  = "idle"
                        bar_cls    = "idle"
                        pill_text  = "No LTV Required"
                        pill_cls   = "pill-na"
                    else:
                        badge_html = '<span class="badge badge-purple">Tie-up Exempt</span>'
                        ltv_text   = "Tie-up Exempt"
                        ltv_class  = "idle"
                        bar_cls    = "idle"
                        pill_text  = "No LTV Required"
                        pill_cls   = "pill-na"
                elif no_fmv_err or ltv is None:
                    badge_html = '<span class="badge badge-fail">No FMV</span>'
                    ltv_text   = "—"
                    ltv_class  = "fail"
                    bar_cls    = "fail"
                    pill_text  = "No collateral allocated"
                    pill_cls   = "pill-neg"
                else:
                    pct_bar = min((ltv / max_ltv) * 100, 100)
                    badge_html = ('<span class="badge badge-pass">Pass</span>' if row["Pass_Status"]
                                  else '<span class="badge badge-fail">Fail</span>')
                    ltv_text = f"{ltv:.2f}%"
                    ltv_class = "ok" if ltv <= max_ltv * 0.85 else ("warn" if ltv <= max_ltv else "fail")
                    bar_cls = ltv_class
                    sv = row.get("Total FMV", 0.0) - row["Principal"] / (max_ltv / 100.0)
                    pill_text = (f"Surplus Rs. {sv:,.0f}" if sv >= 0 else f"Short Rs. {abs(sv):,.0f}")
                    pill_cls  = ("pill-pos" if sv >= 0 else "pill-neg")

                mode     = row.get("Collateral_Mode", "pool")
                mode_lbl = "Pool" if mode == "pool" else "Assigned"
                if row.get("override_ltv"):
                    mode_lbl = "Override"
                has_both = (not is_unsec and row.get("tied_property_ids")
                            and mode == "assigned" and bool(row.get("assigned_collateral_ids")))
                if has_both:
                    mode_lbl += " + Tied"
                coll_names = row.get("Collateral_Names", [])
                coll_text  = (", ".join(coll_names[:2]) + ("…" if len(coll_names) > 2 else "")
                              if coll_names else "Pool")
                bar_pct = 100 if (is_unsec or no_fmv_err or ltv is None) else min((ltv / max_ltv) * 100, 100)

                st.markdown(f"""
                <div class="fac-card">
                    <div class="fac-card-head">
                        <div class="fac-type">{esc(row['Loan Type'])}</div>
                        {badge_html}
                    </div>
                    <div class="fac-ac">{ac_id}</div>
                    <div class="fac-coll">{esc(mode_lbl)} · {esc(coll_text)}</div>
                    <div class="fac-ltv {ltv_class}">{ltv_text}</div>
                    <div class="fac-meta">Max: {max_ltv:.0f}% · FMV: Rs.{row['Total FMV']:,.0f}</div>
                    <span class="pill {pill_cls}">{pill_text}</span>
                    <div class="ltv-bar-wrap"><div class="ltv-bar-fill {bar_cls}" style="width:{bar_pct:.1f}%"></div></div>
                </div>
                """, unsafe_allow_html=True)

        # Aggregate card
        agg_col_idx = len(all_visual) % n_cols
        with cols[agg_col_idx]:
            aggregate_ltv = summary["aggregate_ltv"]
            agg_fill = "ok" if aggregate_ltv <= 50 else ("warn" if aggregate_ltv <= 65 else "fail")
            agg_color = "#059669" if aggregate_ltv <= 70 else "#DC2626"
            agg_pill  = ('<span class="pill pill-pos">Within limits</span>' if aggregate_ltv <= 70
                          else '<span class="pill pill-neg">Exceeds limit</span>')
            st.markdown(f"""
            <div class="fac-card" style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%); border-color:#334155;">
                <div class="fac-card-head">
                    <div class="fac-type" style="color:white;">AGGREGATE</div>
                    <span class="badge badge-info">All Facilities</span>
                </div>
                <div class="fac-ac" style="background:rgba(255,255,255,0.15); color:#A5B4FC;">PORTFOLIO</div>
                <div class="fac-coll" style="color:#94A3B8;">Combined exposure</div>
                <div class="fac-ltv" style="color:{agg_color};">{aggregate_ltv:.2f}%</div>
                <div class="fac-meta" style="color:#94A3B8;">
                    Rs. {summary['total_secured_principal']:,.0f} / Rs. {summary['total_fmv']:,.0f}
                </div>
                {agg_pill}
                <div class="ltv-bar-wrap"><div class="ltv-bar-fill {agg_fill}" style="width:{min(aggregate_ltv,100):.1f}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    # ---- Detailed Breakdown Table ----
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown("#### Detailed Breakdown", unsafe_allow_html=False)

    def display_sort_key(r):
        m = r.get("Max LTV%")
        if m is None:
            return (2, 0)
        return (0 if m <= 50 else 1, -(r.get("Principal", 0)))

    sorted_display = sorted(results, key=display_sort_key)
    disp_rows      = []
    fmv_id_map     = {s["id"]: s["Plot"] for s in st.session_state.fmv_sources}

    for r in sorted_display:
        is_unsec      = r["Is_Unsecured"]
        no_fmv_err    = r.get("No_FMV_Error", False)
        ltv_val       = r.get("LTV%")
        max_ltv       = r.get("Max LTV%")
        exempt_reason = r.get("Exempt_Reason")
        override_flag = r.get("override_ltv", False)
        tieup_flag    = bool(r.get("tied_property_ids"))
        has_both = (
            not is_unsec and tieup_flag
            and r.get("collateral_mode") == "assigned"
            and bool(r.get("assigned_collateral_ids"))
        )

        if is_unsec:
            ltv_disp = "Overridden" if exempt_reason == "override" else (
                       "Tie-up Exempt" if exempt_reason == "tieup" else "N/A (Unsecured)")
        elif no_fmv_err:
            ltv_disp = "No FMV"
        elif ltv_val is None:
            ltv_disp = "N/A"
        else:
            ltv_disp = f"{ltv_val:.2f}%"

        if is_unsec or max_ltv is None:
            surplus_disp = "N/A"
        elif no_fmv_err:
            surplus_disp = "No FMV"
        else:
            req_fmv = r["Principal"] / (max_ltv / 100.0)
            sv      = r.get("Total FMV", 0.0) - req_fmv
            surplus_disp = f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"

        flags_list = []
        if override_flag: flags_list.append("Override")
        if tieup_flag:    flags_list.append("Tie-up (Addl.)" if has_both else "Tie-up (Exempt)")

        row = {
            "A/C No.":             r.get("loan_account_id", "N/A"),
            "Facility":            r["Loan Type"],
            "Principal":           f"Rs. {r['Principal']:,.0f}",
            "Assigned FMV":        "N/A" if is_unsec else f"Rs. {r['Assigned FMV']:,.0f}",
            "Pool FMV":            "N/A" if is_unsec else f"Rs. {r['Pool FMV']:,.0f}",
            "Total FMV":           "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
            "LTV%":                ltv_disp,
            "Max LTV":             "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
            "Surplus/(Shortfall)": surplus_disp,
            "Status":              "PASS" if r["Pass_Status"] else "FAIL",
            "Flags":               " · ".join(flags_list) if flags_list else "—",
        }
        if has_ties:
            tied_names = [fmv_id_map.get(cid, str(cid)) for cid in r.get("tied_property_ids", [])]
            row["Tied Properties"] = ", ".join(tied_names) if tied_names else "N/A"
        disp_rows.append(row)

    agg_row = {
        "A/C No.": "AGG", "Facility": "AGGREGATE",
        "Principal": f"Rs. {summary['total_exposure']:,.0f}",
        "Assigned FMV": "—", "Pool FMV": "—",
        "Total FMV": f"Rs. {summary['total_fmv']:,.0f}",
        "LTV%": f"{summary['aggregate_ltv']:.2f}%",
        "Max LTV": "—",
        "Surplus/(Shortfall)": "—",
        "Status": "PASS" if summary["aggregate_ltv"] <= 70 else "FAIL",
        "Flags": "—",
    }
    if has_ties:
        agg_row["Tied Properties"] = "—"
    disp_rows.append(agg_row)

    st.dataframe(pd.DataFrame(disp_rows), hide_index=True, use_container_width=True,
                 height=min(520, 80 + len(disp_rows) * 38))

    # ---- Override / Tie-up Register ----
    exempt_register = [
        r for r in results
        if r.get("Is_Unsecured") and r.get("Exempt_Reason") in ("override", "tieup")
    ]
    addl_sec_register = [
        r for r in results
        if not r.get("Is_Unsecured")
        and bool(r.get("tied_property_ids"))
        and r.get("collateral_mode") == "assigned"
        and bool(r.get("assigned_collateral_ids"))
    ]

    if exempt_register or addl_sec_register:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.expander("📋 LTV Override, Tie-up & Additional Security Register", expanded=False):
            st.caption(
                "Exempt facilities are excluded from LTV calculation. "
                "Facilities with both assigned collateral and tie-up have LTV calculated normally; "
                "tie-up serves as additional security only. Manual overrides must be sanctioned by credit authority."
            )
            fmv_src_map   = {s["id"]: s for s in st.session_state.fmv_sources}
            register_rows = []
            for r in exempt_register:
                tied_names, tied_owners, tied_fmv_total = [], [], 0.0
                for cid in r.get("tied_property_ids", []):
                    src = fmv_src_map.get(cid)
                    if src:
                        tied_names.append(src.get("Plot", ""))
                        tied_owners.append(src.get("Owner", "") or "N/A")
                        tied_fmv_total += src.get("Amount", 0.0)
                unique_owners = list(dict.fromkeys(tied_owners))
                exempt_reason = r.get("Exempt_Reason", "")
                exempt_label  = ("Manual LTV Override" if exempt_reason == "override"
                                  else "Tie-up Exempt (No Collateral)")
                register_rows.append({
                    "A/C No.":         r.get("loan_account_id", "?"),
                    "Facility Type":   r["Loan Type"],
                    "Principal (Rs.)": f"Rs. {r['Principal']:,.0f}",
                    "Type":            exempt_label,
                    "Tied Properties": ", ".join(tied_names) if tied_names else "—",
                    "Tied Owner(s)":   ", ".join(unique_owners) if unique_owners else "—",
                    "Tied FMV (Rs.)":  f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "—",
                    "LTV":             "No LTV Required",
                })
            for r in addl_sec_register:
                tied_names, tied_owners, tied_fmv_total = [], [], 0.0
                for cid in r.get("tied_property_ids", []):
                    src = fmv_src_map.get(cid)
                    if src:
                        tied_names.append(src.get("Plot", ""))
                        tied_owners.append(src.get("Owner", "") or "N/A")
                        tied_fmv_total += src.get("Amount", 0.0)
                unique_owners = list(dict.fromkeys(tied_owners))
                ltv_val = r.get("LTV%")
                ltv_str = f"{ltv_val:.2f}%" if ltv_val is not None else "N/A"
                register_rows.append({
                    "A/C No.":         r.get("loan_account_id", "?"),
                    "Facility Type":   r["Loan Type"],
                    "Principal (Rs.)": f"Rs. {r['Principal']:,.0f}",
                    "Type":            "Addl. Security (LTV Active)",
                    "Tied Properties": ", ".join(tied_names) if tied_names else "—",
                    "Tied Owner(s)":   ", ".join(unique_owners) if unique_owners else "—",
                    "Tied FMV (Rs.)":  f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "—",
                    "LTV":             ltv_str,
                })
            st.dataframe(pd.DataFrame(register_rows), hide_index=True, use_container_width=True)


# ============================================================
# 📑 TAB 4: REPORTS
# ============================================================
def render_reports(results, summary):
    st.markdown(section_header(
        "Reports & Export",
        "Generate professional PDF reports and Excel exports for credit committee review",
        "📑", "purple",
    ), unsafe_allow_html=True)

    if not results:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📑</div>
            <div class="empty-title">Nothing to export yet</div>
            <div class="empty-sub">Add properties and facilities first, then return here to generate your report.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    rep_l, rep_r = st.columns([1.4, 1])

    # ---- PDF Generation ----
    with rep_l:
        st.markdown("##### 📄 Professional PDF Report", unsafe_allow_html=False)
        st.caption("Institutional-grade report with executive summary, collateral register, "
                   "facility LTV breakdown, and override register.")
        report_name = st.text_input(
            "Client / Portfolio Name",
            placeholder="e.g. Ramesh Sharma - Q2 Review",
            key="rep_client_name",
            label_visibility="visible",
        )
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            if not report_name.strip():
                st.error("Please enter a client name.")
            else:
                with st.spinner("Compiling PDF…"):
                    try:
                        pdf_bytes = generate_pdf(
                            report_name.strip(), results,
                            st.session_state.fmv_sources, summary
                        )
                        safe_name = (report_name.strip()
                                     .replace(" ", "_").replace("/", "-").replace("\\", "-"))
                        st.session_state["generated_pdf"]      = pdf_bytes
                        st.session_state["generated_pdf_name"] = (
                            f"LTV_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        )
                        st.toast("✅ PDF generated successfully!", icon="📄")
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

        if "generated_pdf" in st.session_state:
            st.markdown("""
            <div class="notice-strip info" style="margin-top:1rem;">
                <span>✅</span> Your report is ready. Use the download button to save.
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label=f"⬇ Download {st.session_state.get('generated_pdf_name','report.pdf')}",
                data=st.session_state["generated_pdf"],
                file_name=st.session_state["generated_pdf_name"],
                mime="application/pdf",
                type="primary", use_container_width=True,
            )

    # ---- Excel Export ----
    with rep_r:
        st.markdown("##### 📊 Excel Export", unsafe_allow_html=False)
        st.caption("Multi-sheet workbook with Summary, Facilities, and Properties tabs. "
                   "Ideal for further analysis or audit trails.")
        if st.button("Generate Excel Workbook", type="primary", use_container_width=True):
            try:
                excel_bytes = export_portfolio_excel(
                    results, st.session_state.fmv_sources, summary
                )
                st.session_state["generated_excel"] = excel_bytes
                st.session_state["generated_excel_name"] = (
                    f"LTV_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                )
                st.toast("✅ Excel workbook generated!", icon="📊")
                st.rerun()
            except Exception as e:
                st.error(f"Excel export failed: {e}")

        if "generated_excel" in st.session_state:
            st.markdown("""
            <div class="notice-strip info" style="margin-top:1rem;">
                <span>✅</span> Workbook ready. Download below.
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label=f"⬇ Download {st.session_state.get('generated_excel_name','workbook.xlsx')}",
                data=st.session_state["generated_excel"],
                file_name=st.session_state["generated_excel_name"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary", use_container_width=True,
            )

    # ---- Bulk Import ----
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("##### 📥 Bulk Import from Excel", unsafe_allow_html=False)
    st.caption("Upload an Excel file to bulk-import properties. Expected columns: "
               "**Plot** (or Property), **Owner**, **Amount** (FMV).")

    with st.expander("How to format your Excel file", expanded=False):
        sample_df = pd.DataFrame({
            "Plot":     ["Plot 42-B, Sector 7", "Flat 301, Tower B", "Land at Bhaktapur"],
            "Owner":    ["Ramesh Sharma",       "Sita Devi",        "Hari Krishna"],
            "Amount":   [15_000_000,            8_500_000,          4_200_000],
        })
        st.dataframe(sample_df, hide_index=True, use_container_width=True)
        st.caption("Column names are matched case-insensitively. The first matching column wins.")

    upload_col1, upload_col2 = st.columns([3, 1])
    with upload_col1:
        uploaded = st.file_uploader(
            "Choose an Excel file", type=["xlsx", "xls", "csv"],
            key="bulk_upload", label_visibility="collapsed",
        )
    with upload_col2:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        if uploaded and st.button("Import", type="primary", use_container_width=True):
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                else:
                    df = pd.read_excel(uploaded, engine="openpyxl")
                # Normalize columns
                col_map = {}
                for c in df.columns:
                    lc = str(c).lower().strip()
                    if lc in ("plot", "property", "reference", "ref", "property reference"):
                        col_map[c] = "Plot"
                    elif lc in ("owner", "owner name"):
                        col_map[c] = "Owner"
                    elif lc in ("amount", "fmv", "value", "fair market value"):
                        col_map[c] = "Amount"
                df = df.rename(columns=col_map)
                required = {"Plot", "Amount"}
                if not required.issubset(set(df.columns)):
                    st.error(f"Missing required columns. Found: {list(df.columns)}. Need at least: Plot, Amount")
                else:
                    n_added, n_skipped = 0, 0
                    for _, row in df.iterrows():
                        plot = str(row.get("Plot", "")).strip()
                        amt  = float(pd.to_numeric(row.get("Amount"), errors="coerce") or 0)
                        own  = str(row.get("Owner", "") or "").strip() if "Owner" in df.columns else ""
                        if not plot or amt <= 0:
                            n_skipped += 1
                            continue
                        fid = _next_fmv_id()
                        st.session_state.fmv_sources.append({
                            "id": fid, "Plot": plot, "Owner": own, "Amount": amt,
                        })
                        n_added += 1
                    st.toast(f"✅ Imported {n_added} properties ({n_skipped} skipped).", icon="📥")
                    st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")


# ============================================================
# 🏠 EMPTY STATE (no facilities)
# ============================================================
def render_onboarding():
    """Shown when there are no facilities in the portfolio."""
    st.markdown("""
    <style>
        .ob-hero {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #312E81 100%);
            border-radius: 18px;
            padding: 2.5rem 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 20px 50px rgb(15 23 42 / 0.20);
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }
        .ob-hero::before {
            content: ''; position: absolute; top: -50%; left: -30%;
            width: 160%; height: 160%;
            background: radial-gradient(ellipse, rgba(99, 102, 241, 0.25) 0%, transparent 60%);
            pointer-events: none;
        }
        .ob-hero-icon {
            width: 70px; height: 70px; border-radius: 18px;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            display: inline-flex; align-items: center; justify-content: center;
            font-size: 2rem; margin-bottom: 1rem; position: relative; z-index: 1;
        }
        .ob-hero-title { font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.5rem; position: relative; z-index: 1; }
        .ob-hero-sub   { font-size: 0.95rem; color: #CBD5E1; max-width: 580px; margin: 0 auto 1.25rem; line-height: 1.6; position: relative; z-index: 1; }
        .ob-hero-pills { display: flex; justify-content: center; gap: 0.5rem; flex-wrap: wrap; position: relative; z-index: 1; }
        .ob-pill { background: rgba(255, 255, 255, 0.10); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 99px; padding: 0.3rem 0.85rem; font-size: 0.72rem; font-weight: 600; color: #E2E8F0; }
    </style>
    <div class="ob-hero">
        <div class="ob-hero-icon">🏦</div>
        <div class="ob-hero-title">Welcome to LTV Analysis Engine</div>
        <div class="ob-hero-sub">
            Institutional-grade Loan-to-Value analysis with multi-collateral waterfall allocation,
            dedicated assignment, tie-up security, LTV override, surplus/shortfall reporting, and one-click export.
        </div>
        <div class="ob-hero-pills">
            <span class="ob-pill">Multi-Collateral</span>
            <span class="ob-pill">Waterfall Pool</span>
            <span class="ob-pill">Tie-up</span>
            <span class="ob-pill">Override</span>
            <span class="ob-pill">Loan A/C IDs</span>
            <span class="ob-pill">PDF Export</span>
            <span class="ob-pill">Excel Export</span>
            <span class="ob-pill">Bulk Import</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-num">1</div>
            <div class="feature-title">Add Properties</div>
            <div class="feature-desc">Enter each collateral property with owner name and FMV via the sidebar. Or bulk-import from Excel in the Reports tab.</div>
        </div>
        <div class="feature-card">
            <div class="feature-num">2</div>
            <div class="feature-title">Add Loan Facilities</div>
            <div class="feature-desc">Choose facility type, principal, and collateral mode. Use Override for LTV-exempt loans or tie-up for additional security.</div>
        </div>
        <div class="feature-card">
            <div class="feature-num">3</div>
            <div class="feature-title">Analyze Portfolio</div>
            <div class="feature-desc">Real-time LTV calculations, weighted & aggregate LTV, surplus/shortfall, and visual breakdowns across all facilities.</div>
        </div>
        <div class="feature-card">
            <div class="feature-num">4</div>
            <div class="feature-title">Export Reports</div>
            <div class="feature-desc">Generate professional PDF reports for credit committee review, or export multi-sheet Excel workbooks for audit trails.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 🚀 MAIN APP
# ============================================================
def main():
    # Inject component CSS
    st.markdown(COMPONENT_CSS, unsafe_allow_html=True)

    # Sidebar (quick-add workbench)
    render_sidebar()

    # Header bar
    render_header()

    # Empty state
    if not st.session_state.loans:
        # Still show property quick-add warning if needed
        if not st.session_state.fmv_sources and not _all_loans_ltv_exempt():
            st.markdown("""
            <div class="notice-strip">
                <span>ℹ️</span>
                Add at least one property in the sidebar before adding facilities, or enable <b>Override</b> on every facility.
            </div>
            """, unsafe_allow_html=True)
        render_onboarding()
        st.stop()

    # Property warning
    if not st.session_state.fmv_sources and not _all_loans_ltv_exempt():
        st.warning("⚠ Add at least one property/FMV source in the sidebar. "
                   "Properties are only optional when all facilities have Override enabled.")
        st.stop()

    # Calculate results
    results, summary = run_portfolio_ltv(
        st.session_state.loans, st.session_state.fmv_sources
    )

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊  Dashboard",
        "📦  Portfolio",
        "📐  Analysis",
        "📑  Reports",
    ])

    with tab1:
        render_dashboard(results, summary)

    with tab2:
        render_portfolio(results, summary)

    with tab3:
        render_analysis(results, summary)

    with tab4:
        render_reports(results, summary)


if __name__ == "__main__":
    main()
