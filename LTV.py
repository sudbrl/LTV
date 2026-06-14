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
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        #MainMenu, footer, header { visibility: hidden; }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: #030D1C !important;
            background-image:
                radial-gradient(circle at 20% 50%, rgba(26, 58, 92, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(200, 150, 43, 0.06) 0%, transparent 40%),
                radial-gradient(ellipse at 50% 100%, rgba(11, 25, 41, 0.8) 0%, transparent 60%) !important;
        }

        /* Dot grid overlay */
        .stApp::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: radial-gradient(circle, rgba(26, 58, 92, 0.35) 1px, transparent 1px);
            background-size: 28px 28px;
            pointer-events: none;
            z-index: 0;
        }

        .block-container {
            max-width: 460px !important;
            padding-top: 6vh !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            position: relative;
            z-index: 1;
        }

        /* ── LOGIN CARD */
        .login-shell {
            background: linear-gradient(160deg, #0B1929 0%, #0A1522 100%);
            border-radius: 16px;
            border: 1px solid #1A3A5C;
            overflow: hidden;
            box-shadow:
                0 0 0 1px rgba(200,150,43,0.08),
                0 24px 64px rgba(0,0,0,0.7),
                0 4px 24px rgba(0,0,0,0.5);
        }

        .login-gold-bar {
            height: 3px;
            background: linear-gradient(90deg, transparent 0%, #C8962B 30%, #E8C060 60%, #C8962B 80%, transparent 100%);
            box-shadow: 0 0 16px rgba(200,150,43,0.6), 0 0 32px rgba(200,150,43,0.2);
        }

        .login-body {
            padding: 2rem 2rem 1.75rem;
        }

        .login-brand {
            text-align: center;
            margin-bottom: 1.75rem;
        }

        .login-seal {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 52px; height: 52px;
            background: linear-gradient(135deg, #1A3A5C, #0D2237);
            border: 1px solid #C8962B;
            border-radius: 12px;
            font-size: 1.5rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 0 20px rgba(200,150,43,0.2);
        }

        .login-product-name {
            font-family: 'Sora', sans-serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: #DCE8F8;
            letter-spacing: -0.01em;
            margin-bottom: 0.2rem;
        }

        .login-division {
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #C8962B;
        }

        .login-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #1A3A5C, transparent);
            margin: 1.25rem 0;
        }

        .login-field-label {
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #6A8FAF;
            margin-bottom: 0.35rem;
            display: block;
        }

        div[data-testid="stTextInput"] label { display: none !important; }

        div[data-testid="stTextInput"] > div > div > input {
            background: #071426 !important;
            border: 1px solid #1A3A5C !important;
            border-radius: 8px !important;
            color: #DCE8F8 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.9rem !important;
            padding: 0.65rem 0.9rem !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: #C8962B !important;
            box-shadow: 0 0 0 3px rgba(200,150,43,0.12), inset 0 0 0 1px rgba(200,150,43,0.2) !important;
            background: #081830 !important;
        }

        div[data-testid="stTextInput"] > div > div > input::placeholder {
            color: #2D5070 !important;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #C8962B 0%, #A87820 100%) !important;
            color: #030D1C !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'Sora', sans-serif !important;
            font-weight: 700 !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.04em !important;
            padding: 0.65rem !important;
            width: 100% !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 16px rgba(200,150,43,0.3) !important;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #D9A83C 0%, #C8962B 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 24px rgba(200,150,43,0.45) !important;
        }

        .login-err {
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            border-radius: 8px;
            color: #FCA5A5;
            font-size: 0.8rem;
            font-weight: 500;
            line-height: 1.5;
            padding: 0.7rem 0.9rem;
            margin-top: 0.85rem;
        }

        .login-footer {
            text-align: center;
            font-size: 0.65rem;
            color: #2D5070;
            padding: 0.9rem 2rem;
            border-top: 1px solid rgba(26,58,92,0.5);
            letter-spacing: 0.06em;
        }

        div[data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    st.markdown('<div class="login-shell"><div class="login-gold-bar"></div><div class="login-body">', unsafe_allow_html=True)

    st.markdown("""
        <div class="login-brand">
            <div class="login-seal">🏦</div>
            <div class="login-product-name">LTV Analysis Engine</div>
            <div class="login-division">Credit Risk · Secure Access</div>
        </div>
        <div class="login-divider"></div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="login-field-label">Username</span>', unsafe_allow_html=True)
    username = st.text_input(
        label="username", placeholder="Enter your username", key="_login_u",
        label_visibility="collapsed", autocomplete="username",
    )

    st.markdown('<span class="login-field-label" style="margin-top:0.75rem; display:block;">Password</span>', unsafe_allow_html=True)
    password = st.text_input(
        label="password", placeholder="Enter your password", type="password",
        key="_login_p", label_visibility="collapsed", autocomplete="current-password",
    )

    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
    clicked = st.button("Sign In →", key="_login_btn", use_container_width=True)

    if clicked:
        u = str(username).strip()
        p = str(password).strip()
        if not u:
            st.session_state["_login_error"] = "⚠️ Username is required."
            st.rerun()
        elif not p:
            st.session_state["_login_error"] = "⚠️ Password is required."
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
                    f"<b>Username and password appear swapped.</b><br>"
                    f"Try username <code>admin</code> with password <code>{u}</code>."
                )
            else:
                error_msg = "Invalid credentials. Please check your username and password."
            st.session_state["_login_error"] = error_msg
            st.rerun()

    err = st.session_state.get("_login_error", "")
    if err:
        st.markdown(f'<div class="login-err">{err}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close login-body
    st.markdown("""
        <div class="login-footer">
            🔐 &nbsp; SECURED CONNECTION &nbsp;·&nbsp; AUTHORISED PERSONNEL ONLY
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close login-shell


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
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #DCE8F8;
        letter-spacing: -0.005em;
    }

    /* ── Page background */
    .main {
        background: #040E1F !important;
        background-image:
            radial-gradient(ellipse at 0% 0%, rgba(26,58,92,0.12) 0%, transparent 40%),
            radial-gradient(ellipse at 100% 100%, rgba(200,150,43,0.04) 0%, transparent 40%) !important;
    }

    .block-container {
        max-width: 97% !important;
        padding-top: 1.25rem !important;
    }

    /* ── All number/data displays */
    .mono { font-family: 'JetBrains Mono', monospace; }

    /* ── Generic inputs */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        background: #071426 !important;
        border: 1px solid #1A3A5C !important;
        border-radius: 8px !important;
        color: #DCE8F8 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 0.85rem !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #C8962B !important;
        box-shadow: 0 0 0 3px rgba(200,150,43,0.12) !important;
        background: #081830 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #2D5070 !important;
    }

    /* ── Selectbox */
    div[data-baseweb="select"] > div {
        background: #071426 !important;
        border: 1px solid #1A3A5C !important;
        border-radius: 8px !important;
        color: #DCE8F8 !important;
    }

    /* ── Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #040E1F 0%, #060F1C 100%) !important;
        border-right: 1px solid #1A3A5C;
    }
    [data-testid="stSidebar"] * { color: #B8CDE0 !important; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: #DCE8F8 !important; }

    [data-testid="stSidebar"] div[data-testid="stTextInput"] input,
    [data-testid="stSidebar"] div[data-testid="stNumberInput"] input {
        background: #081628 !important;
        border-color: #1E3F6A !important;
        color: #DCE8F8 !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #081628 !important;
        border-color: #1E3F6A !important;
        color: #DCE8F8 !important;
    }

    /* ── Primary button */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #C8962B 0%, #A87820 100%) !important;
        border: none !important;
        color: #030D1C !important;
        border-radius: 8px !important;
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 12px rgba(200,150,43,0.25) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #D9A83C 0%, #C8962B 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(200,150,43,0.4) !important;
    }

    /* ── Dataframe / tables */
    [data-testid="stDataFrame"] {
        border-radius: 10px !important;
        overflow: hidden;
        border: 1px solid #1A3A5C !important;
    }

    /* ── Expanders */
    [data-testid="stExpander"] {
        background: #060F1C !important;
        border: 1px solid #1A3A5C !important;
        border-radius: 10px !important;
    }

    /* ── Warnings and info boxes */
    [data-testid="stAlert"] {
        background: rgba(26,58,92,0.3) !important;
        border-color: #1A3A5C !important;
        color: #B8CDE0 !important;
        border-radius: 8px !important;
    }

    /* ── Checkboxes */
    [data-testid="stCheckbox"] { color: #B8CDE0 !important; }

    /* ── Multiselect */
    span[data-baseweb="tag"] {
        background: rgba(200,150,43,0.15) !important;
        border: 1px solid rgba(200,150,43,0.3) !important;
        border-radius: 5px !important;
    }

    /* ── Page title */
    h1 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        color: #DCE8F8 !important;
        letter-spacing: -0.02em !important;
    }
    h2, h3 {
        font-family: 'Sora', sans-serif !important;
        font-weight: 600 !important;
        color: #C8D9EE !important;
    }

    /* ── Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #071426; }
    ::-webkit-scrollbar-thumb { background: #1E3F6A; border-radius: 3px; }

    /* ────────────────────────────────────────
       COMPONENT CLASSES
    ──────────────────────────────────────── */

    /* KPI cards */
    .kpi-card {
        background: linear-gradient(145deg, #0B1929 0%, #0A1724 100%);
        border: 1px solid #1A3A5C;
        border-radius: 12px;
        padding: 1.1rem 1.3rem 1rem;
        position: relative;
        overflow: hidden;
        transition: border-color 0.2s;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C8962B, transparent);
        opacity: 0.5;
    }
    .kpi-card:hover { border-color: #2A5080; }

    .kpi-label {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #6A8FAF;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 600;
        color: #DCE8F8;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        font-size: 0.72rem;
        font-weight: 500;
        margin-top: 0.25rem;
        color: #4A6A8F;
    }
    .kpi-pos { color: #10C980 !important; }
    .kpi-neg { color: #EF4444 !important; }

    /* Aggregate KPI (gold highlighted) */
    .kpi-card-gold {
        background: linear-gradient(145deg, #0F1E0A 0%, #0A1908 100%);
        border: 1px solid #C8962B;
        border-radius: 12px;
        padding: 1.1rem 1.3rem 1rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 24px rgba(200,150,43,0.1);
    }
    .kpi-card-gold::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C8962B 40%, #F0C860 60%, #C8962B, transparent);
        box-shadow: 0 0 8px rgba(200,150,43,0.8);
    }
    .kpi-label-gold {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #C8962B;
        margin-bottom: 0.4rem;
    }
    .kpi-value-gold {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 600;
        color: #E8B84B;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-sub-gold {
        font-size: 0.72rem;
        color: #8A7030;
        margin-top: 0.25rem;
    }

    /* Gauge bars */
    .gauge-track {
        height: 5px;
        background: #0D2035;
        border-radius: 99px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    .gauge-fill-ok   { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #0A8A60, #10C980); }
    .gauge-fill-warn { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #B45309, #F59E0B); }
    .gauge-fill-fail { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #991B1B, #EF4444); }

    /* Status banners */
    .status-pass {
        background: rgba(16,201,128,0.06);
        border: 1px solid rgba(16,201,128,0.25);
        border-left: 4px solid #10C980;
        border-radius: 10px;
        color: #6EE7B7;
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.01em;
        padding: 0.85rem 1.25rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .status-fail {
        background: rgba(239,68,68,0.06);
        border: 1px solid rgba(239,68,68,0.25);
        border-left: 4px solid #EF4444;
        border-radius: 10px;
        color: #FCA5A5;
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.01em;
        padding: 0.85rem 1.25rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    /* Section header divider */
    .section-head {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.5rem 0 0.85rem;
    }
    .section-head-label {
        font-family: 'Sora', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #C8D9EE;
        white-space: nowrap;
    }
    .section-head-line {
        height: 1px;
        flex: 1;
        background: linear-gradient(90deg, #1A3A5C, transparent);
    }

    /* Visual summary cards */
    .vis-card {
        background: #0B1929;
        border: 1px solid #1A3A5C;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.65rem;
        transition: border-color 0.2s;
    }
    .vis-card:hover { border-color: #2A5080; }
    .vis-card-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #C8D9EE;
        margin-bottom: 0.1rem;
    }
    .vis-card-mode {
        font-size: 0.63rem;
        color: #4A6A8F;
        margin-bottom: 0.5rem;
    }
    .vis-card-pct {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        line-height: 1.1;
    }
    .vis-card-meta {
        font-size: 0.68rem;
        color: #4A6A8F;
        margin-top: 0.1rem;
    }
    .surplus-ok  { background: rgba(16,201,128,0.08); border: 1px solid rgba(16,201,128,0.2); color: #6EE7B7; border-radius: 6px; padding: 0.18rem 0.55rem; font-size: 0.68rem; font-weight: 600; display: inline-block; margin-top: 0.4rem; }
    .surplus-bad { background: rgba(239,68,68,0.08);  border: 1px solid rgba(239,68,68,0.2);  color: #FCA5A5; border-radius: 6px; padding: 0.18rem 0.55rem; font-size: 0.68rem; font-weight: 600; display: inline-block; margin-top: 0.4rem; }

    /* Aggregate vis card */
    .vis-card-agg {
        background: linear-gradient(145deg, #0D1E0A, #0A1908);
        border: 1px solid rgba(200,150,43,0.3);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 0 16px rgba(200,150,43,0.06);
    }

    /* Sidebar step headers */
    .sb-step {
        font-family: 'Sora', sans-serif;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #C8962B !important;
        margin: 0.5rem 0 0.65rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sb-step-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px; height: 18px;
        background: rgba(200,150,43,0.15);
        border: 1px solid rgba(200,150,43,0.4);
        border-radius: 50%;
        font-size: 0.62rem;
        font-weight: 800;
        color: #C8962B;
    }

    .sb-divider {
        height: 1px;
        background: linear-gradient(90deg, #1A3A5C, transparent);
        margin: 0.75rem 0;
    }

    .sb-stat {
        background: rgba(200,150,43,0.06);
        border: 1px solid rgba(200,150,43,0.15);
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        font-size: 0.75rem;
        margin: 0.4rem 0;
        color: #B8CDE0 !important;
    }
    .sb-stat b { color: #C8962B !important; font-family: 'JetBrains Mono', monospace; }

    .sb-prop-row {
        background: rgba(26,58,92,0.2);
        border: 1px solid #1A3A5C;
        border-radius: 8px;
        padding: 0.45rem 0.7rem;
        margin: 0.25rem 0;
        font-size: 0.74rem;
        color: #8AAFC8 !important;
    }
    .sb-prop-name { color: #B8CDE0 !important; font-weight: 600; }

    .sb-loan-row {
        border-left: 2px solid #1E3F6A;
        padding: 0.25rem 0 0.25rem 0.65rem;
        margin: 0.15rem 0;
        font-size: 0.73rem;
        color: #6A8FAF !important;
    }

    /* Smart hint boxes */
    .hint-box {
        background: rgba(200,150,43,0.06);
        border-left: 3px solid rgba(200,150,43,0.4);
        border-radius: 0 6px 6px 0;
        padding: 0.45rem 0.65rem;
        font-size: 0.72rem;
        color: #9A7A30 !important;
        margin: 0.3rem 0 0.5rem;
        line-height: 1.5;
    }
    .hint-box b { color: #C8962B !important; font-family: 'JetBrains Mono', monospace; }

    .hint-unsec {
        background: rgba(245,158,11,0.06);
        border-left: 3px solid rgba(245,158,11,0.35);
        border-radius: 0 6px 6px 0;
        padding: 0.4rem 0.65rem;
        font-size: 0.72rem;
        color: #C88A10 !important;
        margin: 0.3rem 0;
    }

    /* Property info pill row */
    .pill-row {
        display: flex; gap: 0.65rem; flex-wrap: wrap; margin-top: 0.5rem;
    }
    .pill {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .pill-pool { background: rgba(26,58,92,0.4); border: 1px solid #1E3F6A; color: #7AB8E8; }
    .pill-asgn { background: rgba(200,150,43,0.1); border: 1px solid rgba(200,150,43,0.3); color: #C8962B; }

    /* ── LANDING PAGE */
    .lp-wrap { max-width: 1060px; margin: 0 auto; padding: 2rem 0.5rem 3rem; }

    .lp-hero {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        padding: 3.5rem 3rem 3rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #030D1C 0%, #071A2E 50%, #040E20 100%);
        border: 1px solid #1A3A5C;
        box-shadow: 0 0 80px rgba(200,150,43,0.06), 0 24px 80px rgba(0,0,0,0.5);
    }
    .lp-hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image: radial-gradient(circle, rgba(26,58,92,0.3) 1px, transparent 1px);
        background-size: 24px 24px;
        pointer-events: none;
    }
    .lp-hero::after {
        content: '';
        position: absolute;
        top: 0; left: 10%; right: 10%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #C8962B 30%, #F0C860 60%, #C8962B 80%, transparent);
        box-shadow: 0 0 20px rgba(200,150,43,0.6);
    }

    .lp-eyebrow {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #C8962B;
        margin-bottom: 0.85rem;
        position: relative;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .lp-eyebrow::before {
        content: '';
        width: 20px; height: 1px;
        background: #C8962B;
    }

    .lp-hero-title {
        font-family: 'Sora', sans-serif;
        font-size: 2.65rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 0.85rem;
        position: relative;
    }
    .lp-hero-title span {
        color: #C8962B;
    }

    .lp-hero-sub {
        font-size: 0.98rem;
        color: #6A8FAF;
        max-width: 560px;
        line-height: 1.7;
        margin-bottom: 1.75rem;
        position: relative;
    }

    .lp-tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        position: relative;
    }
    .lp-tag {
        background: rgba(26,58,92,0.5);
        border: 1px solid #1A3A5C;
        border-radius: 99px;
        padding: 0.28rem 0.85rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: #7AADC8;
        letter-spacing: 0.03em;
        backdrop-filter: blur(4px);
    }

    /* Metrics strip inside hero */
    .lp-hero-metrics {
        position: absolute;
        right: 3rem;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .lp-metric-item {
        background: rgba(26,58,92,0.3);
        border: 1px solid #1A3A5C;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        text-align: right;
        min-width: 140px;
    }
    .lp-metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.35rem;
        font-weight: 600;
        color: #C8962B;
        line-height: 1;
    }
    .lp-metric-lbl {
        font-size: 0.62rem;
        color: #4A6A8F;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }

    /* Workflow steps */
    .lp-steps {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
        position: relative;
    }

    .lp-step-card {
        background: #0B1929;
        border: 1px solid #1A3A5C;
        border-radius: 14px;
        padding: 1.5rem 1.35rem;
        transition: border-color 0.2s, transform 0.2s;
    }
    .lp-step-card:hover {
        border-color: rgba(200,150,43,0.4);
        transform: translateY(-2px);
    }

    .lp-step-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 600;
        color: #C8962B;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }
    .lp-step-icon {
        font-size: 1.5rem;
        margin-bottom: 0.6rem;
        display: block;
    }
    .lp-step-title {
        font-family: 'Sora', sans-serif;
        font-size: 0.98rem;
        font-weight: 700;
        color: #C8D9EE;
        margin-bottom: 0.45rem;
    }
    .lp-step-desc {
        font-size: 0.8rem;
        color: #4A6A8F;
        line-height: 1.6;
    }

    /* Feature grid */
    .lp-features {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .lp-feat {
        background: #0B1929;
        border: 1px solid #1A3A5C;
        border-radius: 12px;
        padding: 1.1rem;
        transition: border-color 0.2s;
    }
    .lp-feat:hover { border-color: #2A5080; }
    .lp-feat-icon { font-size: 1.2rem; margin-bottom: 0.5rem; }
    .lp-feat-title {
        font-size: 0.82rem;
        font-weight: 700;
        color: #C8D9EE;
        margin-bottom: 0.2rem;
    }
    .lp-feat-desc { font-size: 0.74rem; color: #4A6A8F; line-height: 1.5; }

    /* CTA strip */
    .lp-cta {
        background: linear-gradient(135deg, #0B1929, #0A1724);
        border: 1px solid rgba(200,150,43,0.25);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    .lp-cta-left h3 {
        font-family: 'Sora', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #DCE8F8;
        margin-bottom: 0.2rem;
    }
    .lp-cta-left p {
        font-size: 0.8rem;
        color: #4A6A8F;
        margin: 0;
    }
    .lp-cta-arrow {
        background: linear-gradient(135deg, #C8962B, #A87820);
        color: #030D1C;
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        white-space: nowrap;
        box-shadow: 0 4px 16px rgba(200,150,43,0.3);
    }

    @media (max-width: 800px) {
        .lp-steps { grid-template-columns: 1fr; }
        .lp-features { grid-template-columns: repeat(2, 1fr); }
        .lp-hero-metrics { display: none; }
        .lp-hero-title { font-size: 1.75rem; }
        .lp-cta { flex-direction: column; }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ⚙️ DEFAULT LTV POLICY
# ==========================================
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",                "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan",                   "Max LTV%": 60.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial",        "Max LTV%": 80.0,  "Unsecured": False},
    {"Loan Type": "HP Loan (Used)",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "HP Loan Commercial-EV",        "Max LTV%": 80.0,  "Unsecured": False},
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
# 💰 PROFESSIONAL OD / T-L CAP RULES
# ==========================================
PROFESSIONAL_OD_CAP = 500000.0
PROFESSIONAL_TL_CAP = 1500000.0
PROFESSIONAL_COMBINED_CAP = 1500000.0


def _check_professional_caps(l_type, l_amt, existing_loans):
    if l_type not in ("Professional OD", "Professional T/L"):
        return True, ""

    existing_od = sum(
        l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional OD"
    )
    existing_tl = sum(
        l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional T/L"
    )

    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)

    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, (
            f"Professional OD total (Rs. {new_od:,.0f}) would exceed the "
            f"individual cap of Rs. {PROFESSIONAL_OD_CAP:,.0f}."
        )

    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, (
            f"Professional T/L total (Rs. {new_tl:,.0f}) would exceed the "
            f"individual cap of Rs. {PROFESSIONAL_TL_CAP:,.0f}."
        )

    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, (
            f"Combined Professional OD + Professional T/L total "
            f"(Rs. {(new_od + new_tl):,.0f}) would exceed the combined cap "
            f"of Rs. {PROFESSIONAL_COMBINED_CAP:,.0f}."
        )

    return True, ""


# ==========================================
# 🧮 PORTFOLIO LTV ENGINE  (LOGIC UNCHANGED)
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
# 📄 PDF ENGINE  (LOGIC UNCHANGED)
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
    kv("Total Secured Exposure:", f"Rs. {total_secured_p:,.2f}")
    kv("Total Loan Exposure (All Facilities):", f"Rs. {total_exposure:,.2f}")
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
    col_align = ['L', 'R', 'R', 'R', 'R', 'C', 'C', 'R', 'C']

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

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w[0], 6, "AGGREGATE (ALL FACILITIES)", 1, 0, 'L', True)
    pdf.cell(col_w[1], 6, f"{total_exposure:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[2], 6, "-", 1, 0, 'R', True)
    pdf.cell(col_w[3], 6, "-", 1, 0, 'R', True)
    pdf.cell(col_w[4], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[5], 6, f"{aggregate_ltv:.1f}%", 1, 0, 'C', True)
    pdf.cell(col_w[6], 6, "-", 1, 0, 'C', True)
    pdf.cell(col_w[7], 6, "-", 1, 0, 'R', True)
    agg_status_pdf = "PASS" if overall_pass else "FAIL"
    pdf.cell(col_w[8], 6, agg_status_pdf, 1, 1, 'C', True)

    pdf.ln(2)
    pdf.set_font("Arial", "I", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, safe_str(
        "Surplus/(Dfct): +value = excess collateral above requirement  |  (value) = collateral shortfall"
    ), 0, 1, 'L')
    pdf.cell(0, 5, safe_str(
        "Aggregate Principal includes ALL facilities (secured + unsecured); "
        "Aggregate LTV% is computed on secured principal vs total FMV only."
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
    # ── Header
    st.markdown(f"""
        <div style="padding: 0.5rem 0 0.25rem;">
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.75rem;">
                <span style="font-size:1.3rem;">🏦</span>
                <div>
                    <div style="font-family:'Sora',sans-serif; font-size:0.88rem; font-weight:700; color:#DCE8F8 !important;">LTV Engine</div>
                    <div style="font-size:0.6rem; color:#C8962B !important; font-weight:600; letter-spacing:0.1em; text-transform:uppercase;">Credit Risk Division</div>
                </div>
            </div>
            <div style="background:rgba(200,150,43,0.08); border:1px solid rgba(200,150,43,0.2); border-radius:7px; padding:0.35rem 0.7rem; display:flex; align-items:center; justify-content:space-between;">
                <span style="font-size:0.72rem; color:#8AAFC8 !important;">👤 {st.session_state['auth_username']}</span>
                <span style="font-size:0.6rem; color:#C8962B !important; font-weight:600; letter-spacing:0.06em;">ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", type="primary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["auth_username"] = ""
        st.session_state["_login_error"] = ""
        st.rerun()

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── STEP 1: Properties
    st.markdown('<div class="sb-step"><span class="sb-step-num">1</span>Add Properties</div>', unsafe_allow_html=True)

    sb_plot = st.text_input(
        "Property Reference",
        placeholder="e.g. Plot 42-B, Sector 7, Delhi",
        key="sb_plot",
        help="Enter the legal property description or plot reference"
    )
    sb_owner = st.text_input(
        "Owner / Mortgagor Name",
        placeholder="e.g. Ramesh Kumar Sharma",
        key="sb_owner",
        help="Full name of the property owner as per title deed"
    )
    sb_fmv = st.number_input(
        "Fair Market Value (Rs.)",
        min_value=0.0, step=50000.0, key="sb_fmv_amt",
        help="Valuation amount from approved valuer report"
    )

    # Smart hint: running FMV total preview
    if sb_fmv > 0:
        current_pool = sum(s['Amount'] for s in st.session_state.fmv_sources)
        new_total = current_pool + sb_fmv
        st.markdown(
            f'<div class="hint-box">After adding: Pool total = <b>Rs. {new_total:,.0f}</b></div>',
            unsafe_allow_html=True
        )

    if st.button("➕ Add Property", type="primary", use_container_width=True):
        if sb_fmv <= 0:
            st.error("FMV must be greater than zero.")
        elif not sb_plot.strip():
            st.error("Property reference is required.")
        else:
            fid = _next_fmv_id()
            st.session_state.fmv_sources.append({
                "id": fid,
                "Plot": sb_plot.strip(),
                "Owner": sb_owner.strip(),
                "Amount": sb_fmv,
            })
            st.success(f"Property added.")
            st.rerun()

    # Property list
    if st.session_state.fmv_sources:
        assigned_in_use = _get_assigned_in_use()
        total_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources)

        st.markdown(
            f'<div class="sb-stat">💰 Total FMV &nbsp;·&nbsp; <b>Rs. {total_fmv_all:,.0f}</b>'
            f' &nbsp;·&nbsp; {len(st.session_state.fmv_sources)} properties</div>',
            unsafe_allow_html=True
        )

        for src in st.session_state.fmv_sources:
            src_id = src.get('id', '?')
            is_used = src_id in assigned_in_use
            col_a, col_b = st.columns([5, 1])
            with col_a:
                owner_txt = src.get('Owner', '') or ''
                icon = '🔒' if is_used else '🌊'
                st.markdown(
                    f'<div class="sb-prop-row">'
                    f'<span style="margin-right:0.35rem;">{icon}</span>'
                    f'<span class="sb-prop-name">{src.get("Plot","")}</span>'
                    + (f'<br><span style="font-size:0.68rem; color:#4A6A8F !important;">{owner_txt}</span>' if owner_txt else '')
                    + f'<br><span style="font-family:\'JetBrains Mono\',monospace; font-size:0.72rem; color:#C8962B !important;">Rs. {src.get("Amount",0):,.0f}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_b:
                if st.button("✕", key=f"del_fmv_{src_id}", help="Remove property"):
                    st.session_state.fmv_sources = [
                        s for s in st.session_state.fmv_sources
                        if s.get('id') != src_id
                    ]
                    for loan in st.session_state.loans:
                        asgn = loan.get('assigned_collateral_ids', [])
                        if src_id in asgn:
                            asgn.remove(src_id)
                    st.rerun()

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── STEP 2: Loan Facility
    st.markdown('<div class="sb-step"><span class="sb-step-num">2</span>Add Loan Facility</div>', unsafe_allow_html=True)

    policy_dict = get_policy_dict()
    loan_type_list = list(policy_dict.keys())

    if loan_type_list:
        l_type = st.selectbox(
            "Facility Type", loan_type_list, key="sb_loan_type",
            help="Select the credit facility type"
        )
        l_amt = st.number_input(
            "Principal Amount (Rs.)",
            step=10000.0, min_value=0.0, key="sb_loan_principal",
            help="Sanctioned or proposed loan amount"
        )

        max_ltv_sel = policy_dict.get(l_type)

        # Smart hints: show required FMV instantly
        if max_ltv_sel is not None and l_amt > 0:
            req_fmv = l_amt / (max_ltv_sel / 100.0)
            pool_avail = sum(s['Amount'] for s in st.session_state.fmv_sources)
            cover_ok = pool_avail >= req_fmv
            cover_icon = "✅" if cover_ok else "⚠️"
            st.markdown(
                f'<div class="hint-box">'
                f'Policy max: <b>{max_ltv_sel:.0f}%</b> LTV<br>'
                f'Required FMV: <b>Rs. {req_fmv:,.0f}</b><br>'
                f'{cover_icon} Pool FMV: <b>Rs. {pool_avail:,.0f}</b>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif max_ltv_sel is None:
            cap_label = ""
            if l_type == "Professional OD":
                cap_label = f"Individual cap: Rs. {PROFESSIONAL_OD_CAP:,.0f}"
            elif l_type == "Professional T/L":
                cap_label = f"Individual cap: Rs. {PROFESSIONAL_TL_CAP:,.0f}"
            st.markdown(
                f'<div class="hint-unsec">⚡ Unsecured — no collateral required'
                + (f'<br>{cap_label}' if cap_label else '') + '</div>',
                unsafe_allow_html=True
            )

        selected_colls = []
        coll_mode = "pool"

        if max_ltv_sel is not None:
            use_dedicated = st.checkbox(
                "🔒 Assign dedicated collateral(s)?",
                value=False, key="sb_use_dedicated",
                help="Uncheck to use the shared waterfall pool. Check to pin specific properties to this facility."
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
                        key="sb_sel_colls",
                        help="Properties already assigned to another loan will share FMV proportionally."
                    )
                    selected_colls = [coll_options[lbl] for lbl in sel_labels]

                    # Smart hint: show selected FMV total
                    if selected_colls:
                        sel_fmv = sum(
                            s['Amount'] for s in st.session_state.fmv_sources
                            if s.get('id') in selected_colls
                        )
                        overlap = [c for c in selected_colls if c in already_assigned]
                        if overlap:
                            st.warning("⚠️ Shared property — FMV will be split proportionally.")
                        else:
                            cover = (sel_fmv >= req_fmv) if (max_ltv_sel and l_amt > 0) else True
                            req_txt = f"Rs. {req_fmv:,.0f}" if (max_ltv_sel and l_amt > 0) else "N/A"
                            st.markdown(
                                f'<div class="hint-box">Selected FMV: <b>Rs. {sel_fmv:,.0f}</b><br>'
                                f'Required FMV: <b>{req_txt}</b> &nbsp; {"✅ Sufficient" if cover else "⚠️ Shortfall"}'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                else:
                    st.warning("⚠️ Add properties first (Step 1)")

        if st.button("Add to Portfolio", type="primary", use_container_width=True):
            if l_amt <= 0:
                st.error("Principal must be greater than zero.")
            elif coll_mode == "assigned" and not selected_colls:
                st.error("Select at least one property for dedicated mode.")
            else:
                cap_ok, cap_msg = _check_professional_caps(
                    l_type, l_amt, st.session_state.loans
                )
                if not cap_ok:
                    st.error(f"🚫 {cap_msg}")
                else:
                    lid = st.session_state.loan_id_counter
                    st.session_state.loan_id_counter += 1
                    st.session_state.loans.append({
                        "Loan Type": l_type, "Principal": l_amt, "_loan_id": lid,
                        "collateral_mode": coll_mode, "assigned_collateral_ids": selected_colls,
                    })
                    mode_label = "🔒 Dedicated" if coll_mode == "assigned" else "🌊 Pool"
                    st.success(f"Facility added ({mode_label})")
                    st.rerun()

    # Portfolio list
    if st.session_state.loans:
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        total_exp_sb = sum(l['Principal'] for l in st.session_state.loans)
        st.markdown(
            f'<div class="sb-stat">📊 Portfolio &nbsp;·&nbsp; <b>Rs. {total_exp_sb:,.0f}</b>'
            f' &nbsp;·&nbsp; {len(st.session_state.loans)} facilities</div>',
            unsafe_allow_html=True
        )
        for loan in st.session_state.loans:
            mode_icon = {"pool": "🌊", "assigned": "🔒"}.get(loan.get('collateral_mode', 'pool'), "🌊")
            st.markdown(
                f'<div class="sb-loan-row">{mode_icon} {loan["Loan Type"]}'
                f'<br><span style="font-family:\'JetBrains Mono\',monospace; font-size:0.7rem; color:#C8962B !important;">'
                f'Rs. {loan["Principal"]:,.0f}</span></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    if st.button("🔄 Reset Portfolio", type="primary", use_container_width=True):
        st.session_state.loans = []
        st.session_state.fmv_sources = []
        st.session_state.ltv_policy = copy.deepcopy(DEFAULT_LTV_POLICY)
        st.session_state.loan_id_counter = 0
        st.session_state.fmv_id_counter = 0
        for k in ['generated_pdf', 'generated_pdf_name']:
            st.session_state.pop(k, None)
        st.rerun()


# ==========================================
# 🖥️ MAIN AREA — Page header
# ==========================================
st.markdown("""
    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.1rem;">
        <div>
            <div style="font-family:'Sora',sans-serif; font-size:1.6rem; font-weight:800; color:#DCE8F8; letter-spacing:-0.03em; line-height:1.1;">
                LTV Analysis Engine
            </div>
            <div style="font-size:0.8rem; color:#4A6A8F; margin-top:0.15rem;">
                Multi-collateral portfolio — waterfall pool &amp; dedicated assignment
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


# ==========================================
# 🏠 LANDING PAGE
# ==========================================
if not st.session_state.loans:
    st.markdown("""
    <div class="lp-wrap">

      <!-- HERO -->
      <div class="lp-hero">
        <div class="lp-eyebrow">Credit Risk · Institutional Analysis</div>
        <div class="lp-hero-title">
          Institutional-Grade<br>
          <span>LTV Analysis</span>
        </div>
        <div class="lp-hero-sub">
          Precision loan-to-value assessment with multi-collateral waterfall allocation,
          dedicated assignment, and one-click audit-ready PDF reporting.
        </div>
        <div class="lp-tag-row">
          <span class="lp-tag">✦ Multi-Collateral</span>
          <span class="lp-tag">✦ Waterfall Engine</span>
          <span class="lp-tag">✦ Dedicated Assignment</span>
          <span class="lp-tag">✦ Surplus &amp; Shortfall</span>
          <span class="lp-tag">✦ PDF Export</span>
        </div>
        <!-- Floating metrics -->
        <div class="lp-hero-metrics">
          <div class="lp-metric-item">
            <div class="lp-metric-val">16</div>
            <div class="lp-metric-lbl">Facility Types</div>
          </div>
          <div class="lp-metric-item">
            <div class="lp-metric-val">50–80%</div>
            <div class="lp-metric-lbl">LTV Range</div>
          </div>
          <div class="lp-metric-item">
            <div class="lp-metric-val">∞</div>
            <div class="lp-metric-lbl">Properties</div>
          </div>
        </div>
      </div>

      <!-- WORKFLOW -->
      <div class="lp-steps">
        <div class="lp-step-card">
          <div class="lp-step-num">STEP 01</div>
          <div class="lp-step-icon">🏠</div>
          <div class="lp-step-title">Register Collateral</div>
          <div class="lp-step-desc">
            Enter each property with owner name and Fair Market Value. Properties
            automatically join the shared waterfall pool or can be reserved for
            a specific facility.
          </div>
        </div>
        <div class="lp-step-card">
          <div class="lp-step-num">STEP 02</div>
          <div class="lp-step-icon">📋</div>
          <div class="lp-step-title">Add Loan Facilities</div>
          <div class="lp-step-desc">
            Select a facility type and principal amount. Choose Shared Pool
            (waterfall priority order) or Dedicated Assignment to lock specific
            properties to a single loan.
          </div>
        </div>
        <div class="lp-step-card">
          <div class="lp-step-num">STEP 03</div>
          <div class="lp-step-icon">📊</div>
          <div class="lp-step-title">Analyse &amp; Export</div>
          <div class="lp-step-desc">
            Review per-facility LTV%, surplus or shortfall, aggregate portfolio
            LTV, and download a structured PDF report for credit committee review.
          </div>
        </div>
      </div>

      <!-- FEATURES -->
      <div class="lp-features">
        <div class="lp-feat">
          <div class="lp-feat-icon">🧮</div>
          <div class="lp-feat-title">Waterfall Allocation</div>
          <div class="lp-feat-desc">50% LTV facilities funded first. Stricter loans get priority access to the pool — exactly as policy requires.</div>
        </div>
        <div class="lp-feat">
          <div class="lp-feat-icon">🔒</div>
          <div class="lp-feat-title">Dedicated Assignment</div>
          <div class="lp-feat-desc">Pin any property exclusively to a facility. FMV split proportionally when the same property backs multiple loans.</div>
        </div>
        <div class="lp-feat">
          <div class="lp-feat-icon">📐</div>
          <div class="lp-feat-title">Surplus &amp; Shortfall</div>
          <div class="lp-feat-desc">Per-facility excess collateral or deficit displayed inline and printed on every PDF report.</div>
        </div>
        <div class="lp-feat">
          <div class="lp-feat-icon">👤</div>
          <div class="lp-feat-title">Owner Tracking</div>
          <div class="lp-feat-desc">Mortgagor name recorded per property and carried through to the audit-ready PDF report.</div>
        </div>
      </div>

      <!-- CTA -->
      <div class="lp-cta">
        <div class="lp-cta-left">
          <h3>Ready to begin your analysis?</h3>
          <p>Add your first property in Step 1 of the sidebar, then add a loan facility in Step 2.</p>
        </div>
        <div class="lp-cta-arrow">← Use the sidebar</div>
      </div>

    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.fmv_sources:
    st.warning("⚠️ Add at least one property in Step 1 of the sidebar before running analysis.")
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
st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Exposure</div>
        <div class="kpi-value">Rs.&nbsp;{total_exposure:,.0f}</div>
        <div class="kpi-sub">{len(st.session_state.loans)} facilities in portfolio</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Collateral FMV</div>
        <div class="kpi-value">Rs.&nbsp;{total_fmv:,.0f}</div>
        <div class="kpi-sub kpi-pos">{len(st.session_state.fmv_sources)} registered properties</div>
    </div>""", unsafe_allow_html=True)

with k3:
    gc = "gauge-fill-ok" if wtd_ltv <= 50 else ("gauge-fill-warn" if wtd_ltv <= 65 else "gauge-fill-fail")
    wc = "#10C980" if wtd_ltv <= 50 else ("#F59E0B" if wtd_ltv <= 65 else "#EF4444")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Weighted Avg LTV</div>
        <div class="kpi-value" style="color:{wc};">{wtd_ltv:.2f}%</div>
        <div class="gauge-track"><div class="{gc}" style="width:{min(wtd_ltv,100):.1f}%;"></div></div>
    </div>""", unsafe_allow_html=True)

with k4:
    agc = "gauge-fill-ok" if aggregate_ltv <= 50 else ("gauge-fill-warn" if aggregate_ltv <= 65 else "gauge-fill-fail")
    st.markdown(f"""
    <div class="kpi-card-gold">
        <div class="kpi-label-gold">Aggregate LTV</div>
        <div class="kpi-value-gold">{aggregate_ltv:.2f}%</div>
        <div class="kpi-sub-gold">Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
        <div class="gauge-track"><div class="{agc}" style="width:{min(aggregate_ltv,100):.1f}%;"></div></div>
    </div>""", unsafe_allow_html=True)

# ── Status Banner
if overall_pass:
    st.markdown(
        "<div class='status-pass'>✅ &nbsp; PORTFOLIO APPROVED — All Facilities Within LTV Policy Limits</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='status-fail'>⚠️ &nbsp; PORTFOLIO DECLINED — One or More Facilities Exceed Maximum LTV</div>",
        unsafe_allow_html=True
    )

# ==========================================
# 🏠 PROPERTY INFORMATION
# ==========================================
st.markdown("""
<div class="section-head">
    <span class="section-head-label">🏠 Property Register</span>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)

assigned_coll_ids  = summary['assigned_collateral_ids']
pool_coll_ids      = summary['pool_collateral_ids']
collateral_usage   = summary['collateral_usage']

cid_to_loan_names = {}
for loan in st.session_state.loans:
    if loan.get('collateral_mode') == 'assigned':
        for cid in loan.get('assigned_collateral_ids', []):
            cid_to_loan_names.setdefault(cid, []).append(
                f"{loan['Loan Type']} (Rs.{loan['Principal']:,.0f})"
            )

prop_rows = []
for src in st.session_state.fmv_sources:
    sid         = src.get('id')
    is_assigned = sid in assigned_coll_ids
    ctype       = "🔒 Assigned" if is_assigned else "🌊 Pool"
    prop_rows.append({
        "Property Reference": src.get('Plot', ''),
        "Owner": src.get('Owner', '—') or '—',
        "FMV (Rs.)": f"Rs. {src.get('Amount', 0):,.0f}",
        "Type": ctype,
        "Linked To": ", ".join(cid_to_loan_names.get(sid, [])) if is_assigned else "Shared Pool",
    })

if prop_rows:
    st.dataframe(pd.DataFrame(prop_rows), hide_index=True, use_container_width=True)

    total_pool_fmv     = summary['pool_fmv']
    total_assigned_fmv = sum(
        s['Amount'] for s in st.session_state.fmv_sources
        if s.get('id') in assigned_coll_ids
    )
    n_pool     = len(pool_coll_ids)
    n_assigned = len(assigned_coll_ids)

    st.markdown(
        f"""<div class="pill-row">
          <div class="pill pill-pool">
            🌊 Pool: {n_pool} propert{'y' if n_pool==1 else 'ies'} &nbsp;·&nbsp; Rs. {total_pool_fmv:,.0f}
          </div>
          <div class="pill pill-asgn">
            🔒 Assigned: {n_assigned} propert{'y' if n_assigned==1 else 'ies'} &nbsp;·&nbsp; Rs. {total_assigned_fmv:,.0f}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

# ==========================================
# 📋 PORTFOLIO LTV BREAKDOWN
# ==========================================
st.markdown("""
<div class="section-head">
    <span class="section-head-label">📋 Portfolio LTV Breakdown</span>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)


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

    if is_unsec or max_ltv is None:
        surplus_disp = "N/A"
    else:
        req_fmv    = r['Principal'] / (max_ltv / 100.0)
        actual_fmv = r.get('Total FMV', 0.0)
        sv         = actual_fmv - req_fmv
        surplus_disp = f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"

    disp_rows.append({
        "Facility":            r['Loan Type'],
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
    "Principal":           f"Rs. {total_exposure:,.0f}",
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
# 📊 LTV VISUAL SUMMARY
# ==========================================
st.markdown("""
<div class="section-head">
    <span class="section-head-label">📊 LTV Visual Summary</span>
    <div class="section-head-line"></div>
</div>
""", unsafe_allow_html=True)

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
            "gauge-fill-ok"   if ltv <= max_ltv * 0.8
            else "gauge-fill-warn" if ltv <= max_ltv
            else "gauge-fill-fail"
        )
        s_color  = "#10C980" if row['Pass_Status'] else "#EF4444"
        mode     = row.get('Collateral_Mode', 'pool')
        mode_badge = {"pool": "🌊 Shared Pool", "assigned": "🔒 Dedicated"}.get(mode, "🌊 Shared Pool")
        coll_names = row.get('Collateral_Names', [])
        coll_text  = (
            ", ".join(coll_names[:2]) + ("…" if len(coll_names) > 2 else "")
            if coll_names else "Pool"
        )

        req_fmv_card    = row['Principal'] / (max_ltv / 100.0)
        actual_fmv_card = row.get('Total FMV', 0.0)
        sv_card         = actual_fmv_card - req_fmv_card
        if sv_card >= 0:
            surplus_html = f"<span class='surplus-ok'>↑ Surplus Rs. {sv_card:,.0f}</span>"
        else:
            surplus_html = f"<span class='surplus-bad'>↓ Short Rs. {abs(sv_card):,.0f}</span>"

        with bar_cols[col_idx]:
            st.markdown(f"""
            <div class="vis-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div class="vis-card-title">{row['Loan Type']}</div>
                    <div class="vis-card-mode">{mode_badge}</div>
                </div>
                <div style="font-size:0.65rem; color:#2D5070; margin-bottom:0.45rem;">🏠 {coll_text}</div>
                <div class="vis-card-pct" style="color:{s_color};">{ltv:.2f}%</div>
                <div class="vis-card-meta">Max {max_ltv:.0f}% &nbsp;·&nbsp; FMV Rs.{row['Total FMV']:,.0f}</div>
                {surplus_html}
                <div class="gauge-track">
                    <div class="{fill_cls}" style="width:{pct_of_max:.1f}%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # Aggregate card
    agg_col_idx  = len(secured_disp) % num_cols
    agg_fill_cls = (
        "gauge-fill-ok"   if aggregate_ltv <= 50
        else "gauge-fill-warn" if aggregate_ltv <= 65
        else "gauge-fill-fail"
    )
    agg_color = "#10C980" if aggregate_ltv <= 70 else "#EF4444"

    with bar_cols[agg_col_idx]:
        st.markdown(f"""
        <div class="vis-card-agg">
            <div style="font-size:0.62rem; font-weight:700; color:#C8962B; letter-spacing:0.1em;
                        text-transform:uppercase; margin-bottom:0.35rem;">Aggregate</div>
            <div class="vis-card-pct" style="color:{agg_color};">{aggregate_ltv:.2f}%</div>
            <div style="font-size:0.7rem; color:#8A7030; margin-top:0.1rem;">
                Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}
            </div>
            <div class="gauge-track" style="margin-top:0.5rem;">
                <div class="{agg_fill_cls}" style="width:{min(aggregate_ltv,100):.1f}%;"></div>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("No secured facilities in portfolio.")


# ── Manage Portfolio
with st.expander("⚙️ Manage Portfolio — Remove Facilities", expanded=False):
    if not st.session_state.loans:
        st.info("No facilities added yet.")
    else:
        for loan in st.session_state.loans:
            lc1, lc2, lc3 = st.columns([3, 2, 1])
            mode_icon = {"pool": "🌊", "assigned": "🔒"}.get(
                loan.get('collateral_mode', 'pool'), "🌊"
            )
            with lc1:
                st.markdown(
                    f"**{mode_icon} {loan['Loan Type']}** &nbsp; Rs. {loan['Principal']:,.0f}"
                )
            with lc2:
                cnames = _get_collateral_names(
                    loan.get('assigned_collateral_ids', []),
                    st.session_state.fmv_sources
                )
                st.markdown(
                    f"<span style='font-size:0.78rem; color:#4A6A8F;'>"
                    f"{'  ·  '.join(cnames) if cnames else 'Shared Pool'}</span>",
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
            placeholder="e.g. Ramesh Kumar Sharma — Q3 Credit Review",
            label_visibility="collapsed",
            help="Name used on the PDF report header"
        )
    with ec2:
        if st.button("Generate PDF", type="primary", use_container_width=True):
            if not report_name.strip():
                st.error("Enter a client or portfolio name.")
            else:
                with st.spinner("Generating report..."):
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
        st.success("✅ Report ready for download.")
        st.download_button(
            label="⬇️ Download PDF Report",
            data=st.session_state['generated_pdf'],
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
        )
