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


def _get_all_passwords():
    try:
        return [str(v).strip() for v in st.secrets["passwords"].values()]
    except Exception:
        return []


def _show_login():
    st.markdown("""
    <style>
        #MainMenu, footer, header { visibility: hidden; }
        .stApp {
            background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%) !important;
        }
        .block-container {
            max-width: 480px !important;
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .login-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.75rem;
            box-shadow: 0 4px 24px rgba(124,58,237,0.12);
            border: 1px solid #ede9fe;
            margin: 0 auto;
        }
        .login-header { text-align: center; margin-bottom: 1.25rem; }
        .login-icon { font-size: 2.25rem; line-height: 1; margin-bottom: 0.25rem; }
        .login-title {
            font-size: 1.25rem; font-weight: 800; color: #1e1b4b;
            letter-spacing: -0.02em; margin-bottom: 0.25rem;
        }
        .login-badge {
            display: inline-block; background: #ede9fe; color: #6d28d9;
            font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em;
            text-transform: uppercase; padding: 0.15rem 0.6rem; border-radius: 99px;
        }
        .input-group { margin-bottom: 0.75rem; }
        .input-label {
            font-size: 0.7rem; font-weight: 700; color: #374151;
            text-transform: uppercase; letter-spacing: 0.06em;
            margin-bottom: 0.25rem; display: block;
        }
        div[data-testid="stTextInput"] > div > div > input {
            border-radius: 8px !important; border: 1.5px solid #e5e7eb !important;
            padding: 0.5rem 0.75rem !important; font-size: 0.95rem !important;
            background: #ffffff !important; color: #111827 !important;
            min-height: 2.25rem !important;
        }
        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: #7c3aed !important;
            box-shadow: 0 0 0 2px rgba(124,58,237,0.1) !important;
        }
        div[data-testid="stTextInput"] label { display: none !important; }
        div.stButton > button {
            background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
            color: white !important; border: none !important;
            border-radius: 8px !important; font-weight: 700 !important;
            font-size: 0.9rem !important; padding: 0.6rem !important;
            width: 100% !important; margin-top: 0.25rem !important;
            box-shadow: 0 2px 8px rgba(124,58,237,0.25) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(124,58,237,0.35) !important;
        }
        .err-box {
            background: #fef2f2; border: 1.5px solid #fca5a5;
            color: #991b1b; border-radius: 8px; padding: 0.75rem;
            font-size: 0.85rem; font-weight: 600; margin-top: 0.75rem;
            text-align: center; line-height: 1.5;
        }
        .tip-highlight {
            background: #fee2e2; padding: 0.2rem 0.4rem;
            border-radius: 4px; font-family: monospace; font-weight: 700;
        }
        .login-footer {
            text-align: center; font-size: 0.7rem;
            color: #9ca3af; margin-top: 1rem;
        }
        div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    with st.container():
        st.markdown("""
        <div class="login-card">
            <div class="login-header">
                <div class="login-icon">🏦</div>
                <div class="login-title">LTV Analysis Engine</div>
                <div class="login-badge">Secure Sign In</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<span class="input-label">👤 Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            label="username", placeholder="Type: admin", key="_login_u",
            label_visibility="collapsed", autocomplete="username",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="input-group">', unsafe_allow_html=True)
        st.markdown('<span class="input-label">🔒 Password</span>', unsafe_allow_html=True)
        password = st.text_input(
            label="password", placeholder="Type password here", type="password",
            key="_login_p", label_visibility="collapsed", autocomplete="current-password",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        clicked = st.button("Sign In", key="_login_btn", use_container_width=True)

        if clicked:
            u = str(username).strip()
            p = str(password).strip()
            if not u:
                st.session_state["_login_error"] = "⚠️ Enter username: <span class='tip-highlight'>Username</span>"
                st.rerun()
            elif not p:
                st.session_state["_login_error"] = "⚠️ Please enter your password."
                st.rerun()
            elif _check_credentials(u, p):
                st.session_state["authenticated"] = True
                st.session_state["auth_username"] = u
                st.session_state["_login_error"] = ""
                st.rerun()
            else:
                all_passwords = _get_all_passwords()
                if u in all_passwords:
                    error_msg = (
                        f"❌ <b>You entered the password as username!</b><br><br>"
                        f"You typed: <span class='tip-highlight'>{u}</span> in the username field.<br><br>"
                        f"<b>Correct way:</b><br>"
                        f"• Username: <span class='tip-highlight'>admin</span><br>"
                        f"• Password: <span class='tip-highlight'>{u}</span>"
                    )
                else:
                    error_msg = f"❌ Invalid credentials.<br><br>You entered: '{u}'"
                st.session_state["_login_error"] = error_msg
                st.rerun()

        err = st.session_state.get("_login_error", "")
        if err:
            st.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)

        st.markdown("""
            <div class="login-footer">🔐 Secured by Streamlit Cloud</div>
        </div>
        """, unsafe_allow_html=True)


# ── Auth state init
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
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif; color: #1a1f36; letter-spacing: -0.01em;
    }
    .block-container { max-width: 96% !important; padding-top: 1.5rem !important; }
    .main { background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%); }
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        border-radius: 10px !important; border: 1px solid #e2e8f0 !important;
        padding: 0.65rem 0.9rem !important; font-size: 0.95rem !important;
        background: #f8fafc !important; transition: all 0.2s;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
        background: white !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
        box-shadow: 4px 0 24px rgba(0,0,0,0.18);
    }
    [data-testid="stSidebar"] * { color: #e0e7ff; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.95) !important;
        color: #1e1b4b !important; font-weight: 600;
    }
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #7c3aed !important; border-color: #7c3aed !important;
        color: white !important; border-radius: 8px; font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #6d28d9 !important; border-color: #6d28d9 !important;
        transform: translateY(-1px);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
        padding: 1.25rem 1.5rem; border-radius: 14px; border: 1px solid #ddd6fe;
        box-shadow: 0 4px 14px rgba(124,58,237,0.08);
    }
    .metric-label {
        font-size: 0.75rem; font-weight: 700; color: #7c3aed;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.7rem; font-weight: 700; color: #1e1b4b;
        font-family: 'DM Mono', monospace; line-height: 1.1;
    }
    .metric-sub { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
    .delta-pos { color: #059669; }
    .delta-neg { color: #dc2626; }
    .status-banner {
        padding: 0.9rem 1.5rem; border-radius: 12px; font-weight: 700;
        font-size: 1rem; text-align: center; margin: 1.25rem 0;
    }
    .status-pass { background: #d1fae5; border: 2px solid #059669; color: #065f46; }
    .status-fail { background: #fee2e2; border: 2px solid #dc2626; color: #991b1b; }
    .aggregate-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 1.25rem 1.5rem; border-radius: 14px; border: 1px solid #4338ca;
        box-shadow: 0 4px 14px rgba(30,27,75,0.18);
    }
    .aggregate-label {
        font-size: 0.75rem; font-weight: 700; color: #a5b4fc;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem;
    }
    .aggregate-value {
        font-size: 1.7rem; font-weight: 700; color: #ffffff;
        font-family: 'DM Mono', monospace; line-height: 1.1;
    }
    .aggregate-sub { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; color: #c7d2fe; }
    .ltv-gauge-wrap {
        margin-top: 0.4rem; height: 7px; background: #e2e8f0;
        border-radius: 99px; overflow: hidden;
    }
    .gauge-ok   { height: 100%; border-radius: 99px; background: #059669; }
    .gauge-warn { height: 100%; border-radius: 99px; background: #f59e0b; }
    .gauge-fail { height: 100%; border-radius: 99px; background: #dc2626; }

    /* ── Property Info Cards */
    .prop-card {
        background: #ffffff;
        border: 1px solid #e8e0fd;
        border-radius: 14px;
        padding: 1rem 1.15rem;
        box-shadow: 0 2px 10px rgba(124,58,237,0.07);
        margin-bottom: 0.5rem;
        transition: box-shadow 0.2s;
    }
    .prop-card:hover { box-shadow: 0 5px 18px rgba(124,58,237,0.13); }
    .prop-title { font-size: 0.9rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.15rem; }
    .prop-owner { font-size: 0.75rem; color: #7c3aed; font-weight: 600; margin-bottom: 0.4rem; }
    .prop-fmv { font-size: 1.2rem; font-weight: 700; color: #1e1b4b; font-family: 'DM Mono', monospace; }
    .prop-badge {
        display: inline-block; font-size: 0.68rem; font-weight: 700;
        padding: 0.15rem 0.55rem; border-radius: 99px; margin-top: 0.35rem;
    }
    .badge-pool { background: #dbeafe; color: #1d4ed8; }
    .badge-assigned { background: #fef3c7; color: #92400e; }
    .prop-usage { font-size: 0.72rem; color: #64748b; margin-top: 0.3rem; }

    /* ── Surplus/Shortfall badge on gauge cards */
    .surplus-badge {
        display: inline-block; font-size: 0.72rem; font-weight: 700;
        padding: 0.2rem 0.6rem; border-radius: 8px; margin-top: 0.4rem;
    }
    .surplus-pos { background: #d1fae5; color: #065f46; }
    .surplus-neg { background: #fee2e2; color: #991b1b; }
    .surplus-na  { background: #f1f5f9; color: #64748b; }

    /* ── Landing page */
    .landing-wrap { max-width: 980px; margin: 0 auto; padding: 2rem 1rem; }
    .landing-hero {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 22px; padding: 3.25rem 2.75rem; text-align: center;
        box-shadow: 0 12px 48px rgba(30,27,75,0.35); margin-bottom: 2rem;
        position: relative; overflow: hidden;
    }
    .landing-hero::before {
        content: '';
        position: absolute; inset: 0;
        background: radial-gradient(ellipse at 60% 0%, rgba(124,58,237,0.35) 0%, transparent 60%);
        pointer-events: none;
    }
    .landing-hero-icon { font-size: 3.75rem; margin-bottom: 0.85rem; position: relative; }
    .landing-hero-title {
        font-size: 2.4rem; font-weight: 800; color: #ffffff;
        letter-spacing: -0.04em; margin-bottom: 0.6rem; line-height: 1.15;
        position: relative;
    }
    .landing-hero-sub {
        font-size: 1.05rem; color: #c7d2fe; max-width: 580px;
        margin: 0 auto 1.75rem; line-height: 1.65; position: relative;
    }
    .landing-badge-row {
        display: flex; justify-content: center; gap: 0.55rem;
        flex-wrap: wrap; position: relative;
    }
    .landing-badge {
        background: rgba(255,255,255,0.1); color: #e0e7ff;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 99px; padding: 0.3rem 0.9rem;
        font-size: 0.73rem; font-weight: 600; letter-spacing: 0.04em;
        backdrop-filter: blur(4px);
    }
    .steps-grid {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 1.1rem; margin-bottom: 1.6rem;
    }
    .step-card {
        background: #ffffff; border-radius: 16px;
        border: 1px solid #e8e0fd; padding: 1.5rem 1.25rem;
        box-shadow: 0 2px 16px rgba(124,58,237,0.07);
        transition: box-shadow 0.2s;
    }
    .step-card:hover { box-shadow: 0 6px 24px rgba(124,58,237,0.14); }
    .step-num {
        width: 2.1rem; height: 2.1rem; border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white; font-weight: 800; font-size: 0.9rem;
        display: flex; align-items: center; justify-content: center;
        margin-bottom: 0.8rem; box-shadow: 0 2px 8px rgba(109,40,217,0.35);
    }
    .step-title { font-size: 0.97rem; font-weight: 700; color: #1e1b4b; margin-bottom: 0.35rem; }
    .step-desc { font-size: 0.82rem; color: #64748b; line-height: 1.55; }
    .feature-grid {
        display: grid; grid-template-columns: repeat(2, 1fr);
        gap: 0.9rem; margin-bottom: 1.6rem;
    }
    .feature-pill {
        background: linear-gradient(135deg, #faf8ff, #f0ebff);
        border: 1px solid #e4d9fe; border-radius: 12px;
        padding: 0.85rem 1.1rem; display: flex; align-items: flex-start; gap: 0.7rem;
        transition: border-color 0.2s;
    }
    .feature-pill:hover { border-color: #a78bfa; }
    .feature-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 0.05rem; }
    .feature-text { font-size: 0.83rem; color: #4c1d95; font-weight: 700; line-height: 1.4; }
    .feature-sub { font-size: 0.75rem; color: #7c3aed; font-weight: 400; margin-top: 0.1rem; }
    .landing-cta {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 1.5px solid #86efac; border-radius: 16px;
        padding: 1.35rem 1.75rem; text-align: center;
    }
    .landing-cta-title { font-size: 1.05rem; font-weight: 700; color: #14532d; margin-bottom: 0.35rem; }
    .landing-cta-sub { font-size: 0.84rem; color: #166534; line-height: 1.5; }
    @media (max-width: 700px) {
        .steps-grid { grid-template-columns: 1fr; }
        .feature-grid { grid-template-columns: 1fr; }
        .landing-hero-title { font-size: 1.6rem; }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ⚙️ DEFAULT LTV POLICY
# ==========================================
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",                "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Auto Loan",                "Max LTV%": None,  "Unsecured": False},
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


def get_policy_dict():
    return {
        p["Loan Type"]: (None if p["Unsecured"] else p["Max LTV%"])
        for p in st.session_state.ltv_policy
    }


def safe_str(text):
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u00a0': ' ',
        '\u20b9': 'Rs.', '\u2265': '>=', '\u2264': '<=', '\u2026': '...',
    }
    for ch, rep in replacements.items():
        text = text.replace(ch, rep)
    return text.encode('latin-1', errors='replace').decode('latin-1')


# ==========================================
# 🔧 SESSION STATE INIT & MIGRATION
# ==========================================
def _next_fmv_id():
    fid = st.session_state.fmv_id_counter
    st.session_state.fmv_id_counter += 1
    return fid


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


if 'fmv_id_counter' not in st.session_state:
    st.session_state.fmv_id_counter = 0
if 'loan_id_counter' not in st.session_state:
    st.session_state.loan_id_counter = 0
if 'loans' not in st.session_state:
    st.session_state.loans = []
if 'fmv_sources' not in st.session_state:
    st.session_state.fmv_sources = []
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


# ==========================================
# 🧮 PORTFOLIO LTV ENGINE
# ==========================================
def run_portfolio_ltv(loans, fmv_sources):
    policy = get_policy_dict()
    fmv_sources = [s for s in fmv_sources if 'id' in s]

    collateral_usage = {s['id']: [] for s in fmv_sources}
    for loan in loans:
        if loan.get('collateral_mode') == 'assigned':
            for cid in loan.get('assigned_collateral_ids', []):
                if cid in collateral_usage:
                    collateral_usage[cid].append(loan['_loan_id'])

    assigned_collateral_ids = {
        cid for cid, users in collateral_usage.items() if users
    }
    pool_collateral_ids = {
        s['id'] for s in fmv_sources if s['id'] not in assigned_collateral_ids
    }
    collateral_fmv_map = {s['id']: s['Amount'] for s in fmv_sources}

    loan_collateral_shares = {loan['_loan_id']: {} for loan in loans}
    for cid in assigned_collateral_ids:
        user_loan_ids = collateral_usage[cid]
        cid_fmv = collateral_fmv_map.get(cid, 0.0)
        if len(user_loan_ids) == 1:
            lid = user_loan_ids[0]
            if lid in loan_collateral_shares:
                loan_collateral_shares[lid][cid] = cid_fmv
        else:
            sharing_loans = [l for l in loans if l['_loan_id'] in user_loan_ids]
            total_principal = sum(l['Principal'] for l in sharing_loans)
            for sl in sharing_loans:
                share = (
                    cid_fmv * (sl['Principal'] / total_principal)
                    if total_principal > 0 else cid_fmv / len(sharing_loans)
                )
                if sl['_loan_id'] in loan_collateral_shares:
                    loan_collateral_shares[sl['_loan_id']][cid] = share

    loan_assigned_fmv = {}
    for loan in loans:
        lid = loan['_loan_id']
        if loan.get('collateral_mode') == 'assigned':
            loan_assigned_fmv[lid] = sum(
                loan_collateral_shares.get(lid, {}).values()
            )
        else:
            loan_assigned_fmv[lid] = 0.0

    pool_fmv = sum(
        s['Amount'] for s in fmv_sources if s['id'] in pool_collateral_ids
    )

    def waterfall_sort_key(loan):
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            return (2, 0)
        return (0 if max_ltv <= 50 else 1, -loan['Principal'])

    pool_participating = [
        l for l in loans
        if policy.get(l['Loan Type']) is not None
        and l.get('collateral_mode', 'pool') == 'pool'
    ]
    pool_participating_sorted = sorted(pool_participating, key=waterfall_sort_key)
    remaining_pool = pool_fmv
    pool_alloc = {}
    last_idx = len(pool_participating_sorted) - 1

    for i, loan in enumerate(pool_participating_sorted):
        lid = loan['_loan_id']
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            pool_alloc[lid] = 0.0
            continue
        principal = loan['Principal']
        already_have = loan_assigned_fmv.get(lid, 0.0)
        req_total = principal / (max_ltv / 100.0)
        pool_needed = max(0.0, req_total - already_have)
        allocated = remaining_pool if i == last_idx else min(pool_needed, remaining_pool)
        pool_alloc[lid] = allocated
        remaining_pool = max(0.0, remaining_pool - allocated)

    total_fmv = sum(s['Amount'] for s in fmv_sources)
    results = []

    for loan in loans:
        lid = loan['_loan_id']
        lt = loan['Loan Type']
        max_ltv = policy.get(lt)
        principal = loan['Principal']
        mode = loan.get('collateral_mode', 'pool')

        if max_ltv is None:
            results.append({
                **loan,
                'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0,
                'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True,
                'Is_Unsecured': True, 'Collateral_Mode': mode,
                'Collateral_Names': [], 'Shared_Collateral_Ids': [],
            })
            continue

        assigned_fmv_val = loan_assigned_fmv.get(lid, 0.0)
        pool_fmv_val = pool_alloc.get(lid, 0.0)
        total_alloc = assigned_fmv_val + pool_fmv_val
        ltv_pct = (
            principal / total_alloc * 100.0 if total_alloc > 0 else float('inf')
        )
        passes = (ltv_pct <= max_ltv) if total_alloc > 0 else False

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
            'Shared_Collateral_Ids': shared_cids,
        })

    secured_results = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure = sum(r['Principal'] for r in results)
    total_alloc_fmv = sum(r['Total FMV'] for r in secured_results)
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
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 27, 75)
        self.cell(0, 10, 'LTV ANALYSIS REPORT', 0, 1, 'L')
        self.set_draw_color(124, 58, 237)
        self.set_line_width(0.5)
        self.line(10, 20, 200, 20)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(
            0, 10,
            safe_str(
                f'Page {self.page_no()} | LTV Engine | '
                f'{datetime.now().strftime("%B %d, %Y")}'
            ),
            0, 0, 'C'
        )


def generate_pdf(client_name, results, fmv_sources, summary):
    pdf = PDFReport()
    pdf.add_page()

    total_fmv = summary['total_fmv']
    total_exposure = summary['total_exposure']
    aggregate_ltv = summary['aggregate_ltv']
    overall_pass = summary['overall_pass']
    total_secured_p = summary['total_secured_principal']

    # ── Executive Summary
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "EXECUTIVE SUMMARY", 0, 1)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    def kv(label, value):
        pdf.set_font("Arial", "", 10)
        pdf.cell(80, 6, safe_str(label), 0, 0)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, safe_str(str(value)), 0, 1)

    kv("Client Name:", client_name)
    kv("Analysis Date:", datetime.now().strftime("%B %d, %Y"))
    kv("Total Loan Exposure:", f"Rs. {total_exposure:,.2f}")
    kv("Total Collateral FMV:", f"Rs. {total_fmv:,.2f}")
    kv("Aggregate LTV%:", f"{aggregate_ltv:.2f}%")

    pdf.ln(3)
    res_text = (
        "APPROVED - Within LTV Limits" if overall_pass
        else "DECLINED - Exceeds LTV Limits"
    )
    if overall_pass:
        pdf.set_text_color(5, 150, 105)
    else:
        pdf.set_text_color(220, 38, 38)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, safe_str(f"Assessment Result: {res_text}"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    # ── Collateral / FMV Sources
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "COLLATERAL / FMV SOURCES", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    col_w_fmv = [70, 35, 25, 60]

    pdf.set_font("Arial", "B", 7)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w_fmv[0], 7, "Plot / Property Reference", 1, 0, 'C', fill=True)
    pdf.cell(col_w_fmv[1], 7, "FMV (Rs.)", 1, 0, 'C', fill=True)
    pdf.cell(col_w_fmv[2], 7, "Type", 1, 0, 'C', fill=True)
    pdf.cell(col_w_fmv[3], 7, "Owner", 1, 1, 'C', fill=True)

    pdf.set_font("Arial", "", 8)
    assigned_ids = summary['assigned_collateral_ids']

    for i, src in enumerate(fmv_sources):
        fid = src.get('id', i)
        fill = (i % 2 == 0)
        pdf.set_fill_color(248, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        ctype = "Assigned" if fid in assigned_ids else "Pool"
        owner = src.get('Owner', '—') or '—'
        pdf.cell(col_w_fmv[0], 6, safe_str(src['Plot']), 1, 0, 'L', fill)
        pdf.cell(col_w_fmv[1], 6, f"{src['Amount']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w_fmv[2], 6, safe_str(ctype), 1, 0, 'C', fill)
        pdf.cell(col_w_fmv[3], 6, safe_str(owner[:30]), 1, 1, 'L', fill)

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w_fmv[0], 6, "TOTAL", 1, 0, 'R', True)
    pdf.cell(col_w_fmv[1], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w_fmv[2] + col_w_fmv[3], 6, "", 1, 1, '', True)

    # ── Facility LTV Breakdown
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "FACILITY LTV BREAKDOWN", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    col_w = [40, 20, 20, 20, 18, 14, 14, 24, 20]
    hdrs = [
        "Facility Type", "Principal", "Asgn.FMV",
        "Pool FMV", "Tot.FMV", "LTV%", "Max%", "Surplus/(Dfct)", "Status"
    ]

    pdf.set_font("Arial", "B", 7)
    pdf.set_fill_color(237, 233, 254)
    for i, h in enumerate(hdrs):
        pdf.cell(col_w[i], 7, h, 1, 0, 'C', fill=True)
    pdf.ln()

    def display_sort(r):
        m = r.get('Max LTV%')
        if m is None:
            return (2, 0)
        return (0 if m <= 50 else 1, -(r.get('Principal', 0)))

    for idx, row in enumerate(sorted(results, key=display_sort)):
        fill = (idx % 2 == 0)
        pdf.set_fill_color(248, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        is_unsec = row.get('Is_Unsecured', False)
        max_ltv = row.get('Max LTV%')
        ltv_val = row.get('LTV%')
        ltv_disp = "N/A" if (is_unsec or ltv_val is None) else f"{ltv_val:.1f}%"
        max_disp = "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%"
        asgn_disp = "N/A" if is_unsec else f"{row['Assigned FMV']:,.0f}"
        pool_disp = "N/A" if is_unsec else f"{row['Pool FMV']:,.0f}"
        total_disp = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"

        if is_unsec or max_ltv is None:
            surplus_disp = "N/A"
            surplus_val = None
        else:
            req_fmv = row['Principal'] / (max_ltv / 100.0)
            actual_fmv = row.get('Total FMV', 0.0)
            surplus_val = actual_fmv - req_fmv
            if surplus_val >= 0:
                surplus_disp = f"+{surplus_val:,.0f}"
            else:
                surplus_disp = f"({abs(surplus_val):,.0f})"

        status = "PASS" if row['Pass_Status'] else "FAIL"

        pdf.set_font("Arial", "", 8)
        pdf.cell(col_w[0], 6, safe_str(row['Loan Type']), 1, 0, 'L', fill)
        pdf.cell(col_w[1], 6, f"{row['Principal']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w[2], 6, safe_str(asgn_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[3], 6, safe_str(pool_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[4], 6, safe_str(total_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[5], 6, safe_str(ltv_disp), 1, 0, 'C', fill)
        pdf.cell(col_w[6], 6, safe_str(max_disp), 1, 0, 'C', fill)

        if surplus_val is None:
            pdf.set_text_color(100, 116, 139)
        elif surplus_val >= 0:
            pdf.set_text_color(5, 150, 105)
        else:
            pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[7], 6, safe_str(surplus_disp), 1, 0, 'R', fill)
        pdf.set_text_color(0, 0, 0)

        if status == "PASS":
            pdf.set_text_color(5, 150, 105)
        else:
            pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[8], 6, status, 1, 1, 'C', fill)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(2)
    pdf.set_font("Arial", "I", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, safe_str(
        "Surplus/(Dfct): +value = excess collateral above requirement  |  (value) = collateral shortfall"
    ), 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)

    pdf_data = pdf.output(dest='S')
    if isinstance(pdf_data, str):
        return pdf_data.encode('latin-1')
    return bytes(pdf_data)


# ==========================================
# 📐 SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("## 🏦 LTV Engine")

    st.markdown(
        f"<div style='background:rgba(255,255,255,0.1); border-radius:8px; "
        f"padding:0.4rem 0.85rem; font-size:0.78rem; color:#c7d2fe; margin-bottom:0.25rem;'>"
        f"👤 <b>{st.session_state['auth_username']}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("🚪 Sign Out", type="primary"):
        st.session_state["authenticated"] = False
        st.session_state["auth_username"] = ""
        st.session_state["_login_error"] = ""
        st.rerun()

    st.markdown("---")

    # ── Step 1: Add Properties
    st.markdown("### 📍 Step 1 — Add Properties")

    sb_plot = st.text_input(
        "Property Reference",
        placeholder="e.g. Plot No. 42-B, Sector 7",
        key="sb_plot"
    )
    sb_owner = st.text_input(
        "Owner Name",
        placeholder="e.g. Ramesh Kumar Sharma",
        key="sb_owner"
    )
    sb_fmv = st.number_input(
        "Fair Market Value (Rs.)",
        min_value=0.0, step=50000.0, key="sb_fmv_amt"
    )

    if st.button("➕ Add Property", type="primary"):
        if sb_fmv <= 0:
            st.error("FMV must be > 0")
        elif not sb_plot.strip():
            st.error("Enter a property reference")
        else:
            fid = _next_fmv_id()
            st.session_state.fmv_sources.append({
                "id": fid,
                "Plot": sb_plot.strip(),
                "Owner": sb_owner.strip(),
                "Amount": sb_fmv,
            })
            st.success(f"✅ Added: {sb_plot.strip()}")
            st.rerun()

    if st.session_state.fmv_sources:
        assigned_in_use = _get_assigned_in_use()
        total_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources)
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.08); border-radius:8px; "
            f"padding:0.5rem 0.85rem; margin:0.4rem 0; font-size:0.82rem;'>"
            f"💰 Total FMV: <b>Rs. {total_fmv_all:,.0f}</b> &nbsp;·&nbsp; "
            f"📦 {len(st.session_state.fmv_sources)} properties</div>",
            unsafe_allow_html=True
        )
        for src in st.session_state.fmv_sources:
            src_id = src.get('id', '?')
            is_used = src_id in assigned_in_use
            col_a, col_b = st.columns([5, 1])
            with col_a:
                owner_txt = src.get('Owner', '') or ''
                owner_line = f"<br>&nbsp;&nbsp;<span style='color:#a5b4fc;'>{owner_txt}</span>" if owner_txt else ""
                st.markdown(
                    f"<div style='font-size:0.78rem; color:#c7d2fe; padding:0.2rem 0;'>"
                    f"{'🔒' if is_used else '🌊'} <b>{src.get('Plot','')}</b>"
                    f"{owner_line}"
                    f"<br>&nbsp;&nbsp;Rs. {src.get('Amount',0):,.0f}</div>",
                    unsafe_allow_html=True
                )
            with col_b:
                if st.button("🗑", key=f"del_fmv_{src_id}"):
                    st.session_state.fmv_sources = [
                        s for s in st.session_state.fmv_sources
                        if s.get('id') != src_id
                    ]
                    for loan in st.session_state.loans:
                        asgn = loan.get('assigned_collateral_ids', [])
                        if src_id in asgn:
                            asgn.remove(src_id)
                    st.rerun()

    st.markdown("---")

    # ── Step 2: Add Loan Facility
    st.markdown("### 📋 Step 2 — Add Loan Facility")
    policy_dict = get_policy_dict()
    loan_type_list = list(policy_dict.keys())

    if loan_type_list:
        l_type = st.selectbox("Facility Type", loan_type_list, key="sb_loan_type")
        l_amt = st.number_input(
            "Principal Amount (Rs.)",
            step=10000.0, min_value=0.0, key="sb_loan_principal"
        )
        max_ltv_sel = policy_dict.get(l_type)
        selected_colls = []
        coll_mode = "pool"

        if max_ltv_sel is not None:
            use_dedicated = st.checkbox(
                "🔒 Assign dedicated collateral(s)?",
                value=False, key="sb_use_dedicated",
                help=(
                    "Checked → link specific properties exclusively to this loan.\n\n"
                    "Unchecked → loan draws from the shared waterfall pool."
                )
            )
            coll_mode = "assigned" if use_dedicated else "pool"

            if use_dedicated:
                if st.session_state.fmv_sources:
                    already_assigned = _get_assigned_in_use()
                    coll_options = {}
                    for s in st.session_state.fmv_sources:
                        sid = s.get('id')
                        base = f"{s.get('Plot','?')} — Rs.{s.get('Amount',0):,.0f}"
                        label = (
                            f"⚠️ {base} [in use]"
                            if sid in already_assigned else f"✅ {base}"
                        )
                        coll_options[label] = sid
                    sel_labels = st.multiselect(
                        "Select Collateral(s)",
                        options=list(coll_options.keys()),
                        key="sb_sel_colls"
                    )
                    selected_colls = [coll_options[lbl] for lbl in sel_labels]
                    overlap = [c for c in selected_colls if c in already_assigned]
                    if overlap:
                        st.warning("⚠️ Selected property already assigned — FMV will be split proportionally.")
                else:
                    st.warning("⚠️ Add properties first (Step 1)")

        if max_ltv_sel is None:
            st.markdown(
                "<div style='background:rgba(245,158,11,0.15); border-left:3px solid #f59e0b; "
                "padding:0.4rem 0.75rem; border-radius:6px; font-size:0.78rem; color:#fde68a;'>"
                "⚡ Unsecured — no collateral required</div>",
                unsafe_allow_html=True
            )

        if st.button("Add to Portfolio", type="primary"):
            if l_amt <= 0:
                st.error("Principal must be > 0")
            elif coll_mode == "assigned" and not selected_colls:
                st.error("Select at least one property for dedicated mode")
            else:
                lid = st.session_state.loan_id_counter
                st.session_state.loan_id_counter += 1
                st.session_state.loans.append({
                    "Loan Type": l_type, "Principal": l_amt, "_loan_id": lid,
                    "collateral_mode": coll_mode, "assigned_collateral_ids": selected_colls,
                })
                mode_label = "🔒 Dedicated" if coll_mode == "assigned" else "🌊 Pool"
                st.success(f"✅ Added {l_type} ({mode_label})")
                st.rerun()

    if st.session_state.loans:
        st.markdown("---")
        st.markdown("**Portfolio**")
        for loan in st.session_state.loans:
            mode_icon = {"pool": "🌊", "assigned": "🔒"}.get(
                loan.get('collateral_mode', 'pool'), "🌊"
            )
            st.markdown(
                f"<div style='font-size:0.76rem; color:#c7d2fe; padding:0.12rem 0;'>"
                f"{mode_icon} {loan['Loan Type']} — Rs. {loan['Principal']:,.0f}</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    if st.button("🔄 Reset Everything", type="primary"):
        st.session_state.loans = []
        st.session_state.fmv_sources = []
        st.session_state.ltv_policy = copy.deepcopy(DEFAULT_LTV_POLICY)
        st.session_state.loan_id_counter = 0
        st.session_state.fmv_id_counter = 0
        for k in ['generated_pdf', 'generated_pdf_name']:
            st.session_state.pop(k, None)
        st.rerun()


# ==========================================
# 🖥️ MAIN AREA
# ==========================================
st.title("🏦 LTV Analysis Engine")
st.markdown(
    "Multi-collateral LTV — assign dedicated collateral to loans "
    "or let them draw from the shared waterfall pool."
)

# ==========================================
# 🏠 LANDING PAGE
# ==========================================
if not st.session_state.loans:
    st.markdown("""
    <div class="landing-wrap">
      <div class="landing-hero">
        <div class="landing-hero-icon">🏦</div>
        <div class="landing-hero-title">LTV Analysis Engine</div>
        <div class="landing-hero-sub">
          Institutional-grade Loan-to-Value analysis with multi-collateral
          waterfall allocation, dedicated assignment, surplus/shortfall reporting,
          and one-click PDF export.
        </div>
        <div class="landing-badge-row">
          <span class="landing-badge">✅ Multi-Collateral</span>
          <span class="landing-badge">🌊 Waterfall Pool</span>
          <span class="landing-badge">🔒 Dedicated Assignment</span>
          <span class="landing-badge">📊 Surplus &amp; Shortfall</span>
          <span class="landing-badge">📄 PDF Export</span>
        </div>
      </div>

      <div class="steps-grid">
        <div class="step-card">
          <div class="step-num">1</div>
          <div class="step-title">Add Properties</div>
          <div class="step-desc">Enter each collateral property with owner name and Fair Market Value. Properties can float in the shared waterfall pool or be locked to a specific loan.</div>
        </div>
        <div class="step-card">
          <div class="step-num">2</div>
          <div class="step-title">Add Loan Facilities</div>
          <div class="step-desc">Select a facility type and principal amount. Choose <b>Shared Pool</b> (waterfall priority) or <b>Dedicated Assignment</b> to link specific properties to a loan.</div>
        </div>
        <div class="step-card">
          <div class="step-num">3</div>
          <div class="step-title">Analyse &amp; Export</div>
          <div class="step-desc">Review per-facility LTV%, surplus or shortfall per loan, the aggregate portfolio LTV, and download a professional PDF report instantly.</div>
        </div>
      </div>

      <div class="feature-grid">
        <div class="feature-pill">
          <div class="feature-icon">🧮</div>
          <div>
            <div class="feature-text">Waterfall Allocation Engine</div>
            <div class="feature-sub">50% LTV facilities funded first — stricter loans get priority access to the pool</div>
          </div>
        </div>
        <div class="feature-pill">
          <div class="feature-icon">🔒</div>
          <div>
            <div class="feature-text">Dedicated Collateral Assignment</div>
            <div class="feature-sub">Pin specific properties to individual facilities; FMV split proportionally if shared</div>
          </div>
        </div>
        <div class="feature-pill">
          <div class="feature-icon">📊</div>
          <div>
            <div class="feature-text">Surplus &amp; Shortfall</div>
            <div class="feature-sub">Per-facility excess collateral or deficit shown on screen and in the PDF report</div>
          </div>
        </div>
        <div class="feature-pill">
          <div class="feature-icon">👤</div>
          <div>
            <div class="feature-text">Property Owner Tracking</div>
            <div class="feature-sub">Owner name recorded per property and printed on every PDF report</div>
          </div>
        </div>
      </div>

      <div class="landing-cta">
        <div class="landing-cta-title">👈 Ready to get started?</div>
        <div class="landing-cta-sub">
          Use the sidebar — add your first property in <b>Step 1</b>,
          then add a loan facility in <b>Step 2</b>.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.fmv_sources:
    st.warning("⚠️ Add at least one property/FMV source in the sidebar (Step 1).")
    st.stop()

# ── Run engine
results, summary = run_portfolio_ltv(
    st.session_state.loans,
    st.session_state.fmv_sources,
)
total_fmv = summary['total_fmv']
total_exposure = summary['total_exposure']
total_secured_principal = summary['total_secured_principal']
total_alloc_fmv = summary['total_alloc_fmv']
wtd_ltv = summary['wtd_ltv']
aggregate_ltv = summary['aggregate_ltv']
overall_pass = summary['overall_pass']

# ── KPI Row
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total Exposure</div>
        <div class='metric-value'>Rs.{total_exposure:,.0f}</div>
        <div class='metric-sub' style='color:#64748b;'>{len(st.session_state.loans)} facilities</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total FMV</div>
        <div class='metric-value'>Rs.{total_fmv:,.0f}</div>
        <div class='metric-sub delta-pos'>{len(st.session_state.fmv_sources)} properties</div>
    </div>""", unsafe_allow_html=True)
with k3:
    gc = "gauge-ok" if wtd_ltv <= 50 else ("gauge-warn" if wtd_ltv <= 65 else "gauge-fail")
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Weighted Avg LTV%</div>
        <div class='metric-value'>{wtd_ltv:.2f}%</div>
        <div class='ltv-gauge-wrap'><div class='{gc}' style='width:{min(wtd_ltv,100):.1f}%'></div></div>
    </div>""", unsafe_allow_html=True)
with k4:
    agc = "gauge-ok" if aggregate_ltv <= 50 else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    st.markdown(f"""<div class='aggregate-card'>
        <div class='aggregate-label'>Aggregate LTV%</div>
        <div class='aggregate-value'>{aggregate_ltv:.2f}%</div>
        <div class='aggregate-sub'>Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
        <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
            <div class='{agc}' style='width:{min(aggregate_ltv,100):.1f}%'></div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Status Banner
if overall_pass:
    st.markdown(
        "<div class='status-banner status-pass'>✅ PORTFOLIO APPROVED — All Facilities Within LTV Limits</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='status-banner status-fail'>⚠️ PORTFOLIO DECLINED — One or More Facilities Exceed Maximum LTV</div>",
        unsafe_allow_html=True
    )

# ==========================================
# 🏠 PROPERTY INFORMATION SECTION
# ==========================================
st.markdown("### 🏠 Property Information")

assigned_coll_ids  = summary['assigned_collateral_ids']
pool_coll_ids      = summary['pool_collateral_ids']
collateral_usage   = summary['collateral_usage']

# Build a lookup: collateral id → list of loan names that use it
cid_to_loan_names = {}
for loan in st.session_state.loans:
    if loan.get('collateral_mode') == 'assigned':
        for cid in loan.get('assigned_collateral_ids', []):
            cid_to_loan_names.setdefault(cid, []).append(
                f"{loan['Loan Type']} (Rs.{loan['Principal']:,.0f})"
            )

prop_rows = []
for src in st.session_state.fmv_sources:
    sid        = src.get('id')
    is_assigned = sid in assigned_coll_ids
    ctype      = "🔒 Assigned" if is_assigned else "🌊 Pool"
    usage_text = ""
    if is_assigned and sid in cid_to_loan_names:
        usage_text = "  ·  Used by: " + ", ".join(cid_to_loan_names[sid])
    prop_rows.append({
        "Property Reference": src.get('Plot', ''),
        "Owner": src.get('Owner', '—') or '—',
        "FMV (Rs.)": f"Rs. {src.get('Amount', 0):,.0f}",
        "Type": ctype,
        "Linked To": ", ".join(cid_to_loan_names.get(sid, [])) if is_assigned else "Shared Pool",
    })

if prop_rows:
    prop_df = pd.DataFrame(prop_rows)
    st.dataframe(prop_df, hide_index=True, use_container_width=True)

    # ── Summary pills below the table
    total_pool_fmv     = summary['pool_fmv']
    total_assigned_fmv = sum(
        s['Amount'] for s in st.session_state.fmv_sources
        if s.get('id') in assigned_coll_ids
    )
    n_pool     = len(pool_coll_ids)
    n_assigned = len(assigned_coll_ids)

    st.markdown(
        f"""
        <div style='display:flex; gap:0.75rem; flex-wrap:wrap; margin-top:0.5rem;'>
          <div style='background:#dbeafe; border:1px solid #93c5fd; border-radius:10px;
                      padding:0.5rem 1rem; font-size:0.82rem; color:#1d4ed8; font-weight:600;'>
            🌊 Pool Properties: <b>{n_pool}</b> &nbsp;·&nbsp; FMV: <b>Rs. {total_pool_fmv:,.0f}</b>
          </div>
          <div style='background:#fef3c7; border:1px solid #fcd34d; border-radius:10px;
                      padding:0.5rem 1rem; font-size:0.82rem; color:#92400e; font-weight:600;'>
            🔒 Assigned Properties: <b>{n_assigned}</b> &nbsp;·&nbsp; FMV: <b>Rs. {total_assigned_fmv:,.0f}</b>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Portfolio LTV Table
st.markdown("### 📋 Portfolio LTV Breakdown")


def display_sort_key(r):
    m = r.get('Max LTV%')
    if m is None:
        return (2, 0)
    return (0 if m <= 50 else 1, -(r.get('Principal', 0)))


sorted_display = sorted(results, key=display_sort_key)
disp_rows = []

for r in sorted_display:
    is_unsec = r['Is_Unsecured']
    ltv_val  = r.get('LTV%')
    max_ltv  = r.get('Max LTV%')
    mode     = r.get('Collateral_Mode', 'pool')
    coll_names = r.get('Collateral_Names', [])
    mode_disp  = {"pool": "🌊 Pool", "assigned": "🔒 Assigned"}.get(mode, "🌊 Pool")
    coll_disp  = ", ".join(coll_names) if coll_names else ("Pool" if not is_unsec else "—")

    if is_unsec or max_ltv is None:
        surplus_disp = "N/A"
    else:
        req_fmv    = r['Principal'] / (max_ltv / 100.0)
        actual_fmv = r.get('Total FMV', 0.0)
        sv         = actual_fmv - req_fmv
        surplus_disp = f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"

    disp_rows.append({
        "Facility":            r['Loan Type'],
        "Mode":                mode_disp,
        "Collateral(s)":       coll_disp,
        "Principal":           f"Rs. {r['Principal']:,.0f}",
        "Assigned FMV":        "N/A" if is_unsec else f"Rs. {r['Assigned FMV']:,.0f}",
        "Pool FMV":            "N/A" if is_unsec else f"Rs. {r['Pool FMV']:,.0f}",
        "Total FMV":           "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
        "LTV%":                "N/A" if (is_unsec or ltv_val is None) else f"{ltv_val:.2f}%",
        "Max LTV":             "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
        "Surplus/(Shortfall)": surplus_disp,
        "Status":              "✅ PASS" if r['Pass_Status'] else "❌ FAIL",
    })

disp_rows.append({
    "Facility":            "── AGGREGATE ──",
    "Mode":                "—",
    "Collateral(s)":       "All",
    "Principal":           f"Rs. {total_secured_principal:,.0f}",
    "Assigned FMV":        "—",
    "Pool FMV":            "—",
    "Total FMV":           f"Rs. {total_fmv:,.0f}",
    "LTV%":                f"{aggregate_ltv:.2f}%",
    "Max LTV":             "—",
    "Surplus/(Shortfall)": "—",
    "Status":              "✅ PASS" if aggregate_ltv <= 70 else "❌ FAIL",
})
st.dataframe(pd.DataFrame(disp_rows), hide_index=True, use_container_width=True)

# ==========================================
# 📊 LTV VISUAL SUMMARY WITH SURPLUS/SHORTFALL
# ==========================================
st.markdown("### 📊 LTV Visual Summary")
secured_disp = [r for r in sorted_display if not r['Is_Unsecured']]

if secured_disp:
    num_cols = min(len(secured_disp) + 1, 4)
    bar_cols = st.columns(num_cols)

    for i, row in enumerate(secured_disp):
        col_idx = i % num_cols
        ltv     = row['LTV%'] if row['LTV%'] is not None else 0
        max_ltv = row['Max LTV%'] or 100
        pct_of_max = min((ltv / max_ltv) * 100, 100)

        fill_cls = (
            "gauge-ok"   if ltv <= max_ltv * 0.8
            else "gauge-warn" if ltv <= max_ltv
            else "gauge-fail"
        )
        s_color  = "#059669" if row['Pass_Status'] else "#dc2626"
        mode     = row.get('Collateral_Mode', 'pool')
        mode_badge = {"pool": "🌊 Pool", "assigned": "🔒 Assigned"}.get(mode, "🌊 Pool")
        coll_names = row.get('Collateral_Names', [])
        coll_text  = (
            ", ".join(coll_names[:2]) + ("..." if len(coll_names) > 2 else "")
            if coll_names else "Pool"
        )

        # ── Surplus / Shortfall for this loan
        req_fmv_card    = row['Principal'] / (max_ltv / 100.0)
        actual_fmv_card = row.get('Total FMV', 0.0)
        sv_card         = actual_fmv_card - req_fmv_card
        if sv_card >= 0:
            surplus_html = (
                f"<span class='surplus-badge surplus-pos'>"
                f"✅ Surplus Rs. {sv_card:,.0f}</span>"
            )
        else:
            surplus_html = (
                f"<span class='surplus-badge surplus-neg'>"
                f"⚠️ Short Rs. {abs(sv_card):,.0f}</span>"
            )

        with bar_cols[col_idx]:
            st.markdown(f"""
            <div style='background:white; border:1px solid #ddd6fe; border-radius:12px;
                        padding:1rem; margin-bottom:0.75rem;'>
                <div style='display:flex; justify-content:space-between; margin-bottom:0.3rem;'>
                    <div style='font-size:0.75rem; font-weight:700; color:#1e1b4b;'>{row['Loan Type']}</div>
                    <div style='font-size:0.68rem; color:#64748b;'>{mode_badge}</div>
                </div>
                <div style='font-size:0.68rem; color:#94a3b8; margin-bottom:0.4rem;'>🏠 {coll_text}</div>
                <div style='font-size:1.5rem; font-weight:700; color:{s_color};
                            font-family:DM Mono,monospace;'>{ltv:.2f}%</div>
                <div style='font-size:0.72rem; color:#64748b;'>
                    Max: {max_ltv:.0f}% &nbsp;·&nbsp; FMV: Rs.{row['Total FMV']:,.0f}
                </div>
                {surplus_html}
                <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
                    <div class='{fill_cls}' style='width:{pct_of_max:.1f}%'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Aggregate card
    agg_col_idx  = len(secured_disp) % num_cols
    agg_fill_cls = (
        "gauge-ok"   if aggregate_ltv <= 50
        else "gauge-warn" if aggregate_ltv <= 65
        else "gauge-fail"
    )
    agg_color = "#059669" if aggregate_ltv <= 70 else "#dc2626"

    with bar_cols[agg_col_idx]:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);
                    border:1px solid #4338ca; border-radius:12px;
                    padding:1rem; margin-bottom:0.75rem;'>
            <div style='font-size:0.7rem; font-weight:700; color:#a5b4fc;
                        text-transform:uppercase; margin-bottom:0.3rem;'>AGGREGATE</div>
            <div style='font-size:1.5rem; font-weight:700; color:{agg_color};
                        font-family:DM Mono,monospace;'>{aggregate_ltv:.2f}%</div>
            <div style='font-size:0.74rem; color:#c7d2fe;'>
                Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}
            </div>
            <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
                <div class='{agg_fill_cls}' style='width:{min(aggregate_ltv,100):.1f}%'></div>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("No secured facilities in portfolio.")

# ── Loan Management
with st.expander("⚙️ Manage Portfolio — Remove Loans", expanded=False):
    if not st.session_state.loans:
        st.info("No loans added yet.")
    else:
        for loan in st.session_state.loans:
            lc1, lc2, lc3 = st.columns([3, 2, 1])
            mode_icon = {"pool": "🌊", "assigned": "🔒"}.get(
                loan.get('collateral_mode', 'pool'), "🌊"
            )
            with lc1:
                st.markdown(f"**{mode_icon} {loan['Loan Type']}**  Rs. {loan['Principal']:,.0f}")
            with lc2:
                cnames = _get_collateral_names(
                    loan.get('assigned_collateral_ids', []),
                    st.session_state.fmv_sources
                )
                st.markdown(
                    f"<span style='font-size:0.8rem; color:#64748b;'>"
                    f"{'  |  '.join(cnames) if cnames else 'Pool'}</span>",
                    unsafe_allow_html=True
                )
            with lc3:
                if st.button("Remove", key=f"rm_loan_{loan['_loan_id']}"):
                    st.session_state.loans = [
                        l for l in st.session_state.loans
                        if l['_loan_id'] != loan['_loan_id']
                    ]
                    st.rerun()

# ── PDF Export
with st.expander("📄 Generate PDF Report", expanded=True):
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
                        st.session_state['generated_pdf'] = pdf_bytes
                        st.session_state['generated_pdf_name'] = (
                            f"LTV_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

    if 'generated_pdf' in st.session_state:
        st.markdown("---")
        st.success("✅ Report ready.")
        st.download_button(
            label="⬇️ Download PDF",
            data=st.session_state['generated_pdf'],
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
        )
