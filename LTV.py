import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import copy

# ==========================================
# ⚙️ PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="LTV Analysis Engine",
    layout="wide",
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🔐 AUTHENTICATION
# ==========================================
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


def _show_login():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * { box-sizing: border-box; }
        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background: linear-gradient(145deg, #eef2ff 0%, #f5f3ff 50%, #ede9fe 100%) !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Wide layout: give room for columns */
        .block-container {
            max-width: 100% !important;
            padding: 0 1rem !important;
            margin: 0 auto !important;
        }

        /* ── Card = center column's vertical block ── */
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
            max-width: 600px;
            width: 100%;
            margin: max(5vh, 2rem) auto 3rem auto !important;
            background: #ffffff !important;
            border-radius: 22px !important;
            overflow: hidden !important;
            border: 1px solid rgba(99,102,241,0.18) !important;
            box-shadow:
                0 2px 4px rgba(0,0,0,0.04),
                0 8px 32px rgba(99,102,241,0.13),
                0 24px 60px rgba(99,102,241,0.07) !important;
            padding: 2.5rem !important;
        }

        /* ── Full-bleed purple header (negative margins offset the 2.5rem card padding) ── */
        .lp-header {
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 55%, #7c3aed 100%);
            margin: -2.5rem -2.5rem 2rem -2.5rem;
            padding: 2.5rem 2.5rem 2.25rem;
            text-align: center;
            border-radius: 22px 22px 0 0;
            position: relative;
            overflow: hidden;
        }

        .lp-header::before {
            content: '';
            position: absolute;
            top: -40%; left: -30%;
            width: 160%; height: 160%;
            background: radial-gradient(ellipse, rgba(255,255,255,0.1) 0%, transparent 65%);
            pointer-events: none;
        }

        .lp-logo {
            font-size: 3.1rem;
            display: block;
            margin-bottom: 0.75rem;
            position: relative;
            z-index: 1;
        }

        .lp-app-name {
            font-size: 1.55rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.04em;
            margin-bottom: 0.3rem;
            position: relative;
            z-index: 1;
        }

        .lp-app-tagline {
            font-size: 0.71rem;
            color: rgba(255,255,255,0.6);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            position: relative;
            z-index: 1;
            margin-bottom: 1.35rem;
        }

        /* Feature chips in header */
        .lp-chips {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
            justify-content: center;
            position: relative;
            z-index: 1;
        }

        .lp-chip {
            font-size: 0.63rem;
            font-weight: 600;
            color: rgba(255,255,255,0.88);
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.22);
            border-radius: 99px;
            padding: 0.22rem 0.65rem;
            white-space: nowrap;
            letter-spacing: 0.01em;
        }

        /* ── Form copy ── */
        .lp-welcome-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1e1b4b;
            margin-bottom: 0.25rem;
        }

        .lp-welcome-sub {
            font-size: 0.79rem;
            color: #64748b;
            line-height: 1.55;
        }

        /* ── Field labels ── */
        .lp-field-label {
            display: block;
            font-size: 0.72rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.3rem;
            margin-top: 1.05rem;
        }

        /* ── Inputs ── */
        div[data-testid="stTextInput"] label { display: none !important; }
        div[data-testid="stTextInput"] > div { background: transparent !important; }
        div[data-testid="stTextInput"] > div > div {
            background: #f9fafb !important;
            border: 1.5px solid #e5e7eb !important;
            border-radius: 10px !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stTextInput"] > div > div:focus-within {
            border-color: #6366f1 !important;
            background: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.13) !important;
        }
        div[data-testid="stTextInput"] > div > div > input {
            background: transparent !important;
            border: none !important;
            color: #111827 !important;
            font-size: 0.92rem !important;
            font-family: 'Inter', sans-serif !important;
            padding: 0.7rem 1rem !important;
        }
        div[data-testid="stTextInput"] > div > div > input::placeholder {
            color: #9ca3af !important;
        }

        /* ── Sign In button ── */
        div.stButton > button {
            width: 100% !important;
            background: linear-gradient(135deg, #4338ca 0%, #7c3aed 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 0.93rem !important;
            padding: 0.75rem 1.5rem !important;
            margin-top: 1.5rem !important;
            letter-spacing: 0.025em !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 3px 14px rgba(99,102,241,0.38) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 22px rgba(99,102,241,0.52) !important;
            background: linear-gradient(135deg, #3730a3 0%, #6d28d9 100%) !important;
        }
        div.stButton > button:active { transform: translateY(0) !important; }

        /* ── Error ── */
        .lp-error {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 0.7rem 1rem;
            margin-top: 0.8rem;
            font-size: 0.8rem;
            color: #b91c1c;
            font-weight: 500;
            display: flex;
            gap: 0.5rem;
            align-items: flex-start;
            line-height: 1.5;
        }

        /* ── Divider ── */
        .lp-divider {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 1.6rem 0 0.9rem;
        }
        .lp-divider-line { flex: 1; height: 1px; background: #e5e7eb; }
        .lp-divider-text {
            font-size: 0.63rem;
            color: #9ca3af;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            white-space: nowrap;
        }

        /* ── Security row ── */
        .lp-sec-row {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 0;
        }
        .lp-sec-item {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.64rem;
            color: #6b7280;
            font-weight: 500;
            padding: 0 0.6rem;
        }
        .lp-sec-item:not(:last-child) { border-right: 1px solid #e5e7eb; }
        .lp-sec-dot { width: 5px; height: 5px; border-radius: 50%; background: #22c55e; flex-shrink: 0; }

        div[data-testid="stVerticalBlock"] > div { gap: 0.1rem !important; }

        /* Responsive: on narrow screens stack normally */
        @media (max-width: 640px) {
            div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div[data-testid="stVerticalBlock"] {
                max-width: 96vw !important;
                margin: 1rem auto !important;
                padding: 1.5rem !important;
            }
            .lp-header {
                margin: -1.5rem -1.5rem 1.5rem -1.5rem !important;
                padding: 2rem 1.5rem 1.75rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    # Three columns — center column becomes the login card
    _, card_col, _ = st.columns([1, 2.5, 1])

    with card_col:
        # ── Purple header (full-bleed via negative margins)
        st.markdown("""
        <div class="lp-header">
            <span class="lp-logo">🏦</span>
            <div class="lp-app-name">LTV Analysis Engine</div>
            <div class="lp-app-tagline">Loan-to-Value Platform</div>
            <div class="lp-chips">
                <span class="lp-chip">Multi-Collateral</span>
                <span class="lp-chip">Waterfall Pool</span>
                <span class="lp-chip">Tie-up &amp; Override</span>
                <span class="lp-chip">PDF Reports</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Welcome copy
        st.markdown("""
        <div class="lp-welcome-title">Welcome Back</div>
        <div class="lp-welcome-sub">Sign in with your institutional credentials to continue.</div>
        """, unsafe_allow_html=True)

        # ── Username
        st.markdown('<span class="lp-field-label">Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            label="u", placeholder="Enter your username",
            key="_login_u", label_visibility="collapsed",
            autocomplete="username",
        )

        # ── Password
        st.markdown('<span class="lp-field-label">Password</span>', unsafe_allow_html=True)
        password = st.text_input(
            label="p", placeholder="Enter your password",
            type="password", key="_login_p",
            label_visibility="collapsed",
            autocomplete="current-password",
        )

        clicked = st.button("Sign In →", key="_login_btn", use_container_width=True)

        err = st.session_state.get("_login_error", "")
        if err:
            st.markdown(
                f'<div class="lp-error"><span>⚠</span><span>{err}</span></div>',
                unsafe_allow_html=True,
            )

        # ── Footer
        st.markdown("""
        <div class="lp-divider">
            <div class="lp-divider-line"></div>
            <div class="lp-divider-text">Secured Access</div>
            <div class="lp-divider-line"></div>
        </div>
        <div class="lp-sec-row">
            <span class="lp-sec-item"><span class="lp-sec-dot"></span>TLS Secured</span>
            <span class="lp-sec-item"><span class="lp-sec-dot"></span>Session Protected</span>
            <span class="lp-sec-item"><span class="lp-sec-dot"></span>Audit Ready</span>
        </div>
        """, unsafe_allow_html=True)

        if clicked:
            u = str(username).strip()
            p = str(password).strip()
            if not u:
                st.session_state["_login_error"] = "Username is required to continue."
                st.rerun()
            elif not p:
                st.session_state["_login_error"] = "Password is required to continue."
                st.rerun()
            elif _check_credentials(u, p):
                st.session_state["authenticated"] = True
                st.session_state["auth_username"] = u
                st.session_state["_login_error"] = ""
                st.rerun()
            else:
                st.session_state["_login_error"] = (
                    f'Invalid credentials for \"{u}\". '
                    "Please check your username and password and try again."
                )
                st.rerun()


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    _show_login()
    st.stop()


# ==========================================
# 🎨 MAIN APP STYLES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #1a1f36; letter-spacing: -0.01em; }
    .block-container { max-width: 96% !important; padding-top: 1.5rem !important; }
    .main { background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%); }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
        border-radius: 10px !important; border: 1px solid #e2e8f0 !important;
        padding: 0.65rem 0.9rem !important; font-size: 0.95rem !important;
        background: #f8fafc !important; transition: all 0.2s;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stNumberInput"] input:focus {
        border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important; background: white !important;
    }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%); box-shadow: 4px 0 24px rgba(0,0,0,0.18); }
    [data-testid="stSidebar"] * { color: #e0e7ff; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"], [data-testid="stSidebar"] input { background: rgba(255,255,255,0.95) !important; color: #1e1b4b !important; font-weight: 600; }
    div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #7c3aed !important; border-color: #7c3aed !important;
        color: white !important; border-radius: 8px; font-weight: 600; transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover { background-color: #6d28d9 !important; border-color: #6d28d9 !important; transform: translateY(-1px); }
    .metric-card { background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%); padding: 1.25rem 1.5rem; border-radius: 14px; border: 1px solid #ddd6fe; box-shadow: 0 4px 14px rgba(124,58,237,0.08); }
    .metric-label { font-size: 0.75rem; font-weight: 700; color: #7c3aed; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem; }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #1e1b4b; font-family: 'DM Mono', monospace; line-height: 1.1; }
    .metric-sub { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
    .delta-pos { color: #059669; }
    .delta-neg { color: #dc2626; }
    .status-banner { padding: 0.9rem 1.5rem; border-radius: 12px; font-weight: 700; font-size: 1rem; text-align: center; margin: 1.25rem 0; }
    .status-pass { background: #d1fae5; border: 2px solid #059669; color: #065f46; }
    .status-fail { background: #fee2e2; border: 2px solid #dc2626; color: #991b1b; }
    .aggregate-card { background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 1.25rem 1.5rem; border-radius: 14px; border: 1px solid #4338ca; box-shadow: 0 4px 14px rgba(30,27,75,0.18); }
    .aggregate-label { font-size: 0.75rem; font-weight: 700; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem; }
    .aggregate-value { font-size: 1.7rem; font-weight: 700; color: #ffffff; font-family: 'DM Mono', monospace; line-height: 1.1; }
    .aggregate-sub { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; color: #c7d2fe; }
    .ltv-gauge-wrap { margin-top: 0.4rem; height: 7px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }
    .gauge-ok   { height: 100%; border-radius: 99px; background: #059669; }
    .gauge-warn { height: 100%; border-radius: 99px; background: #f59e0b; }
    .gauge-fail { height: 100%; border-radius: 99px; background: #dc2626; }
    .gauge-err  { height: 100%; border-radius: 99px; background: #6b7280; }
    .surplus-pos { background: #d1fae5; color: #065f46; display:inline-block; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:8px; margin-top:0.4rem; }
    .surplus-neg { background: #fee2e2; color: #991b1b; display:inline-block; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:8px; margin-top:0.4rem; }
    .surplus-err { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; display:inline-block; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:8px; margin-top:0.4rem; }
    .surplus-na { background: #f1f5f9; color: #64748b; display:inline-block; font-size:0.72rem; font-weight:700; padding:0.2rem 0.6rem; border-radius:8px; margin-top:0.4rem; }
    .ac-id-badge { display: inline-block; font-size: 0.68rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 6px; background: #ede9fe; color: #4c1d95; font-family: 'DM Mono', monospace; }
    .override-badge { display: inline-block; font-size: 0.65rem; font-weight: 700; padding: 0.12rem 0.45rem; border-radius: 6px; background: #fef9c3; color: #854d0e; border: 1px solid #fde047; font-family: 'DM Mono', monospace; margin-left: 0.3rem; }
    .tieup-badge { display: inline-block; font-size: 0.65rem; font-weight: 700; padding: 0.12rem 0.45rem; border-radius: 6px; background: #fdf4ff; color: #6b21a8; border: 1px solid #e9d5ff; font-family: 'DM Mono', monospace; margin-left: 0.3rem; }
    .landing-wrap { max-width: 980px; margin: 0 auto; padding: 2rem 1rem; }
    .landing-hero { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); border-radius: 22px; padding: 3.25rem 2.75rem; text-align: center; box-shadow: 0 12px 48px rgba(30,27,75,0.35); margin-bottom: 2rem; position: relative; overflow: hidden; }
    .landing-hero-icon { font-size: 3.75rem; margin-bottom: 0.85rem; }
    .landing-hero-title { font-size: 2.4rem; font-weight: 800; color: #ffffff; letter-spacing: -0.04em; margin-bottom: 0.6rem; line-height: 1.15; }
    .landing-hero-sub { font-size: 1.05rem; color: #c7d2fe; max-width: 580px; margin: 0 auto 1.75rem; line-height: 1.65; }
    .landing-badge-row { display: flex; justify-content: center; gap: 0.55rem; flex-wrap: wrap; }
    .landing-badge { background: rgba(255,255,255,0.1); color: #e0e7ff; border: 1px solid rgba(255,255,255,0.18); border-radius: 99px; padding: 0.3rem 0.9rem; font-size: 0.73rem; font-weight: 600; }
    .steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.1rem; margin-bottom: 1.6rem; }
    .step-card { background: #ffffff; border-radius: 16px; border: 1px solid #e8e0fd; padding: 1.5rem 1.25rem; box-shadow: 0 2px 16px rgba(124,58,237,0.07); }
    .step-num { width: 2.1rem; height: 2.1rem; border-radius: 50%; background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; font-weight: 800; font-size: 0.9rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.8rem; }
    .step-title { font-size: 0.97rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.35rem; }
    .step-desc { font-size: 0.82rem; color: #64748b; line-height: 1.55; }
    .landing-cta { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 1.5px solid #86efac; border-radius: 16px; padding: 1.35rem 1.75rem; text-align: center; }
    .landing-cta-title { font-size: 1.05rem; font-weight: 700; color: #14532d; margin-bottom: 0.35rem; }
    .landing-cta-sub { font-size: 0.84rem; color: #166534; line-height: 1.5; }
    @media (max-width: 700px) { .steps-grid { grid-template-columns: 1fr; } .landing-hero-title { font-size: 1.6rem; } }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ⚙️ DEFAULT LTV POLICY
# ==========================================
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",                "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan",                  "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial",       "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "HP Loan (Used)",           "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial-EV",    "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "First Time Home Buyer",    "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "Personal Term Loan (PTL)", "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Education Loan",           "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Professional T/L",         "Max LTV%": None,  "Unsecured": False},
    {"Loan Type": "Professional OD",          "Max LTV%": None,  "Unsecured": False},
    {"Loan Type": "Cash Credit facility",     "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Short Term Facility",      "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Permanent WC Loan",        "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Business Term Loan",       "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Personal OD",              "Max LTV%": 50.0,  "Unsecured": False},
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


def get_policy_dict():
    return {
        p["Loan Type"]: (None if p["Unsecured"] else p["Max LTV%"])
        for p in st.session_state.ltv_policy
    }


def safe_str(text):
    if not isinstance(text, str):
        text = str(text)
    char_map = {
        '\u2014': '-', '\u2013': '-', '\u2012': '-', '\u2011': '-', '\u2010': '-',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u201a': ',', '\u201e': '"',
        '\u00a0': ' ', '\u2009': ' ', '\u202f': ' ',
        '\u200b': '', '\u200c': '', '\u200d': '', '\ufeff': '',
        '\u2022': '*', '\u2023': '*', '\u2043': '-', '\u2026': '...',
        '\u00b7': '.', '\u2027': '.',
        '\u20b9': 'Rs.', '\u20ac': 'EUR', '\u00a3': 'GBP', '\u00a5': 'JPY',
        '\u2265': '>=', '\u2264': '<=', '\u2260': '!=',
        '\u00d7': 'x', '\u00f7': '/', '\u00b1': '+/-', '\u221e': 'inf',
        '\u00bd': '1/2', '\u00bc': '1/4', '\u00be': '3/4',
        '\u00b2': '2', '\u00b3': '3',
        '\u00e9': 'e', '\u00e8': 'e', '\u00ea': 'e', '\u00eb': 'e',
        '\u00e0': 'a', '\u00e2': 'a', '\u00e4': 'a', '\u00e1': 'a',
        '\u00f4': 'o', '\u00f6': 'o', '\u00f3': 'o', '\u00f2': 'o',
        '\u00fb': 'u', '\u00fc': 'u', '\u00fa': 'u', '\u00f9': 'u',
        '\u00ee': 'i', '\u00ef': 'i', '\u00ed': 'i', '\u00ec': 'i',
        '\u00e7': 'c', '\u00f1': 'n',
        '\u00c9': 'E', '\u00c0': 'A', '\u00c2': 'A', '\u00c4': 'A',
        '\u00d4': 'O', '\u00d6': 'O', '\u00db': 'U', '\u00dc': 'U',
        '\u00ce': 'I', '\u00c7': 'C', '\u00d1': 'N',
        '\u2192': '->', '\u2190': '<-', '\u2191': '^', '\u2193': 'v',
        '\u2714': 'OK', '\u2716': 'X', '\u2713': 'OK', '\u2717': 'X',
        '\U0001f512': '', '\U0001f30a': '', '\U0001f517': '',
        '\U0001f4cb': '', '\U0001f3e6': '', '\u26a0': '!',
        '\u2705': 'OK', '\u274c': 'X',
    }
    for ch, rep in char_map.items():
        text = text.replace(ch, rep)
    result = []
    for ch in text:
        try:
            ch.encode('latin-1')
            result.append(ch)
        except (UnicodeEncodeError, UnicodeDecodeError):
            result.append('?')
    return ''.join(result)


# ==========================================
# 🔧 SESSION STATE INIT
# ==========================================
def _next_fmv_id():
    fid = st.session_state.fmv_id_counter
    st.session_state.fmv_id_counter += 1
    return fid


def _generate_loan_account_id(loan_type: str) -> str:
    prefix = LOAN_TYPE_PREFIXES.get(loan_type, "LN")
    if prefix not in st.session_state.loan_type_counters:
        st.session_state.loan_type_counters[prefix] = 0
    st.session_state.loan_type_counters[prefix] += 1
    return f"{prefix}{st.session_state.loan_type_counters[prefix]:03d}"


def _migrate_fmv_sources():
    for src in st.session_state.fmv_sources:
        if 'id' not in src:
            src['id'] = _next_fmv_id()
        if 'Owner' not in src:
            src['Owner'] = ''


def _migrate_loans():
    for loan in st.session_state.loans:
        if 'collateral_mode' not in loan:
            loan['collateral_mode'] = 'pool'
        elif loan['collateral_mode'] == 'both':
            loan['collateral_mode'] = (
                'assigned' if loan.get('assigned_collateral_ids') else 'pool'
            )
        if 'assigned_collateral_ids' not in loan:
            loan['assigned_collateral_ids'] = []
        if '_loan_id' not in loan:
            loan['_loan_id'] = st.session_state.loan_id_counter
            st.session_state.loan_id_counter += 1
        if 'loan_account_id' not in loan:
            loan['loan_account_id'] = _generate_loan_account_id(
                loan.get('Loan Type', 'LN')
            )
        if 'tied_property_ids' not in loan:
            loan['tied_property_ids'] = []
        if 'override_ltv' not in loan:
            loan['override_ltv'] = False


for _k, _v in [
    ('fmv_id_counter', 0),
    ('loan_id_counter', 0),
    ('loan_type_counters', {}),
    ('loans', []),
    ('fmv_sources', []),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

if 'ltv_policy' not in st.session_state:
    st.session_state.ltv_policy = copy.deepcopy(DEFAULT_LTV_POLICY)

_migrate_fmv_sources()
_migrate_loans()


# ==========================================
# 🛠️ HELPERS
# ==========================================
def _get_collateral_names(cids, fmv_sources):
    id_to_plot = {s['id']: s['Plot'] for s in fmv_sources}
    return [id_to_plot[cid] for cid in cids if cid in id_to_plot]


def _get_assigned_in_use():
    return {
        cid
        for loan in st.session_state.loans
        for cid in loan.get('assigned_collateral_ids', [])
        if loan.get('collateral_mode') == 'assigned'
    }


def _get_tied_in_use():
    result = {}
    for loan in st.session_state.loans:
        for cid in loan.get('tied_property_ids', []):
            result.setdefault(cid, []).append(
                loan.get('loan_account_id', loan['Loan Type'])
            )
    return result


def _portfolio_has_ties():
    return any(loan.get('tied_property_ids') for loan in st.session_state.loans)


def _loan_is_ltv_exempt(loan: dict) -> bool:
    policy = get_policy_dict()
    if policy.get(loan.get('Loan Type')) is None:
        return True
    if loan.get('override_ltv', False):
        return True
    if loan.get('tied_property_ids'):
        return True
    return False


def _all_loans_ltv_exempt() -> bool:
    """Returns True if every loan in the portfolio is LTV-exempt."""
    if not st.session_state.loans:
        return False
    for loan in st.session_state.loans:
        if not _loan_is_ltv_exempt(loan):
            return False
    return True


# ==========================================
# 💰 PROFESSIONAL CAPS
# ==========================================
PROFESSIONAL_OD_CAP       = 500_000.0
PROFESSIONAL_TL_CAP       = 1_500_000.0
PROFESSIONAL_COMBINED_CAP = 1_500_000.0


def _check_professional_caps(l_type, l_amt, existing_loans):
    if l_type not in ("Professional OD", "Professional T/L"):
        return True, ""
    existing_od = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional OD")
    existing_tl = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional T/L")
    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)
    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, f"Professional OD total (Rs. {new_od:,.0f}) would exceed cap of Rs. {PROFESSIONAL_OD_CAP:,.0f}."
    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, f"Professional T/L total (Rs. {new_tl:,.0f}) would exceed cap of Rs. {PROFESSIONAL_TL_CAP:,.0f}."
    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, f"Combined Prof OD + T/L (Rs. {(new_od+new_tl):,.0f}) would exceed combined cap of Rs. {PROFESSIONAL_COMBINED_CAP:,.0f}."
    return True, ""


# ==========================================
# 🧮 PORTFOLIO LTV ENGINE
# ==========================================
def run_portfolio_ltv(loans, fmv_sources):
    policy      = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if 'id' in s]
    fmv_id_set  = {s['id'] for s in fmv_sources}

    def is_exempt(loan):
        return _loan_is_ltv_exempt(loan)

    collateral_usage = {s['id']: [] for s in fmv_sources}
    for loan in loans:
        if loan.get('collateral_mode') == 'assigned' and not is_exempt(loan):
            for cid in loan.get('assigned_collateral_ids', []):
                if cid in collateral_usage:
                    collateral_usage[cid].append(loan['_loan_id'])

    assigned_collateral_ids = {cid for cid, users in collateral_usage.items() if users}
    pool_collateral_ids     = fmv_id_set - assigned_collateral_ids
    collateral_fmv_map      = {s['id']: s['Amount'] for s in fmv_sources}

    loan_collateral_shares = {loan['_loan_id']: {} for loan in loans}
    for cid in assigned_collateral_ids:
        user_loan_ids = collateral_usage[cid]
        cid_fmv       = collateral_fmv_map.get(cid, 0.0)
        if len(user_loan_ids) == 1:
            lid = user_loan_ids[0]
            if lid in loan_collateral_shares:
                loan_collateral_shares[lid][cid] = cid_fmv
        else:
            sharing_loans = [l for l in loans if l['_loan_id'] in user_loan_ids]
            total_p       = sum(l['Principal'] for l in sharing_loans)
            for sl in sharing_loans:
                share = (
                    cid_fmv * (sl['Principal'] / total_p)
                    if total_p > 0 else cid_fmv / len(sharing_loans)
                )
                if sl['_loan_id'] in loan_collateral_shares:
                    loan_collateral_shares[sl['_loan_id']][cid] = share

    loan_assigned_fmv = {
        loan['_loan_id']: (
            sum(loan_collateral_shares.get(loan['_loan_id'], {}).values())
            if (loan.get('collateral_mode') == 'assigned' and not is_exempt(loan)) else 0.0
        )
        for loan in loans
    }

    pool_fmv = sum(s['Amount'] for s in fmv_sources if s['id'] in pool_collateral_ids)

    def waterfall_sort_key(loan):
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            return (2, 0)
        return (0 if max_ltv <= 50 else 1, -loan['Principal'])

    pool_participating = [
        l for l in loans
        if not is_exempt(l)
        and policy.get(l['Loan Type']) is not None
        and l.get('collateral_mode', 'pool') == 'pool'
    ]
    pool_sorted    = sorted(pool_participating, key=waterfall_sort_key)
    remaining_pool = pool_fmv
    pool_alloc     = {}
    last_idx       = len(pool_sorted) - 1

    for i, loan in enumerate(pool_sorted):
        lid     = loan['_loan_id']
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            pool_alloc[lid] = 0.0
            continue
        principal   = loan['Principal']
        req_total   = principal / (max_ltv / 100.0)
        allocated   = remaining_pool if i == last_idx else min(req_total, remaining_pool)
        pool_alloc[lid] = allocated
        remaining_pool  = max(0.0, remaining_pool - allocated)

    total_fmv = sum(s['Amount'] for s in fmv_sources)
    results   = []

    for loan in loans:
        lid       = loan['_loan_id']
        lt        = loan['Loan Type']
        principal = loan['Principal']
        mode      = loan.get('collateral_mode', 'pool')
        exempt    = is_exempt(loan)
        max_ltv   = policy.get(lt)

        exempt_reason = None
        if max_ltv is None:
            exempt_reason = "policy"
        elif loan.get('override_ltv', False):
            exempt_reason = "override"
        elif loan.get('tied_property_ids'):
            exempt_reason = "tieup"

        if exempt:
            results.append({
                **loan,
                'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0,
                'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True,
                'Is_Unsecured': True, 'Collateral_Mode': mode,
                'Collateral_Names': [], 'Shared_Collateral_Ids': [],
                'No_FMV_Error': False, 'Exempt_Reason': exempt_reason,
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
            loan.get('assigned_collateral_ids', []), fmv_sources
        )
        shared_cids = [
            cid for cid in loan.get('assigned_collateral_ids', [])
            if len(collateral_usage.get(cid, [])) > 1
        ]
        results.append({
            **loan,
            'Max LTV%': max_ltv, 'Assigned FMV': assigned_fmv_val,
            'Pool FMV': pool_fmv_val, 'Total FMV': total_alloc,
            'LTV%': ltv_pct, 'Pass_Status': passes, 'Is_Unsecured': False,
            'Collateral_Mode': mode, 'Collateral_Names': assigned_coll_names,
            'Shared_Collateral_Ids': shared_cids, 'No_FMV_Error': no_fmv_error,
            'Exempt_Reason': None,
        })

    secured_results         = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure          = sum(r['Principal'] for r in results)
    total_alloc_fmv         = sum(r['Total FMV'] for r in secured_results)
    wtd_ltv = (
        total_secured_principal / total_alloc_fmv * 100.0
        if total_alloc_fmv > 0 else 0.0
    )
    aggregate_ltv = (
        total_secured_principal / total_fmv * 100.0 if total_fmv > 0 else 0.0
    )
    overall_pass = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv,
        'pool_fmv': pool_fmv,
        'remaining_pool': remaining_pool,
        'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv,
        'wtd_ltv': wtd_ltv,
        'aggregate_ltv': aggregate_ltv,
        'overall_pass': overall_pass,
        'collateral_usage': collateral_usage,
        'assigned_collateral_ids': assigned_collateral_ids,
        'pool_collateral_ids': pool_collateral_ids,
    }


# ==========================================
# 📄 PDF ENGINE
# ==========================================

# ── Report palette ──
PDF_BAND          = (67, 56, 202)     # header band / table header fill
PDF_DARK          = (30, 27, 75)      # heading text
PDF_MUTED         = (100, 116, 139)   # secondary text
PDF_LINE          = (226, 232, 240)   # hairlines
PDF_ROW_TINT      = (248, 245, 255)   # zebra row tint
PDF_SECTION_BG    = (237, 233, 254)   # light purple fill (totals etc.)
PDF_WHITE         = (255, 255, 255)
PDF_GREEN_SOLID   = (5, 150, 105)
PDF_RED_SOLID     = (220, 38, 38)
PDF_GREEN_SOFT_BG = (209, 250, 229)
PDF_GREEN_SOFT_FG = (5, 150, 105)
PDF_RED_SOFT_BG   = (254, 226, 226)
PDF_RED_SOFT_FG   = (185, 28, 28)
PDF_AMBER_BG      = (254, 249, 195)
PDF_AMBER_FG      = (133, 77, 14)
PDF_BLUE_BG       = (219, 234, 254)
PDF_BLUE_FG       = (29, 78, 216)
PDF_PURPLE_BG     = (253, 244, 255)
PDF_PURPLE_FG     = (107, 33, 168)
PDF_GREY_BG       = (241, 245, 249)
PDF_GREY_FG       = (100, 116, 139)

PDF_PAGE_BOTTOM_MARGIN = 18  # reserved space for footer


class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(*PDF_BAND)
        self.rect(0, 0, self.w, 24, style='F')
        self.set_xy(self.l_margin, 6)
        self.set_text_color(*PDF_WHITE)
        self.set_font('Arial', 'B', 17)
        self.cell(0, 9, safe_str('LTV ANALYSIS REPORT'), 0, 1, 'L')
        self.set_x(self.l_margin)
        self.set_font('Arial', '', 9)
        self.set_text_color(199, 210, 254)
        self.cell(0, 5, safe_str('Loan-to-Value Assessment'), 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.set_y(30)

    def footer(self):
        content_w = self.w - self.l_margin - self.r_margin
        self.set_y(-15)
        self.set_draw_color(*PDF_LINE)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_y(-12)
        self.set_x(self.l_margin)
        self.set_font('Arial', '', 7.5)
        self.set_text_color(*PDF_MUTED)
        dt = datetime.now().strftime("%B %d, %Y")
        self.cell(content_w / 3, 6, safe_str('LTV Analysis Engine'), 0, 0, 'L')
        self.cell(content_w / 3, 6, safe_str(f'Page {self.page_no()}'), 0, 0, 'C')
        self.cell(content_w / 3, 6, safe_str(dt), 0, 0, 'R')
        self.set_text_color(0, 0, 0)


def _pdf_ensure_space(pdf, needed_h):
    if pdf.get_y() + needed_h > pdf.h - PDF_PAGE_BOTTOM_MARGIN:
        pdf.add_page()


def _pdf_section_title(pdf, text):
    x0 = pdf.l_margin
    w  = pdf.w - pdf.l_margin - pdf.r_margin
    y  = pdf.get_y()
    pdf.set_fill_color(*PDF_BAND)
    pdf.rect(x0, y, w, 9, style='F')
    pdf.set_xy(x0 + 3, y + 1.4)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(*PDF_WHITE)
    pdf.cell(w - 6, 6.2, safe_str(text), 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(y + 9 + 5)


def _pdf_metric_card(pdf, x, y, w, h, label, value, value_rgb=PDF_DARK):
    pdf.set_draw_color(*PDF_LINE)
    pdf.set_fill_color(*PDF_WHITE)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, w, h, style='DF', round_corners=True, corner_radius=2.5)
    pdf.set_xy(x + 4, y + 3.2)
    pdf.set_font('Arial', 'B', 7.3)
    pdf.set_text_color(*PDF_MUTED)
    pdf.cell(w - 8, 4, safe_str(label.upper()), 0, 0, 'L')
    pdf.set_xy(x + 4, y + 9.2)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(*value_rgb)
    pdf.cell(w - 8, 7, safe_str(value), 0, 0, 'L')
    pdf.set_text_color(0, 0, 0)


def _pdf_status_banner(pdf, x, y, w, h, text, bg, fg):
    pdf.set_fill_color(*bg)
    pdf.rect(x, y, w, h, style='F', round_corners=True, corner_radius=3)
    pdf.set_xy(x, y)
    pdf.set_font('Arial', 'B', 13)
    pdf.set_text_color(*fg)
    pdf.cell(w, h, safe_str(text), 0, 0, 'C')
    pdf.set_text_color(0, 0, 0)


def _pdf_pill(pdf, x, y, w, h, text, bg, fg, size=7, bold=True):
    pdf.set_fill_color(*bg)
    pdf.rect(x, y, w, h, style='F', round_corners=True, corner_radius=h / 2)
    pdf.set_xy(x, y)
    pdf.set_font('Arial', 'B' if bold else '', size)
    pdf.set_text_color(*fg)
    pdf.cell(w, h, safe_str(text), 0, 0, 'C')
    pdf.set_text_color(0, 0, 0)


def _pdf_col_x(x0, widths, idx):
    return x0 + sum(widths[:idx])


def _pdf_table(pdf, headers, col_widths, rows, render_row, row_h=7.4, header_h=8.2, header_font=8.3):
    x0        = pdf.l_margin
    content_w = sum(col_widths)

    def draw_header():
        pdf.set_x(x0)
        pdf.set_fill_color(*PDF_BAND)
        pdf.set_text_color(*PDF_WHITE)
        pdf.set_font('Arial', 'B', header_font)
        for h, w in zip(headers, col_widths):
            pdf.cell(w, header_h, safe_str(h), 0, 0, 'C', fill=True)
        pdf.ln(header_h)
        pdf.set_text_color(0, 0, 0)

    if pdf.get_y() + header_h + row_h > pdf.h - PDF_PAGE_BOTTOM_MARGIN:
        pdf.add_page()
    draw_header()
    for idx, row in enumerate(rows):
        if pdf.get_y() + row_h > pdf.h - PDF_PAGE_BOTTOM_MARGIN:
            pdf.add_page()
            draw_header()
        y    = pdf.get_y()
        fill = PDF_ROW_TINT if idx % 2 == 0 else PDF_WHITE
        pdf.set_fill_color(*fill)
        pdf.rect(x0, y, content_w, row_h, style='F')
        render_row(pdf, row, x0, y, col_widths, row_h)
        pdf.set_y(y + row_h)
    pdf.set_draw_color(*PDF_LINE)
    pdf.set_line_width(0.25)
    pdf.line(x0, pdf.get_y(), x0 + content_w, pdf.get_y())


def generate_pdf(client_name, results, fmv_sources, summary):
    pdf = PDFReport(orientation='L', unit='mm', format='A4')
    pdf.set_margins(12, 12, 12)
    pdf.set_auto_page_break(False)
    pdf.add_page()

    total_fmv       = summary['total_fmv']
    total_exposure  = summary['total_exposure']
    aggregate_ltv   = summary['aggregate_ltv']
    overall_pass    = summary['overall_pass']
    total_secured_p = summary['total_secured_principal']
    has_tied_pdf    = any(r.get('tied_property_ids') for r in results)
    content_w       = pdf.w - pdf.l_margin - pdf.r_margin

    # ── Executive Summary ──
    _pdf_section_title(pdf, "EXECUTIVE SUMMARY")

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Arial", "", 9.5)
    pdf.cell(40, 6, "Client Name:", 0, 0)
    pdf.set_font("Arial", "B", 9.5)
    pdf.cell(0, 6, safe_str(client_name), 0, 1)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Arial", "", 9.5)
    pdf.cell(40, 6, "Analysis Date:", 0, 0)
    pdf.set_font("Arial", "B", 9.5)
    pdf.cell(0, 6, safe_str(datetime.now().strftime("%B %d, %Y")), 0, 1)
    pdf.ln(3)

    card_y    = pdf.get_y()
    gap       = 5
    card_w    = (content_w - 3 * gap) / 4
    card_h    = 22
    agg_color = PDF_GREEN_SOFT_FG if overall_pass else PDF_RED_SOFT_FG
    _pdf_metric_card(pdf, pdf.l_margin + (card_w + gap) * 0, card_y, card_w, card_h,
                      "Total Secured Exposure", f"Rs. {total_secured_p:,.0f}")
    _pdf_metric_card(pdf, pdf.l_margin + (card_w + gap) * 1, card_y, card_w, card_h,
                      "Total Loan Exposure", f"Rs. {total_exposure:,.0f}")
    _pdf_metric_card(pdf, pdf.l_margin + (card_w + gap) * 2, card_y, card_w, card_h,
                      "Total Collateral FMV", f"Rs. {total_fmv:,.0f}")
    _pdf_metric_card(pdf, pdf.l_margin + (card_w + gap) * 3, card_y, card_w, card_h,
                      "Aggregate LTV%", f"{aggregate_ltv:.2f}%", value_rgb=agg_color)
    pdf.set_y(card_y + card_h + 6)

    if overall_pass:
        banner_text = "PORTFOLIO APPROVED  -  All Facilities Within LTV Limits"
        banner_bg, banner_fg = PDF_GREEN_SOFT_BG, PDF_GREEN_SOFT_FG
    else:
        banner_text = "PORTFOLIO DECLINED  -  One or More Facilities Exceed Maximum LTV"
        banner_bg, banner_fg = PDF_RED_SOFT_BG, PDF_RED_SOFT_FG
    _pdf_status_banner(pdf, pdf.l_margin, pdf.get_y(), content_w, 12, banner_text, banner_bg, banner_fg)
    pdf.set_y(pdf.get_y() + 12 + 8)

    # ── Collateral / FMV Sources ──
    _pdf_ensure_space(pdf, 9 + 5 + 8.2 + 7.4)
    _pdf_section_title(pdf, "COLLATERAL / FAIR MARKET VALUE SOURCES")

    tied_in_use = {}
    for loan in st.session_state.loans:
        for cid in loan.get('tied_property_ids', []):
            tied_in_use.setdefault(cid, []).append(
                loan.get('loan_account_id', loan.get('Loan Type', ''))
            )
    assigned_ids = summary['assigned_collateral_ids']

    if has_tied_pdf:
        fmv_headers = ["Property Reference", "Fair Market Value (Rs.)", "Collateral Type", "Owner", "Tied To A/C"]
        fmv_widths  = [78, 42, 30, 65, 58]
    else:
        fmv_headers = ["Property Reference", "Fair Market Value (Rs.)", "Collateral Type", "Owner"]
        fmv_widths  = [95, 45, 35, 98]

    def render_fmv_row(pdf, row, x0, y, widths, h):
        pdf.set_xy(x0 + 3, y)
        pdf.set_font("Arial", "", 8.4)
        pdf.cell(widths[0] - 3, h, safe_str(row['plot'][:42]), 0, 0, 'L')
        pdf.set_xy(_pdf_col_x(x0, widths, 1), y)
        pdf.set_font("Arial", "B", 8.4)
        pdf.cell(widths[1] - 3, h, f"Rs. {row['amount']:,.0f}", 0, 0, 'R')
        cw, ch = 28, 5.4
        cx = _pdf_col_x(x0, widths, 2) + (widths[2] - cw) / 2
        cy = y + (h - ch) / 2
        if row['ctype'] == 'Assigned':
            _pdf_pill(pdf, cx, cy, cw, ch, "ASSIGNED", PDF_AMBER_BG, PDF_AMBER_FG, 6.4)
        else:
            _pdf_pill(pdf, cx, cy, cw, ch, "POOL", PDF_BLUE_BG, PDF_BLUE_FG, 6.4)
        pdf.set_xy(_pdf_col_x(x0, widths, 3) + 2, y)
        pdf.set_font("Arial", "", 8.4)
        pdf.cell(widths[3] - 2, h, safe_str(row['owner'][:36]), 0, 0, 'L')
        if len(widths) > 4:
            pdf.set_xy(_pdf_col_x(x0, widths, 4) + 2, y)
            pdf.set_font("Arial", "", 7.8)
            pdf.set_text_color(*PDF_MUTED)
            pdf.cell(widths[4] - 2, h, safe_str(row['tied'][:30]), 0, 0, 'L')
            pdf.set_text_color(0, 0, 0)

    fmv_rows = []
    for i, src in enumerate(fmv_sources):
        fid = src.get('id', i)
        tied_list = tied_in_use.get(fid, [])
        fmv_rows.append({
            "plot":   src.get('Plot', ''),
            "amount": src.get('Amount', 0.0),
            "ctype":  "Assigned" if fid in assigned_ids else "Pool",
            "owner":  src.get('Owner', '') or 'N/A',
            "tied":   ", ".join(tied_list) if tied_list else "N/A",
        })

    _pdf_table(pdf, fmv_headers, fmv_widths, fmv_rows, render_fmv_row)

    y = pdf.get_y()
    pdf.set_fill_color(*PDF_SECTION_BG)
    pdf.rect(pdf.l_margin, y, content_w, 8, style='F')
    pdf.set_xy(pdf.l_margin + 3, y)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(*PDF_DARK)
    pdf.cell(fmv_widths[0] - 3, 8, "TOTAL", 0, 0, 'L')
    pdf.set_xy(_pdf_col_x(pdf.l_margin, fmv_widths, 1), y)
    pdf.cell(fmv_widths[1] - 3, 8, f"Rs. {total_fmv:,.0f}", 0, 0, 'R')
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(y + 8 + 8)

    # ── Facility LTV Breakdown ──
    _pdf_ensure_space(pdf, 9 + 5 + 8.2 + 7.4)
    _pdf_section_title(pdf, "FACILITY LTV BREAKDOWN")

    fac_headers = ["A/C No.", "Facility Type", "Principal (Rs.)", "Assigned FMV (Rs.)", "Pool FMV (Rs.)",
                   "Total FMV (Rs.)", "LTV %", "Max LTV %", "Surplus / (Shortfall)", "Status"]
    fac_widths  = [18, 44, 26, 27, 27, 27, 23, 19, 33, 29]

    def display_sort(r):
        m = r.get('Max LTV%')
        if m is None:
            return (2, 0)
        return (0 if m <= 50 else 1, -(r.get('Principal', 0)))

    EXEMPT_BADGE = {
        "override": ("OVERRIDE",  PDF_AMBER_BG,  PDF_AMBER_FG),
        "tieup":    ("TIE-UP",    PDF_PURPLE_BG, PDF_PURPLE_FG),
        "policy":   ("UNSECURED", PDF_GREY_BG,   PDF_GREY_FG),
    }

    fac_rows = []
    for row in sorted(results, key=display_sort):
        is_unsec      = row.get('Is_Unsecured', False)
        no_fmv_err    = row.get('No_FMV_Error', False)
        max_ltv       = row.get('Max LTV%')
        ltv_val       = row.get('LTV%')
        exempt_reason = row.get('Exempt_Reason')

        is_badge = False
        badge_bg = badge_fg = ltv_text = None
        ltv_color = PDF_GREEN_SOFT_FG

        if is_unsec:
            is_badge = True
            ltv_text, badge_bg, badge_fg = EXEMPT_BADGE.get(exempt_reason, ("EXEMPT", PDF_GREY_BG, PDF_GREY_FG))
        elif no_fmv_err:
            ltv_text  = "NO FMV"
            ltv_color = PDF_RED_SOFT_FG
        elif ltv_val is None:
            ltv_text  = "N/A"
            ltv_color = PDF_MUTED
        else:
            ltv_text  = f"{ltv_val:.2f}%"
            ltv_color = PDF_GREEN_SOFT_FG if row['Pass_Status'] else PDF_RED_SOFT_FG

        max_disp      = "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%"
        assigned_disp = "N/A" if is_unsec else f"{row['Assigned FMV']:,.0f}"
        pool_disp     = "N/A" if is_unsec else f"{row['Pool FMV']:,.0f}"
        total_disp    = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"

        if is_unsec or max_ltv is None:
            surplus_disp, surplus_color = "N/A", PDF_MUTED
        elif no_fmv_err:
            surplus_disp, surplus_color = "No FMV", PDF_RED_SOFT_FG
        else:
            req_fmv = row['Principal'] / (max_ltv / 100.0)
            sv      = row.get('Total FMV', 0.0) - req_fmv
            surplus_disp  = f"+{sv:,.0f}" if sv >= 0 else f"({abs(sv):,.0f})"
            surplus_color = PDF_GREEN_SOFT_FG if sv >= 0 else PDF_RED_SOFT_FG

        status    = "PASS" if row['Pass_Status'] else "FAIL"
        status_bg = PDF_GREEN_SOLID if row['Pass_Status'] else PDF_RED_SOLID

        fac_rows.append({
            "ac_id": row.get('loan_account_id', 'N/A'), "facility": row['Loan Type'],
            "principal": row['Principal'], "assigned": assigned_disp, "pool": pool_disp,
            "total": total_disp, "is_badge": is_badge, "ltv_text": ltv_text,
            "ltv_color": ltv_color, "badge_bg": badge_bg, "badge_fg": badge_fg,
            "max": max_disp, "surplus": surplus_disp, "surplus_color": surplus_color,
            "status": status, "status_bg": status_bg,
        })

    def render_fac_row(pdf, row, x0, y, widths, h):
        pdf.set_xy(_pdf_col_x(x0, widths, 0), y)
        pdf.set_font('Arial', 'B', 7.6)
        pdf.cell(widths[0], h, safe_str(row['ac_id']), 0, 0, 'C')
        pdf.set_xy(_pdf_col_x(x0, widths, 1) + 2, y)
        pdf.set_font('Arial', '', 7.6)
        pdf.cell(widths[1] - 2, h, safe_str(row['facility'][:28]), 0, 0, 'L')
        pdf.set_xy(_pdf_col_x(x0, widths, 2), y)
        pdf.cell(widths[2] - 2, h, f"{row['principal']:,.0f}", 0, 0, 'R')
        pdf.set_xy(_pdf_col_x(x0, widths, 3), y)
        pdf.cell(widths[3] - 2, h, safe_str(row['assigned']), 0, 0, 'R')
        pdf.set_xy(_pdf_col_x(x0, widths, 4), y)
        pdf.cell(widths[4] - 2, h, safe_str(row['pool']), 0, 0, 'R')
        pdf.set_xy(_pdf_col_x(x0, widths, 5), y)
        pdf.set_font('Arial', 'B', 7.6)
        pdf.cell(widths[5] - 2, h, safe_str(row['total']), 0, 0, 'R')
        if row['is_badge']:
            bw, bh = widths[6] - 6, 5.2
            bx = _pdf_col_x(x0, widths, 6) + (widths[6] - bw) / 2
            by = y + (h - bh) / 2
            _pdf_pill(pdf, bx, by, bw, bh, row['ltv_text'], row['badge_bg'], row['badge_fg'], 6.2)
        else:
            pdf.set_xy(_pdf_col_x(x0, widths, 6), y)
            pdf.set_font('Arial', 'B', 7.8)
            pdf.set_text_color(*row['ltv_color'])
            pdf.cell(widths[6], h, safe_str(row['ltv_text']), 0, 0, 'C')
            pdf.set_text_color(0, 0, 0)
        pdf.set_xy(_pdf_col_x(x0, widths, 7), y)
        pdf.set_font('Arial', '', 7.6)
        pdf.cell(widths[7], h, safe_str(row['max']), 0, 0, 'C')
        pdf.set_xy(_pdf_col_x(x0, widths, 8), y)
        pdf.set_font('Arial', 'B', 7.6)
        pdf.set_text_color(*row['surplus_color'])
        pdf.cell(widths[8] - 2, h, safe_str(row['surplus']), 0, 0, 'R')
        pdf.set_text_color(0, 0, 0)
        bw, bh = 21, 5.6
        bx = _pdf_col_x(x0, widths, 9) + (widths[9] - bw) / 2
        by = y + (h - bh) / 2
        _pdf_pill(pdf, bx, by, bw, bh, row['status'], row['status_bg'], PDF_WHITE, 7.2)

    _pdf_table(pdf, fac_headers, fac_widths, fac_rows, render_fac_row)

    y = pdf.get_y()
    pdf.set_fill_color(*PDF_SECTION_BG)
    pdf.rect(pdf.l_margin, y, content_w, 8, style='F')
    pdf.set_xy(pdf.l_margin + 3, y)
    pdf.set_font("Arial", "B", 8.5)
    pdf.set_text_color(*PDF_DARK)
    pdf.cell(fac_widths[0] + fac_widths[1] - 3, 8, "AGGREGATE (ALL FACILITIES)", 0, 0, 'L')
    pdf.set_xy(_pdf_col_x(pdf.l_margin, fac_widths, 2), y)
    pdf.cell(fac_widths[2] - 2, 8, f"{total_exposure:,.0f}", 0, 0, 'R')
    pdf.set_xy(_pdf_col_x(pdf.l_margin, fac_widths, 5), y)
    pdf.cell(fac_widths[5] - 2, 8, f"{total_fmv:,.0f}", 0, 0, 'R')
    pdf.set_xy(_pdf_col_x(pdf.l_margin, fac_widths, 6), y)
    pdf.cell(fac_widths[6], 8, f"{aggregate_ltv:.2f}%", 0, 0, 'C')
    agg_status    = "PASS" if overall_pass else "FAIL"
    agg_status_bg = PDF_GREEN_SOLID if overall_pass else PDF_RED_SOLID
    bw, bh = 21, 5.6
    bx = _pdf_col_x(pdf.l_margin, fac_widths, 9) + (fac_widths[9] - bw) / 2
    by = y + (8 - bh) / 2
    _pdf_pill(pdf, bx, by, bw, bh, agg_status, agg_status_bg, PDF_WHITE, 7.2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(y + 8 + 8)

    # ── Override / Tied Register ──
    overridden_loans = [r for r in results if r.get('override_ltv') or r.get('tied_property_ids')]
    if overridden_loans:
        _pdf_ensure_space(pdf, 9 + 5 + 8.2 + 7.4)
        _pdf_section_title(pdf, "LTV OVERRIDE & TIED PROPERTIES REGISTER")

        fmv_id_map_pdf = {s['id']: s for s in fmv_sources}
        reg_headers = ["A/C No.", "Facility Type", "Principal (Rs.)", "Exempt Type", "Tied Properties", "Tied FMV (Rs.)"]
        reg_widths  = [20, 42, 30, 38, 98, 45]

        REG_BADGE = {
            "override": ("MANUAL OVERRIDE",  PDF_AMBER_BG,  PDF_AMBER_FG),
            "tieup":    ("TIE-UP PROPERTIES", PDF_PURPLE_BG, PDF_PURPLE_FG),
            "policy":   ("POLICY EXEMPT",    PDF_GREY_BG,   PDF_GREY_FG),
        }

        reg_rows = []
        for row in overridden_loans:
            exempt_reason = row.get('Exempt_Reason', '')
            badge_text, badge_bg, badge_fg = REG_BADGE.get(exempt_reason, ("EXEMPT", PDF_GREY_BG, PDF_GREY_FG))
            tied_names, tied_fmv_total = [], 0.0
            for cid in row.get('tied_property_ids', []):
                src = fmv_id_map_pdf.get(cid)
                if src:
                    tied_names.append(src.get('Plot', ''))
                    tied_fmv_total += src.get('Amount', 0.0)
            reg_rows.append({
                "ac_id": row.get('loan_account_id', 'N/A'), "facility": row['Loan Type'],
                "principal": row['Principal'], "badge_text": badge_text,
                "badge_bg": badge_bg, "badge_fg": badge_fg,
                "tied": ", ".join(tied_names) if tied_names else "-",
                "tied_fmv": f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "N/A",
            })

        def render_reg_row(pdf, row, x0, y, widths, h):
            pdf.set_xy(_pdf_col_x(x0, widths, 0), y)
            pdf.set_font('Arial', 'B', 7.8)
            pdf.cell(widths[0], h, safe_str(row['ac_id']), 0, 0, 'C')
            pdf.set_xy(_pdf_col_x(x0, widths, 1) + 2, y)
            pdf.set_font('Arial', '', 7.8)
            pdf.cell(widths[1] - 2, h, safe_str(row['facility'][:26]), 0, 0, 'L')
            pdf.set_xy(_pdf_col_x(x0, widths, 2), y)
            pdf.cell(widths[2] - 2, h, f"Rs. {row['principal']:,.0f}", 0, 0, 'R')
            bw, bh = 38, 5.4
            bx = _pdf_col_x(x0, widths, 3) + (widths[3] - bw) / 2
            by = y + (h - bh) / 2
            _pdf_pill(pdf, bx, by, bw, bh, row['badge_text'], row['badge_bg'], row['badge_fg'], 6.2)
            pdf.set_xy(_pdf_col_x(x0, widths, 4) + 2, y)
            pdf.set_font('Arial', '', 7.8)
            pdf.cell(widths[4] - 2, h, safe_str(row['tied'][:54]), 0, 0, 'L')
            pdf.set_xy(_pdf_col_x(x0, widths, 5), y)
            pdf.set_font('Arial', 'B', 7.8)
            pdf.cell(widths[5] - 2, h, safe_str(row['tied_fmv']), 0, 0, 'R')

        _pdf_table(pdf, reg_headers, reg_widths, reg_rows, render_reg_row)

        pdf.set_y(pdf.get_y() + 4)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Arial", "", 7.5)
        pdf.set_text_color(*PDF_MUTED)
        pdf.multi_cell(content_w, 4, safe_str(
            "Overridden and tie-up facilities are excluded from LTV calculation and require credit-authority "
            "sign-off. Tied properties serve only as additional or secondary security."
        ))
        pdf.set_text_color(0, 0, 0)

    pdf_data = pdf.output(dest='S')
    if isinstance(pdf_data, str):
        return pdf_data.encode('latin-1')
    return bytes(pdf_data)


# ==========================================
# 📐 SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## LTV Engine")
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.1); border-radius:8px; padding:0.4rem 0.85rem; "
        f"font-size:0.78rem; color:#c7d2fe; margin-bottom:0.25rem;'>"
        f"Signed in as <b>{st.session_state['auth_username']}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", type="primary"):
        st.session_state["authenticated"] = False
        st.session_state["auth_username"] = ""
        st.session_state["_login_error"]  = ""
        st.rerun()

    st.markdown("---")
    st.markdown("### Step 1 — Add Properties")
    sb_plot  = st.text_input("Property Reference", placeholder="e.g. Plot No. 42-B, Sector 7", key="sb_plot")
    sb_owner = st.text_input("Owner Name", placeholder="e.g. Ramesh Kumar Sharma", key="sb_owner")
    sb_fmv   = st.number_input("Fair Market Value (Rs.)", min_value=0.0, step=50000.0, key="sb_fmv_amt")

    if st.button("Add Property", type="primary"):
        if sb_fmv <= 0:
            st.error("FMV must be > 0")
        elif not sb_plot.strip():
            st.error("Enter a property reference")
        else:
            fid = _next_fmv_id()
            st.session_state.fmv_sources.append({
                "id": fid, "Plot": sb_plot.strip(),
                "Owner": sb_owner.strip(), "Amount": sb_fmv,
            })
            st.success(f"Added: {sb_plot.strip()}")
            st.rerun()

    if st.session_state.fmv_sources:
        assigned_in_use = _get_assigned_in_use()
        tied_in_use_map = _get_tied_in_use()
        total_fmv_all   = sum(s['Amount'] for s in st.session_state.fmv_sources)
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.08); border-radius:8px; padding:0.5rem 0.85rem; "
            f"margin:0.4rem 0; font-size:0.82rem;'>"
            f"Total FMV: <b>Rs. {total_fmv_all:,.0f}</b> &nbsp;·&nbsp; "
            f"{len(st.session_state.fmv_sources)} properties</div>",
            unsafe_allow_html=True
        )
        for src in st.session_state.fmv_sources:
            src_id  = src.get('id', '?')
            is_used = src_id in assigned_in_use
            is_tied = src_id in tied_in_use_map
            tag     = '[A]' if is_used else ('[T]' if is_tied else '[P]')
            col_a, col_b = st.columns([5, 1])
            with col_a:
                owner_txt  = src.get('Owner', '') or ''
                owner_line = (
                    f"<br>&nbsp;&nbsp;<span style='color:#a5b4fc;'>{owner_txt}</span>"
                    if owner_txt else ""
                )
                tied_note = ""
                if is_tied:
                    tied_note = (
                        f"<br>&nbsp;&nbsp;<span style='color:#fcd34d;'>"
                        f"Tied: {', '.join(tied_in_use_map[src_id])}</span>"
                    )
                st.markdown(
                    f"<div style='font-size:0.78rem; color:#c7d2fe; padding:0.2rem 0;'>"
                    f"{tag} <b>{src.get('Plot','')}</b>{owner_line}"
                    f"<br>&nbsp;&nbsp;Rs. {src.get('Amount',0):,.0f}{tied_note}</div>",
                    unsafe_allow_html=True
                )
            with col_b:
                if st.button("X", key=f"del_fmv_{src_id}"):
                    st.session_state.fmv_sources = [
                        s for s in st.session_state.fmv_sources if s.get('id') != src_id
                    ]
                    for loan in st.session_state.loans:
                        for field in ('assigned_collateral_ids', 'tied_property_ids'):
                            lst = loan.get(field, [])
                            if src_id in lst:
                                lst.remove(src_id)
                    st.rerun()

    st.markdown("---")
    st.markdown("### Step 2 — Add Loan Facility")
    policy_dict    = get_policy_dict()
    loan_type_list = list(policy_dict.keys())

    if loan_type_list:
        l_type      = st.selectbox("Facility Type", loan_type_list, key="sb_loan_type")
        l_amt       = st.number_input("Principal Amount (Rs.)", step=10000.0, min_value=0.0, key="sb_loan_principal")
        max_ltv_sel = policy_dict.get(l_type)

        selected_colls = []
        coll_mode      = "pool"
        tie_up_colls   = []
        override_ltv   = False

        if max_ltv_sel is not None:
            override_ltv = st.checkbox(
                "Override collateral requirement (no LTV required)",
                value=False,
                key="sb_override_ltv",
                help=(
                    "Mark this facility as LTV-exempt. No collateral properties needed. "
                    "Must be sanctioned by credit authority."
                )
            )

            if not override_ltv:
                use_dedicated = st.checkbox(
                    "Assign dedicated collateral?", value=False, key="sb_use_dedicated",
                    help="Link specific properties exclusively to this loan."
                )
                coll_mode = "assigned" if use_dedicated else "pool"
                if use_dedicated:
                    if st.session_state.fmv_sources:
                        already_assigned = _get_assigned_in_use()
                        coll_options = {}
                        for s in st.session_state.fmv_sources:
                            sid   = s.get('id')
                            base  = f"{s.get('Plot','?')} - Rs.{s.get('Amount',0):,.0f}"
                            label = f"[In use] {base}" if sid in already_assigned else base
                            coll_options[label] = sid
                        sel_labels     = st.multiselect("Select Collateral(s)", options=list(coll_options.keys()), key="sb_sel_colls")
                        selected_colls = [coll_options[lbl] for lbl in sel_labels]
                        overlap        = [c for c in selected_colls if c in already_assigned]
                        if overlap:
                            st.warning("Selected property already assigned — FMV will be split proportionally.")
                    else:
                        st.warning("Add properties first (Step 1) to use dedicated mode.")
            else:
                st.info("LTV Override enabled — no collateral properties required.")
        else:
            st.info("Unsecured facility — no collateral required.")

        if not override_ltv:
            use_tie_up = st.checkbox(
                "Tie up Property (additional security)?", value=False, key="sb_use_tie_up",
                help="Selecting tie-up properties makes this facility LTV-exempt."
            )
            if use_tie_up:
                if st.session_state.fmv_sources:
                    tie_options = {
                        f"{s.get('Plot','?')} - Rs.{s.get('Amount',0):,.0f}": s.get('id')
                        for s in st.session_state.fmv_sources
                    }
                    tie_sel      = st.multiselect("Select properties to tie up", options=list(tie_options.keys()), key="sb_tie_up_props")
                    tie_up_colls = [tie_options[lbl] for lbl in tie_sel]
                    if tie_up_colls:
                        st.warning(f"{len(tie_up_colls)} property/ies tied — facility will be LTV-exempt.")
                else:
                    st.warning("Add properties first (Step 1) to use tie-up.")
        else:
            tie_up_colls = []

        if st.button("Add to Portfolio", type="primary"):
            if l_amt <= 0:
                st.error("Principal must be > 0")
            elif coll_mode == "assigned" and not selected_colls and not override_ltv:
                st.error("Select at least one property for dedicated mode, or enable Override.")
            else:
                cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
                if not cap_ok:
                    st.error(f"Cap exceeded: {cap_msg}")
                else:
                    ac_id = _generate_loan_account_id(l_type)
                    lid   = st.session_state.loan_id_counter
                    st.session_state.loan_id_counter += 1
                    st.session_state.loans.append({
                        "Loan Type":               l_type,
                        "Principal":               l_amt,
                        "_loan_id":                lid,
                        "loan_account_id":         ac_id,
                        "collateral_mode":         coll_mode,
                        "assigned_collateral_ids": selected_colls,
                        "tied_property_ids":       tie_up_colls,
                        "override_ltv":            override_ltv,
                    })
                    flags = []
                    if override_ltv:
                        flags.append("Override")
                    elif coll_mode == "assigned":
                        flags.append("Dedicated")
                    else:
                        flags.append("Pool")
                    if tie_up_colls:
                        flags.append(f"{len(tie_up_colls)} tied [LTV-Exempt]")
                    st.success(f"[{ac_id}] {l_type} ({' + '.join(flags)})")
                    st.rerun()

    if st.session_state.loans:
        st.markdown("---")
        st.markdown("**Portfolio**")
        for loan in st.session_state.loans:
            mode_lbl = {"pool": "[P]", "assigned": "[A]"}.get(loan.get('collateral_mode', 'pool'), "[P]")
            tie_note = " [T]" if loan.get('tied_property_ids') else ""
            ovr_note = " [Ovr]" if loan.get('override_ltv') else ""
            ac_id    = loan.get('loan_account_id', '?')
            st.markdown(
                f"<div style='font-size:0.76rem; color:#c7d2fe; padding:0.12rem 0;'>"
                f"{mode_lbl} <b style='color:#a5b4fc; font-family:monospace;'>[{ac_id}]</b>"
                f"{tie_note}{ovr_note} "
                f"{loan['Loan Type']} - Rs. {loan['Principal']:,.0f}</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    if st.button("Reset Everything", type="primary"):
        for k in ['loans', 'fmv_sources', 'ltv_policy', 'loan_id_counter',
                  'fmv_id_counter', 'loan_type_counters', 'generated_pdf', 'generated_pdf_name']:
            if k in ['loans', 'fmv_sources']:
                st.session_state[k] = []
            elif k in ['loan_id_counter', 'fmv_id_counter']:
                st.session_state[k] = 0
            elif k == 'loan_type_counters':
                st.session_state[k] = {}
            elif k == 'ltv_policy':
                st.session_state[k] = copy.deepcopy(DEFAULT_LTV_POLICY)
            else:
                st.session_state.pop(k, None)
        st.rerun()


# ==========================================
# 🖥️ MAIN AREA
# ==========================================
st.title("LTV Analysis Engine")
st.markdown(
    "Multi-collateral LTV — assign dedicated collateral, draw from the shared waterfall pool, "
    "tie up additional properties (LTV-exempt), or override collateral requirements per facility."
)

if not st.session_state.loans:
    st.markdown("""
    <div class="landing-wrap">
      <div class="landing-hero">
        <div class="landing-hero-icon">🏦</div>
        <div class="landing-hero-title">LTV Analysis Engine</div>
        <div class="landing-hero-sub">
          Institutional-grade Loan-to-Value analysis with multi-collateral waterfall allocation,
          dedicated assignment, tie-up security, LTV override, surplus/shortfall reporting, and one-click PDF export.
        </div>
        <div class="landing-badge-row">
          <span class="landing-badge">Multi-Collateral</span>
          <span class="landing-badge">Waterfall Pool</span>
          <span class="landing-badge">Dedicated Assignment</span>
          <span class="landing-badge">Tie-up = LTV Exempt</span>
          <span class="landing-badge">Override Flag</span>
          <span class="landing-badge">Loan A/C IDs</span>
          <span class="landing-badge">PDF Export</span>
        </div>
      </div>
      <div class="steps-grid">
        <div class="step-card">
          <div class="step-num">1</div>
          <div class="step-title">Add Properties</div>
          <div class="step-desc">Enter each collateral property with owner name and FMV. Optional if all loans use Override.</div>
        </div>
        <div class="step-card">
          <div class="step-num">2</div>
          <div class="step-title">Add Loan Facilities</div>
          <div class="step-desc">Select facility type, principal, collateral mode (pool/dedicated/override), and optionally tie up additional properties.</div>
        </div>
        <div class="step-card">
          <div class="step-num">3</div>
          <div class="step-title">Analyse &amp; Export</div>
          <div class="step-desc">Review per-facility LTV%, surplus or shortfall, aggregate LTV, override register, and download a professional PDF.</div>
        </div>
      </div>
      <div class="landing-cta">
        <div class="landing-cta-title">Ready to get started?</div>
        <div class="landing-cta-sub">Add properties in <b>Step 1</b> (or skip if using Override), then add a loan in <b>Step 2</b>.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.fmv_sources:
    if not _all_loans_ltv_exempt():
        st.warning(
            "Add at least one property/FMV source in the sidebar (Step 1). "
            "Properties are only optional when all facilities have LTV Override enabled."
        )
        st.stop()

results, summary = run_portfolio_ltv(
    st.session_state.loans,
    st.session_state.fmv_sources,
)
total_fmv               = summary['total_fmv']
total_exposure          = summary['total_exposure']
total_secured_principal = summary['total_secured_principal']
total_alloc_fmv         = summary['total_alloc_fmv']
wtd_ltv                 = summary['wtd_ltv']
aggregate_ltv           = summary['aggregate_ltv']
overall_pass            = summary['overall_pass']
has_ties                = _portfolio_has_ties()
has_overrides           = any(l.get('override_ltv') for l in st.session_state.loans)

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Total Exposure</div>
        <div class='metric-value'>Rs.{total_exposure:,.0f}</div>
        <div class='metric-sub' style='color:#64748b;'>{len(st.session_state.loans)} facilities</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Total FMV</div>
        <div class='metric-value'>Rs.{total_fmv:,.0f}</div>
        <div class='metric-sub delta-pos'>{len(st.session_state.fmv_sources)} properties</div>
    </div>""", unsafe_allow_html=True)
with k3:
    gc = "gauge-ok" if wtd_ltv <= 50 else ("gauge-warn" if wtd_ltv <= 65 else "gauge-fail")
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>Weighted Avg LTV%</div>
        <div class='metric-value'>{wtd_ltv:.2f}%</div>
        <div class='ltv-gauge-wrap'><div class='{gc}' style='width:{min(wtd_ltv,100):.1f}%'></div></div>
    </div>""", unsafe_allow_html=True)
with k4:
    agc = "gauge-ok" if aggregate_ltv <= 50 else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    st.markdown(f"""
    <div class='aggregate-card'>
        <div class='aggregate-label'>Aggregate LTV%</div>
        <div class='aggregate-value'>{aggregate_ltv:.2f}%</div>
        <div class='aggregate-sub'>Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
        <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
            <div class='{agc}' style='width:{min(aggregate_ltv,100):.1f}%'></div>
        </div>
    </div>""", unsafe_allow_html=True)

if has_overrides or has_ties:
    exempt_loans = [
        r for r in results
        if r.get('Is_Unsecured') and r.get('Exempt_Reason') in ('override', 'tieup')
    ]
    if exempt_loans:
        parts = []
        for r in exempt_loans:
            reason = r.get('Exempt_Reason')
            label  = "Override" if reason == "override" else "Tie-up"
            parts.append(f"[{r.get('loan_account_id','?')}] {r['Loan Type']} ({label})")
        st.markdown(
            f"<div style='background:#fefce8; border:1.5px solid #fde047; border-radius:12px; "
            f"padding:0.75rem 1.25rem; margin:0.5rem 0; font-size:0.85rem; color:#713f12;'>"
            f"<b>LTV-Exempt Facilities:</b> {' &nbsp;|&nbsp; '.join(parts)}</div>",
            unsafe_allow_html=True
        )

if overall_pass:
    st.markdown(
        "<div class='status-banner status-pass'>PORTFOLIO APPROVED — All Facilities Within LTV Limits</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='status-banner status-fail'>PORTFOLIO DECLINED — One or More Facilities Exceed Maximum LTV</div>",
        unsafe_allow_html=True
    )

no_fmv_loans = [r for r in results if r.get('No_FMV_Error')]
if no_fmv_loans:
    names = ", ".join(f"[{r.get('loan_account_id','?')}] {r['Loan Type']}" for r in no_fmv_loans)
    st.error(
        f"No Collateral Available — the following facilities have no FMV allocated: {names}. "
        "Add properties or enable Override for these facilities."
    )

# ── Property Information
st.markdown("### Property Information")

assigned_coll_ids = summary['assigned_collateral_ids']
pool_coll_ids     = summary['pool_collateral_ids']
tied_in_use_map   = _get_tied_in_use()

cid_to_loan_names = {}
for loan in st.session_state.loans:
    if loan.get('collateral_mode') == 'assigned' and not _loan_is_ltv_exempt(loan):
        for cid in loan.get('assigned_collateral_ids', []):
            ac = loan.get('loan_account_id', loan['Loan Type'])
            cid_to_loan_names.setdefault(cid, []).append(f"[{ac}] {loan['Loan Type']}")

prop_rows = []
for src in st.session_state.fmv_sources:
    sid         = src.get('id')
    is_assigned = sid in assigned_coll_ids
    is_tied     = sid in tied_in_use_map
    ctype       = "Assigned" if is_assigned else "Pool"
    row = {
        "Property Reference": src.get('Plot', ''),
        "Owner":              src.get('Owner', 'N/A') or 'N/A',
        "FMV (Rs.)":          f"Rs. {src.get('Amount', 0):,.0f}",
        "Type":               ctype,
        "Linked To (LTV)":    ", ".join(cid_to_loan_names.get(sid, [])) if is_assigned else "Shared Pool",
    }
    if has_ties:
        row["Tied To (Addl.)"] = ", ".join(tied_in_use_map.get(sid, [])) if is_tied else "N/A"
    prop_rows.append(row)

if prop_rows:
    st.dataframe(pd.DataFrame(prop_rows), hide_index=True, use_container_width=True)

    total_pool_fmv     = summary['pool_fmv']
    total_assigned_fmv = sum(
        s['Amount'] for s in st.session_state.fmv_sources
        if s.get('id') in assigned_coll_ids
    )
    n_pool     = len(pool_coll_ids)
    n_assigned = len(assigned_coll_ids)
    n_tied     = sum(1 for s in st.session_state.fmv_sources if s.get('id') in tied_in_use_map)

    pills = (
        f"<div style='display:flex; gap:0.75rem; flex-wrap:wrap; margin-top:0.5rem;'>"
        f"<div style='background:#dbeafe; border:1px solid #93c5fd; border-radius:10px; "
        f"padding:0.5rem 1rem; font-size:0.82rem; color:#1d4ed8; font-weight:600;'>"
        f"Pool: <b>{n_pool}</b> &nbsp;·&nbsp; FMV: <b>Rs. {total_pool_fmv:,.0f}</b></div>"
        f"<div style='background:#fef3c7; border:1px solid #fcd34d; border-radius:10px; "
        f"padding:0.5rem 1rem; font-size:0.82rem; color:#92400e; font-weight:600;'>"
        f"Assigned: <b>{n_assigned}</b> &nbsp;·&nbsp; FMV: <b>Rs. {total_assigned_fmv:,.0f}</b></div>"
    )
    if n_tied:
        pills += (
            f"<div style='background:#fdf4ff; border:1px solid #e9d5ff; border-radius:10px; "
            f"padding:0.5rem 1rem; font-size:0.82rem; color:#6b21a8; font-weight:600;'>"
            f"Tied (Addl. Security): <b>{n_tied}</b></div>"
        )
    if has_overrides:
        n_overrides = sum(1 for l in st.session_state.loans if l.get('override_ltv'))
        pills += (
            f"<div style='background:#fefce8; border:1px solid #fde047; border-radius:10px; "
            f"padding:0.5rem 1rem; font-size:0.82rem; color:#713f12; font-weight:600;'>"
            f"LTV Overrides: <b>{n_overrides}</b> facilities</div>"
        )
    pills += "</div>"
    st.markdown(pills, unsafe_allow_html=True)
elif not st.session_state.fmv_sources and _all_loans_ltv_exempt():
    st.info(
        "No properties added. All facilities are LTV-exempt (Override). "
        "You may add properties in Step 1 if needed as additional/tie-up security."
    )

# ── Portfolio LTV Breakdown
st.markdown("### Portfolio LTV Breakdown")


def display_sort_key(r):
    m = r.get('Max LTV%')
    if m is None:
        return (2, 0)
    return (0 if m <= 50 else 1, -(r.get('Principal', 0)))


sorted_display = sorted(results, key=display_sort_key)
fmv_id_map     = {s['id']: s['Plot'] for s in st.session_state.fmv_sources}
disp_rows      = []

for r in sorted_display:
    is_unsec      = r['Is_Unsecured']
    no_fmv_err    = r.get('No_FMV_Error', False)
    ltv_val       = r.get('LTV%')
    max_ltv       = r.get('Max LTV%')
    exempt_reason = r.get('Exempt_Reason')
    override_flag = r.get('override_ltv', False)
    tieup_flag    = bool(r.get('tied_property_ids'))

    if is_unsec:
        if exempt_reason == "override":
            ltv_disp = "Overridden"
        elif exempt_reason == "tieup":
            ltv_disp = "Tie-up Exempt"
        else:
            ltv_disp = "N/A (Unsecured)"
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
        req_fmv = r['Principal'] / (max_ltv / 100.0)
        sv      = r.get('Total FMV', 0.0) - req_fmv
        surplus_disp = f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"

    flags_list = []
    if override_flag:
        flags_list.append("Override")
    if tieup_flag:
        flags_list.append("Tie-up")
    flags_str = " + ".join(flags_list) if flags_list else ""

    row = {
        "A/C No.":             r.get('loan_account_id', 'N/A'),
        "Facility":            r['Loan Type'],
        "Principal":           f"Rs. {r['Principal']:,.0f}",
        "Assigned FMV":        "N/A" if is_unsec else f"Rs. {r['Assigned FMV']:,.0f}",
        "Pool FMV":            "N/A" if is_unsec else f"Rs. {r['Pool FMV']:,.0f}",
        "Total FMV":           "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
        "LTV%":                ltv_disp,
        "Max LTV":             "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
        "Surplus/(Shortfall)": surplus_disp,
        "Status":              "PASS" if r['Pass_Status'] else "FAIL",
        "Flags":               flags_str if flags_str else "-",
    }
    if has_ties:
        tied_names     = [fmv_id_map.get(cid, str(cid)) for cid in r.get('tied_property_ids', [])]
        row["Tied Properties"] = ", ".join(tied_names) if tied_names else "N/A"
    disp_rows.append(row)

agg_row = {
    "A/C No.": "AGG", "Facility": "AGGREGATE",
    "Principal": f"Rs. {total_exposure:,.0f}",
    "Assigned FMV": "N/A", "Pool FMV": "N/A",
    "Total FMV": f"Rs. {total_fmv:,.0f}",
    "LTV%": f"{aggregate_ltv:.2f}%", "Max LTV": "N/A",
    "Surplus/(Shortfall)": "N/A",
    "Status": "PASS" if aggregate_ltv <= 70 else "FAIL",
    "Flags": "-",
}
if has_ties:
    agg_row["Tied Properties"] = "N/A"
disp_rows.append(agg_row)

st.dataframe(pd.DataFrame(disp_rows), hide_index=True, use_container_width=True)

# ── LTV Visual Summary
st.markdown("### LTV Visual Summary")
secured_disp = [r for r in sorted_display if not r['Is_Unsecured']]
exempt_disp  = [r for r in sorted_display if r['Is_Unsecured'] and r.get('Exempt_Reason') in ('override', 'tieup')]

if secured_disp or exempt_disp:
    all_visual = secured_disp + exempt_disp
    num_cols   = min(len(all_visual) + 1, 4)
    bar_cols   = st.columns(num_cols)

    for i, row in enumerate(all_visual):
        col_idx       = i % num_cols
        is_unsec      = row.get('Is_Unsecured', False)
        ltv           = row.get('LTV%')
        max_ltv       = row.get('Max LTV%') or 100
        no_fmv_err    = row.get('No_FMV_Error', False)
        ac_id         = row.get('loan_account_id', '?')
        exempt_reason = row.get('Exempt_Reason')
        override_flag = row.get('override_ltv', False)
        tieup_flag    = bool(row.get('tied_property_ids'))

        if is_unsec:
            if exempt_reason == "override":
                badge_color = "#713f12"; badge_bg = "#fefce8"; badge_border = "#fde047"
                badge_label = "LTV Override"; ltv_text = "Overridden"
            else:
                badge_color = "#6b21a8"; badge_bg = "#fdf4ff"; badge_border = "#e9d5ff"
                badge_label = "Tie-up Exempt"; ltv_text = "Tie-up Exempt"

            card_html = (
                f"<div style='background:linear-gradient(135deg,{badge_bg} 0%,#ffffff 100%); "
                f"border:1.5px solid {badge_border}; border-radius:12px; padding:1rem; margin-bottom:0.75rem;'>"
                f"<div style='display:flex; justify-content:space-between; margin-bottom:0.15rem;'>"
                f"<div style='font-size:0.75rem; font-weight:700; color:#1e1b4b;'>{row['Loan Type']}</div>"
                f"<div style='font-size:0.65rem; font-weight:700; color:{badge_color}; "
                f"background:{badge_bg}; border:1px solid {badge_border}; border-radius:6px; padding:0.1rem 0.35rem;'>{badge_label}</div>"
                f"</div>"
                f"<div style='font-family:monospace; font-size:0.68rem; font-weight:700; color:#4c1d95; "
                f"background:#ede9fe; display:inline-block; padding:0.1rem 0.4rem; border-radius:4px; margin-bottom:0.3rem;'>{ac_id}</div>"
                f"<div style='font-size:1.5rem; font-weight:700; color:{badge_color}; font-family:monospace;'>{ltv_text}</div>"
                f"<div style='font-size:0.72rem; color:#64748b;'>Principal: Rs.{row['Principal']:,.0f}</div>"
                f"<span class='surplus-na'>No LTV Required</span>"
                f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>"
                f"<div style='height:100%; background:{badge_border}; border-radius:99px; width:100%;'></div>"
                f"</div></div>"
            )
            with bar_cols[col_idx]:
                st.markdown(card_html, unsafe_allow_html=True)
            continue

        if no_fmv_err or ltv is None:
            pct_bar = 100.0; fill_cls = "gauge-err"; s_color = "#dc2626"
            ltv_text = "No FMV"; surp_cls = "surplus-err"; surp_text = "No collateral allocated"
        else:
            pct_bar  = min((ltv / max_ltv) * 100, 100)
            fill_cls = "gauge-ok" if ltv <= max_ltv * 0.8 else ("gauge-warn" if ltv <= max_ltv else "gauge-fail")
            s_color  = "#059669" if row['Pass_Status'] else "#dc2626"
            ltv_text = f"{ltv:.2f}%"
            sv       = row.get('Total FMV', 0.0) - row['Principal'] / (max_ltv / 100.0)
            surp_cls  = "surplus-pos" if sv >= 0 else "surplus-neg"
            surp_text = f"Surplus Rs. {sv:,.0f}" if sv >= 0 else f"Short Rs. {abs(sv):,.0f}"

        mode     = row.get('Collateral_Mode', 'pool')
        mode_lbl = "Pool" if mode == "pool" else "Assigned"
        coll_names = row.get('Collateral_Names', [])
        coll_text  = (
            ", ".join(coll_names[:2]) + ("..." if len(coll_names) > 2 else "")
            if coll_names else "Pool"
        )

        with bar_cols[col_idx]:
            st.markdown(
                "<div style='background:white; border:1px solid #ddd6fe; border-radius:12px; "
                "padding:1rem; margin-bottom:0.75rem;'>"
                "<div style='display:flex; justify-content:space-between; margin-bottom:0.15rem;'>"
                f"<div style='font-size:0.75rem; font-weight:700; color:#1e1b4b;'>{row['Loan Type']}</div>"
                f"<div style='font-size:0.68rem; color:#64748b;'>{mode_lbl}</div>"
                "</div>"
                f"<div style='font-family:monospace; font-size:0.68rem; font-weight:700; color:#4c1d95; "
                f"background:#ede9fe; display:inline-block; padding:0.1rem 0.4rem; border-radius:4px; margin-bottom:0.3rem;'>{ac_id}</div>"
                f"<div style='font-size:0.68rem; color:#94a3b8; margin-bottom:0.4rem;'>{coll_text}</div>"
                f"<div style='font-size:1.5rem; font-weight:700; color:{s_color}; font-family:monospace;'>{ltv_text}</div>"
                f"<div style='font-size:0.72rem; color:#64748b;'>Max: {max_ltv:.0f}% &nbsp;·&nbsp; FMV: Rs.{row['Total FMV']:,.0f}</div>"
                f"<span class='{surp_cls}'>{surp_text}</span>"
                f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'><div class='{fill_cls}' style='width:{pct_bar:.1f}%'></div></div>"
                "</div>",
                unsafe_allow_html=True
            )

    agg_col_idx  = len(all_visual) % num_cols
    agg_fill_cls = "gauge-ok" if aggregate_ltv <= 50 else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    agg_color    = "#059669" if aggregate_ltv <= 70 else "#dc2626"
    with bar_cols[agg_col_idx]:
        st.markdown(
            "<div style='background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%); "
            "border:1px solid #4338ca; border-radius:12px; padding:1rem; margin-bottom:0.75rem;'>"
            "<div style='font-size:0.7rem; font-weight:700; color:#a5b4fc; text-transform:uppercase; margin-bottom:0.3rem;'>AGGREGATE</div>"
            f"<div style='font-size:1.5rem; font-weight:700; color:{agg_color}; font-family:monospace;'>{aggregate_ltv:.2f}%</div>"
            f"<div style='font-size:0.74rem; color:#c7d2fe;'>Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>"
            f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>"
            f"<div class='{agg_fill_cls}' style='width:{min(aggregate_ltv,100):.1f}%'></div></div></div>",
            unsafe_allow_html=True
        )
else:
    st.info("No facilities with active LTV calculations in portfolio.")

# ── LTV Override & Tie-up Register (table format)
exempt_register = [
    r for r in results
    if r.get('Is_Unsecured') and r.get('Exempt_Reason') in ('override', 'tieup')
]
if exempt_register:
    with st.expander("LTV Override & Tie-up Register", expanded=False):
        st.caption(
            "Facilities listed here are excluded from LTV calculation. "
            "Override must be sanctioned by credit authority. "
            "Tie-up properties are additional/secondary security only."
        )

        fmv_src_map   = {s['id']: s for s in st.session_state.fmv_sources}
        register_rows = []

        for r in exempt_register:
            ac_id         = r.get('loan_account_id', '?')
            exempt_reason = r.get('Exempt_Reason', '')
            exempt_label  = (
                "Manual LTV Override" if exempt_reason == "override"
                else "Tie-up Properties Selected"
            )

            tied_names, tied_owners, tied_fmv_total = [], [], 0.0
            for cid in r.get('tied_property_ids', []):
                src = fmv_src_map.get(cid)
                if src:
                    tied_names.append(src.get('Plot', ''))
                    tied_owners.append(src.get('Owner', '') or 'N/A')
                    tied_fmv_total += src.get('Amount', 0.0)

            unique_owners = list(dict.fromkeys(tied_owners))

            register_rows.append({
                "A/C No.":         ac_id,
                "Facility Type":   r['Loan Type'],
                "Principal (Rs.)": f"Rs. {r['Principal']:,.0f}",
                "Exempt Type":     exempt_label,
                "Tied Properties": ", ".join(tied_names) if tied_names else "—",
                "Tied Owner(s)":   ", ".join(unique_owners) if unique_owners else "—",
                "Tied FMV (Rs.)":  f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "—",
                "LTV Requirement": "No LTV Required",
            })

        st.dataframe(
            pd.DataFrame(register_rows),
            hide_index=True,
            use_container_width=True,
        )
        st.markdown(
            "<div style='font-size:0.77rem; color:#92400e; background:#fefce8; "
            "border:1px solid #fde047; border-radius:8px; padding:0.6rem 0.9rem; margin-top:0.5rem;'>"
            "<b>⚠ Note:</b> Overridden and tie-up facilities consume <b>no collateral FMV</b>. "
            "Manual overrides must be sanctioned by credit authority. "
            "Tie-up properties serve as additional/secondary security only."
            "</div>",
            unsafe_allow_html=True
        )

# ── Manage Portfolio
with st.expander("Manage Portfolio — Remove Loans", expanded=False):
    if not st.session_state.loans:
        st.info("No loans added yet.")
    else:
        for loan in st.session_state.loans:
            lc1, lc2, lc3, lc4, lc5 = st.columns([2, 3, 2, 2, 1])
            mode_lbl = {"pool": "[Pool]", "assigned": "[Assigned]"}.get(
                loan.get('collateral_mode', 'pool'), "[Pool]"
            )
            ac_id = loan.get('loan_account_id', '?')
            with lc1:
                st.markdown(f"<span class='ac-id-badge'>{ac_id}</span>", unsafe_allow_html=True)
            with lc2:
                st.markdown(f"**{mode_lbl} {loan['Loan Type']}**  Rs. {loan['Principal']:,.0f}")
            with lc3:
                cnames = _get_collateral_names(
                    loan.get('assigned_collateral_ids', []),
                    st.session_state.fmv_sources
                )
                tied_n = len(loan.get('tied_property_ids', []))
                label  = " | ".join(cnames) if cnames else "Pool"
                if tied_n:
                    label += f" | {tied_n} tied"
                st.markdown(f"<span style='font-size:0.8rem; color:#64748b;'>{label}</span>", unsafe_allow_html=True)
            with lc4:
                flags_html = ""
                if loan.get('override_ltv'):
                    flags_html += "<span class='override-badge'>Override</span>"
                if loan.get('tied_property_ids'):
                    flags_html += "<span class='tieup-badge'>Tie-up</span>"
                if flags_html:
                    st.markdown(flags_html, unsafe_allow_html=True)
                else:
                    st.markdown("<span style='font-size:0.75rem; color:#94a3b8;'>-</span>", unsafe_allow_html=True)
            with lc5:
                if st.button("Remove", key=f"rm_loan_{loan['_loan_id']}"):
                    st.session_state.loans = [
                        l for l in st.session_state.loans if l['_loan_id'] != loan['_loan_id']
                    ]
                    st.rerun()

# ── PDF Export
with st.expander("Generate PDF Report", expanded=True):
    ec1, ec2 = st.columns([3, 1])
    with ec1:
        report_name = st.text_input(
            "Client / Portfolio Name",
            placeholder="e.g. Ramesh Sharma - Q2 Review",
            label_visibility="collapsed",
        )
    with ec2:
        if st.button("Generate PDF", type="primary"):
            if not report_name.strip():
                st.error("Enter a client name.")
            else:
                with st.spinner("Generating..."):
                    try:
                        pdf_bytes = generate_pdf(
                            report_name.strip(), results,
                            st.session_state.fmv_sources, summary
                        )
                        safe_name = (
                            report_name.strip()
                            .replace(' ', '_').replace('/', '-').replace('\\', '-')
                        )
                        st.session_state['generated_pdf']      = pdf_bytes
                        st.session_state['generated_pdf_name'] = (
                            f"LTV_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

    if 'generated_pdf' in st.session_state:
        st.markdown("---")
        st.success("Report ready.")
        st.download_button(
            label="Download PDF",
            data=st.session_state['generated_pdf'],
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
        )
