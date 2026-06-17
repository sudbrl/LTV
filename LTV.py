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

        * { box-sizing: border-box; margin: 0; padding: 0; }
        #MainMenu, footer, header { visibility: hidden; }

        .stApp {
            background: #060818 !important;
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.18) 0%, transparent 60%),
                radial-gradient(ellipse 60% 50% at 80% 90%, rgba(139,92,246,0.14) 0%, transparent 60%),
                radial-gradient(ellipse 40% 40% at 60% 40%, rgba(59,130,246,0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        /* ── Wider container ── */
        .block-container {
            max-width: 920px !important;
            margin: 0 auto !important;
            padding-top: 7vh !important;
            padding-bottom: 3rem !important;
            position: relative;
            z-index: 1;
        }

        /* ── Right column card ── */
        [data-testid="stColumn"]:nth-of-type(2) > [data-testid="stVerticalBlock"] {
            background: rgba(10, 14, 30, 0.92) !important;
            border: 1px solid rgba(99,102,241,0.28) !important;
            border-radius: 24px !important;
            padding: 2.5rem 2rem 2rem !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.04) inset,
                0 32px 80px rgba(0,0,0,0.65),
                0 8px 32px rgba(99,102,241,0.12) !important;
            position: relative !important;
        }

        [data-testid="stColumn"]:nth-of-type(2) > [data-testid="stVerticalBlock"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), transparent);
            border-radius: 24px 24px 0 0;
        }

        /* ── Left panel ── */
        .lp-left-panel {
            padding: 1.5rem 2.5rem 1.5rem 0.5rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .lp-logo-outer {
            width: 68px; height: 68px;
            border-radius: 20px;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #9333ea 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.9rem;
            box-shadow:
                0 0 0 1px rgba(139,92,246,0.4),
                0 8px 32px rgba(99,102,241,0.5),
                0 24px 64px rgba(99,102,241,0.2);
            margin-bottom: 1.4rem;
        }

        .lp-wordmark {
            font-size: 1.95rem;
            font-weight: 800;
            color: #f1f5f9;
            letter-spacing: -0.04em;
            line-height: 1.15;
            margin-bottom: 0.45rem;
        }

        .lp-wordmark span {
            background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .lp-tagline-main {
            font-size: 0.88rem;
            color: #64748b;
            font-weight: 400;
            margin-bottom: 2rem;
            line-height: 1.6;
            max-width: 320px;
        }

        .lp-feature-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 2.25rem;
        }

        .lp-feature-item {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }

        .lp-feature-icon {
            width: 30px; height: 30px;
            border-radius: 9px;
            background: rgba(99,102,241,0.14);
            border: 1px solid rgba(99,102,241,0.28);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.82rem;
            flex-shrink: 0;
            margin-top: 0.05rem;
        }

        .lp-feature-text { display: flex; flex-direction: column; }

        .lp-feature-title {
            font-size: 0.82rem;
            font-weight: 700;
            color: #c7d2fe;
            margin-bottom: 0.1rem;
        }

        .lp-feature-desc {
            font-size: 0.71rem;
            color: #475569;
            line-height: 1.45;
        }

        .lp-left-badges {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
        }

        .lp-left-badge {
            font-size: 0.65rem;
            color: #334155;
            font-weight: 600;
            background: rgba(15,20,40,0.8);
            border: 1px solid rgba(99,102,241,0.18);
            border-radius: 99px;
            padding: 0.25rem 0.7rem;
            letter-spacing: 0.03em;
        }

        /* ── Right column: form elements ── */
        .lp-card-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #e2e8f0;
            margin-bottom: 0.25rem;
            letter-spacing: -0.02em;
        }

        .lp-card-sub {
            font-size: 0.79rem;
            color: #475569;
            font-weight: 400;
            margin-bottom: 1.6rem;
            line-height: 1.5;
        }

        .lp-field-label {
            display: block;
            font-size: 0.69rem;
            font-weight: 700;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.4rem;
            margin-top: 1rem;
        }

        div[data-testid="stTextInput"] label { display: none !important; }

        div[data-testid="stTextInput"] > div { background: transparent !important; }

        div[data-testid="stTextInput"] > div > div {
            background: rgba(255,255,255,0.04) !important;
            border: 1px solid rgba(99,102,241,0.25) !important;
            border-radius: 12px !important;
            transition: all 0.25s ease;
        }

        div[data-testid="stTextInput"] > div > div:focus-within {
            border-color: rgba(139,92,246,0.7) !important;
            background: rgba(99,102,241,0.07) !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.15), 0 0 20px rgba(139,92,246,0.1) !important;
        }

        div[data-testid="stTextInput"] > div > div > input {
            background: transparent !important;
            border: none !important;
            color: #e2e8f0 !important;
            font-size: 0.92rem !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 400 !important;
            padding: 0.7rem 0.95rem !important;
            letter-spacing: 0.01em !important;
        }

        div[data-testid="stTextInput"] > div > div > input::placeholder {
            color: rgba(100,116,139,0.7) !important;
            font-weight: 300 !important;
        }

        div.stButton > button {
            width: 100% !important;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            padding: 0.72rem 1.25rem !important;
            letter-spacing: 0.025em !important;
            margin-top: 1.5rem !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 20px rgba(99,102,241,0.4), 0 1px 0 rgba(255,255,255,0.1) inset !important;
        }

        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 32px rgba(99,102,241,0.55), 0 1px 0 rgba(255,255,255,0.1) inset !important;
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
        }

        div.stButton > button:active { transform: translateY(0px) !important; }

        .lp-error {
            background: rgba(239,68,68,0.08);
            border: 1px solid rgba(239,68,68,0.3);
            border-radius: 10px;
            padding: 0.7rem 1rem;
            margin-top: 1rem;
            display: flex;
            align-items: flex-start;
            gap: 0.6rem;
        }

        .lp-error-icon { font-size: 0.85rem; flex-shrink: 0; margin-top: 0.05rem; }

        .lp-error-text { font-size: 0.8rem; color: #fca5a5; font-weight: 500; line-height: 1.45; }

        .lp-divider {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 1.5rem 0 0.75rem;
        }

        .lp-divider-line { flex: 1; height: 1px; background: rgba(99,102,241,0.15); }

        .lp-divider-text {
            font-size: 0.7rem;
            color: #334155;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        .lp-sec-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.4rem; }

        .lp-sec-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.64rem;
            color: #475569;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .lp-sec-pill::before {
            content: '';
            width: 5px; height: 5px;
            border-radius: 50%;
            background: #22c55e;
            flex-shrink: 0;
        }

        div[data-testid="stVerticalBlock"] > div { gap: 0.15rem !important; }

        @media (max-width: 768px) {
            .lp-left-panel { display: none !important; }
            .block-container { padding-top: 4vh !important; }
        }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    col_left, col_right = st.columns([1.25, 0.75])

    # ── Left brand panel (pure HTML, no Streamlit widgets)
    with col_left:
        st.markdown("""
        <div class="lp-left-panel">
            <div class="lp-logo-outer">🏦</div>
            <div class="lp-wordmark">LTV <span>Analysis</span><br>Engine</div>
            <div class="lp-tagline-main">
                Institutional-grade Loan-to-Value analysis platform
                for credit teams and relationship managers.
            </div>

            <ul class="lp-feature-list">
                <li class="lp-feature-item">
                    <div class="lp-feature-icon">📊</div>
                    <div class="lp-feature-text">
                        <span class="lp-feature-title">Multi-Collateral Waterfall</span>
                        <span class="lp-feature-desc">Pool &amp; dedicated assignment modes with proportional FMV split</span>
                    </div>
                </li>
                <li class="lp-feature-item">
                    <div class="lp-feature-icon">🔗</div>
                    <div class="lp-feature-text">
                        <span class="lp-feature-title">Tie-up &amp; Override Support</span>
                        <span class="lp-feature-desc">Flexible per-facility LTV exemptions with audit trail</span>
                    </div>
                </li>
                <li class="lp-feature-item">
                    <div class="lp-feature-icon">📄</div>
                    <div class="lp-feature-text">
                        <span class="lp-feature-title">Institutional PDF Reports</span>
                        <span class="lp-feature-desc">Complete override register, surplus/shortfall &amp; aggregate LTV</span>
                    </div>
                </li>
                <li class="lp-feature-item">
                    <div class="lp-feature-icon">⚡</div>
                    <div class="lp-feature-text">
                        <span class="lp-feature-title">Real-time Portfolio Engine</span>
                        <span class="lp-feature-desc">Instant recalculation across all facilities and collateral</span>
                    </div>
                </li>
            </ul>

            <div class="lp-left-badges">
                <span class="lp-left-badge">🔒 256-bit Encrypted</span>
                <span class="lp-left-badge">Streamlit Cloud</span>
                <span class="lp-left-badge">Institutional Grade</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Right form panel
    with col_right:
        st.markdown("""
        <div class="lp-card-title">Welcome back</div>
        <div class="lp-card-sub">Sign in with your institutional credentials to continue.</div>
        """, unsafe_allow_html=True)

        st.markdown('<span class="lp-field-label">Username</span>', unsafe_allow_html=True)
        username = st.text_input(
            label="u", placeholder="Enter your username",
            key="_login_u", label_visibility="collapsed",
            autocomplete="username",
        )

        st.markdown('<span class="lp-field-label" style="margin-top:1rem;">Password</span>', unsafe_allow_html=True)
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
                f'<div class="lp-error">'
                f'<span class="lp-error-icon">⚠</span>'
                f'<span class="lp-error-text">{err}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("""
        <div class="lp-divider">
            <div class="lp-divider-line"></div>
            <div class="lp-divider-text">Secured Access</div>
            <div class="lp-divider-line"></div>
        </div>
        <div class="lp-sec-pills">
            <span class="lp-sec-pill">TLS Secured</span>
            <span class="lp-sec-pill">Session Protected</span>
            <span class="lp-sec-pill">Audit Ready</span>
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
                    f"Invalid credentials for \"{u}\". "
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
    """
    A loan is LTV-exempt if:
    1. Its policy Max LTV% is None (Professional OD/TL), OR
    2. override_ltv is True, OR
    3. It has tied_property_ids (tie-up = no LTV requirement)
    """
    policy = get_policy_dict()
    if policy.get(loan.get('Loan Type')) is None:
        return True
    if loan.get('override_ltv', False):
        return True
    if loan.get('tied_property_ids'):
        return True
    return False


def _all_loans_ltv_exempt() -> bool:
    """
    Returns True if every loan in the portfolio is LTV-exempt
    (policy-exempt, override, or tie-up), so no collateral is needed at all.
    """
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
        dt = datetime.now().strftime("%B %d, %Y")
        self.cell(0, 10, safe_str(f'Page {self.page_no()} | LTV Engine | {dt}'), 0, 0, 'C')


def _pdf_kv(pdf, label, value):
    pdf.set_font("Arial", "", 10)
    pdf.cell(90, 6, safe_str(label), 0, 0)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, safe_str(str(value)), 0, 1)


def generate_pdf(client_name, results, fmv_sources, summary):
    pdf = PDFReport()
    pdf.add_page()

    total_fmv       = summary['total_fmv']
    total_exposure  = summary['total_exposure']
    aggregate_ltv   = summary['aggregate_ltv']
    overall_pass    = summary['overall_pass']
    total_secured_p = summary['total_secured_principal']
    has_tied_pdf    = any(r.get('tied_property_ids') for r in results)

    # ── Executive Summary
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "EXECUTIVE SUMMARY", 0, 1)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    _pdf_kv(pdf, "Client Name:", client_name)
    _pdf_kv(pdf, "Analysis Date:", datetime.now().strftime("%B %d, %Y"))
    _pdf_kv(pdf, "Total Secured Exposure:", f"Rs. {total_secured_p:,.2f}")
    _pdf_kv(pdf, "Total Loan Exposure (All Facilities):", f"Rs. {total_exposure:,.2f}")
    _pdf_kv(pdf, "Total Collateral FMV:", f"Rs. {total_fmv:,.2f}")
    _pdf_kv(pdf, "Aggregate LTV%:", f"{aggregate_ltv:.2f}%")

    pdf.ln(3)
    res_text = "APPROVED - Within LTV Limits" if overall_pass else "DECLINED - Exceeds LTV Limits"
    if overall_pass:
        pdf.set_text_color(5, 150, 105)
    else:
        pdf.set_text_color(220, 38, 38)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, safe_str(f"Assessment Result: {res_text}"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    # ── Collateral Sources
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "COLLATERAL / FMV SOURCES", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    tied_in_use = {}
    for loan in st.session_state.loans:
        for cid in loan.get('tied_property_ids', []):
            tied_in_use.setdefault(cid, []).append(
                loan.get('loan_account_id', loan.get('Loan Type', ''))
            )

    assigned_ids = summary['assigned_collateral_ids']

    if has_tied_pdf:
        col_w_fmv = [58, 28, 20, 40, 24, 10]
        headers   = ["Plot / Property", "FMV (Rs.)", "Type", "Owner", "Tied A/C", "Ovr"]
    else:
        col_w_fmv = [70, 32, 22, 56]
        headers   = ["Plot / Property", "FMV (Rs.)", "Type", "Owner"]

    pdf.set_font("Arial", "B", 7)
    pdf.set_fill_color(237, 233, 254)
    for hdr, w in zip(headers, col_w_fmv):
        pdf.cell(w, 7, safe_str(hdr), 1, 0, 'C', fill=True)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for i, src in enumerate(fmv_sources):
        fid  = src.get('id', i)
        fill = (i % 2 == 0)
        if fill:
            pdf.set_fill_color(248, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        ctype = "Assigned" if fid in assigned_ids else "Pool"
        owner = safe_str((src.get('Owner', '') or 'N/A')[:22])
        pdf.cell(col_w_fmv[0], 6, safe_str(src['Plot'][:26]), 1, 0, 'L', fill)
        pdf.cell(col_w_fmv[1], 6, f"{src['Amount']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w_fmv[2], 6, safe_str(ctype), 1, 0, 'C', fill)
        pdf.cell(col_w_fmv[3], 6, owner, 1, 0, 'L', fill)
        if has_tied_pdf:
            tied_list = tied_in_use.get(fid, [])
            tied_ac   = safe_str(", ".join(tied_list)[:14] if tied_list else "N/A")
            pdf.cell(col_w_fmv[4], 6, tied_ac, 1, 0, 'L', fill)
            pdf.cell(col_w_fmv[5], 6, "", 1, 1, 'C', fill)
        else:
            pdf.ln()

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w_fmv[0], 6, "TOTAL", 1, 0, 'R', True)
    pdf.cell(col_w_fmv[1], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    rem_w = sum(col_w_fmv[2:])
    pdf.cell(rem_w, 6, "", 1, 1, '', True)

    # ── Facility LTV Breakdown
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "FACILITY LTV BREAKDOWN", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    col_w  = [20, 28, 18, 17, 17, 16, 11, 10, 21, 14, 8]
    hdrs   = ["A/C No.", "Facility", "Principal", "Asgn.FMV", "Pool FMV",
              "Tot.FMV", "LTV%", "Max%", "Surplus/(Dfct)", "Status", "Ovr"]

    pdf.set_font("Arial", "B", 6)
    pdf.set_fill_color(237, 233, 254)
    for h, w in zip(hdrs, col_w):
        pdf.cell(w, 7, safe_str(h), 1, 0, 'C', fill=True)
    pdf.ln()

    def display_sort(r):
        m = r.get('Max LTV%')
        if m is None:
            return (2, 0)
        return (0 if m <= 50 else 1, -(r.get('Principal', 0)))

    for idx, row in enumerate(sorted(results, key=display_sort)):
        fill          = (idx % 2 == 0)
        is_unsec      = row.get('Is_Unsecured', False)
        no_fmv_err    = row.get('No_FMV_Error', False)
        max_ltv       = row.get('Max LTV%')
        ltv_val       = row.get('LTV%')
        ac_id         = safe_str(row.get('loan_account_id', 'N/A'))
        exempt_reason = row.get('Exempt_Reason')
        override_flag = row.get('override_ltv', False)
        tieup_flag    = bool(row.get('tied_property_ids'))

        if fill:
            pdf.set_fill_color(248, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)

        if is_unsec:
            if exempt_reason == "override":
                ltv_disp = "Ovrd"
            elif exempt_reason == "tieup":
                ltv_disp = "TieUp"
            else:
                ltv_disp = "N/A"
        elif no_fmv_err:
            ltv_disp = "ERR"
        elif ltv_val is None:
            ltv_disp = "N/A"
        else:
            ltv_disp = f"{ltv_val:.1f}%"

        max_disp  = "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%"
        asgn_disp = "N/A" if is_unsec else f"{row['Assigned FMV']:,.0f}"
        pool_disp = "N/A" if is_unsec else f"{row['Pool FMV']:,.0f}"
        tot_disp  = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"

        if is_unsec or max_ltv is None:
            surplus_disp = "N/A"
            surplus_val  = None
        elif no_fmv_err:
            surplus_disp = "ERR"
            surplus_val  = -1
        else:
            req_fmv     = row['Principal'] / (max_ltv / 100.0)
            actual_fmv  = row.get('Total FMV', 0.0)
            surplus_val = actual_fmv - req_fmv
            surplus_disp = f"+{surplus_val:,.0f}" if surplus_val >= 0 else f"({abs(surplus_val):,.0f})"

        status = "PASS" if row['Pass_Status'] else "FAIL"
        ovr_disp = "Y" if (override_flag or tieup_flag) else ""

        pdf.set_font("Arial", "B", 6)
        pdf.cell(col_w[0], 6, ac_id, 1, 0, 'C', fill)
        pdf.set_font("Arial", "", 6)
        pdf.cell(col_w[1], 6, safe_str(row['Loan Type'][:18]), 1, 0, 'L', fill)
        pdf.cell(col_w[2], 6, f"{row['Principal']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w[3], 6, safe_str(asgn_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[4], 6, safe_str(pool_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[5], 6, safe_str(tot_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[6], 6, safe_str(ltv_disp), 1, 0, 'C', fill)
        pdf.cell(col_w[7], 6, safe_str(max_disp), 1, 0, 'C', fill)

        if surplus_val is None:
            pdf.set_text_color(100, 116, 139)
        elif surplus_val >= 0:
            pdf.set_text_color(5, 150, 105)
        else:
            pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[8], 6, safe_str(surplus_disp), 1, 0, 'R', fill)
        pdf.set_text_color(0, 0, 0)

        if status == "PASS":
            pdf.set_text_color(5, 150, 105)
        else:
            pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[9], 6, safe_str(status), 1, 0, 'C', fill)
        pdf.set_text_color(0, 0, 0)

        if ovr_disp:
            pdf.set_text_color(133, 77, 14)
        pdf.cell(col_w[10], 6, safe_str(ovr_disp), 1, 1, 'C', fill)
        pdf.set_text_color(0, 0, 0)

    # Aggregate row
    pdf.set_font("Arial", "B", 6)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w[0], 6, "AGG", 1, 0, 'C', True)
    pdf.cell(col_w[1], 6, "AGGREGATE (ALL)", 1, 0, 'L', True)
    pdf.cell(col_w[2], 6, f"{total_exposure:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[3], 6, "N/A", 1, 0, 'R', True)
    pdf.cell(col_w[4], 6, "N/A", 1, 0, 'R', True)
    pdf.cell(col_w[5], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[6], 6, f"{aggregate_ltv:.1f}%", 1, 0, 'C', True)
    pdf.cell(col_w[7], 6, "N/A", 1, 0, 'C', True)
    pdf.cell(col_w[8], 6, "N/A", 1, 0, 'R', True)
    agg_st = "PASS" if overall_pass else "FAIL"
    pdf.cell(col_w[9], 6, agg_st, 1, 0, 'C', True)
    pdf.cell(col_w[10], 6, "", 1, 1, 'C', True)

    pdf.ln(2)
    pdf.set_font("Arial", "I", 6)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 4, safe_str(
        "Ovr = LTV Override active (Override flag or Tie-up). "
        "Ovrd = Manually overridden. TieUp = Tie-up properties selected (no LTV required).\n"
        "Surplus/(Dfct): +value = excess collateral | (value) = shortfall | "
        "ERR = no collateral | N/A = exempt.\n"
        "Aggregate Principal = ALL facilities; Aggregate LTV% = secured principal / total FMV."
    ))
    pdf.set_text_color(0, 0, 0)

    # ── Override / Tied Properties Register (table format in PDF)
    overridden_loans = [r for r in results if r.get('override_ltv') or r.get('tied_property_ids')]
    if overridden_loans:
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.set_text_color(30, 27, 75)
        pdf.cell(0, 8, "LTV OVERRIDE & TIED PROPERTIES REGISTER", 0, 1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

        fmv_id_map_pdf = {s['id']: s for s in fmv_sources}

        # Table header
        reg_col_w = [20, 32, 22, 30, 45, 25, 16]
        reg_hdrs  = ["A/C No.", "Facility", "Principal", "Exempt Type",
                     "Tied Properties", "Tied FMV", "Requirement"]
        pdf.set_font("Arial", "B", 6.5)
        pdf.set_fill_color(237, 233, 254)
        for h, w in zip(reg_hdrs, reg_col_w):
            pdf.cell(w, 7, safe_str(h), 1, 0, 'C', fill=True)
        pdf.ln()

        for idx, row in enumerate(overridden_loans):
            fill          = (idx % 2 == 0)
            ac_id         = safe_str(row.get('loan_account_id', 'N/A'))
            exempt_reason = row.get('Exempt_Reason', '')
            exempt_label  = {
                "override": "Manual Override",
                "tieup":    "Tie-up Props",
                "policy":   "Policy Exempt",
            }.get(exempt_reason, "Exempt")

            tied_names = []
            tied_fmv_total = 0.0
            for cid in row.get('tied_property_ids', []):
                src = fmv_id_map_pdf.get(cid)
                if src:
                    tied_names.append(safe_str(src.get('Plot', '')[:16]))
                    tied_fmv_total += src.get('Amount', 0.0)

            tied_props_str = safe_str(", ".join(tied_names)[:28]) if tied_names else "N/A"
            tied_fmv_str   = f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "N/A"

            if fill:
                pdf.set_fill_color(248, 245, 255)
            else:
                pdf.set_fill_color(255, 255, 255)

            pdf.set_font("Arial", "B", 6.5)
            pdf.cell(reg_col_w[0], 6, ac_id, 1, 0, 'C', fill)
            pdf.set_font("Arial", "", 6.5)
            pdf.cell(reg_col_w[1], 6, safe_str(row['Loan Type'][:18]), 1, 0, 'L', fill)
            pdf.cell(reg_col_w[2], 6, f"Rs.{row['Principal']:,.0f}", 1, 0, 'R', fill)
            pdf.cell(reg_col_w[3], 6, safe_str(exempt_label), 1, 0, 'C', fill)
            pdf.cell(reg_col_w[4], 6, tied_props_str, 1, 0, 'L', fill)
            pdf.cell(reg_col_w[5], 6, tied_fmv_str, 1, 0, 'R', fill)
            pdf.cell(reg_col_w[6], 6, "No LTV Req.", 1, 1, 'C', fill)

        pdf.ln(2)
        pdf.set_font("Arial", "I", 6.5)
        pdf.set_text_color(100, 116, 139)
        pdf.multi_cell(0, 4, safe_str(
            "Note: Overridden and tie-up facilities are treated as LTV-exempt. "
            "Tied properties are additional/secondary security only. "
            "Override must be sanctioned by credit authority."
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

        # ── Override LTV checkbox (available for all loan types that normally need LTV)
        # NOTE: override is allowed even without any collateral entered
        if max_ltv_sel is not None:
            override_ltv = st.checkbox(
                "Override collateral requirement (no LTV required)",
                value=False,
                key="sb_override_ltv",
                help=(
                    "Check this to mark the facility as LTV-exempt regardless of policy. "
                    "The loan will not consume any collateral FMV. "
                    "No properties need to be added. "
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
                            st.warning("Selected property already assigned - FMV will be split proportionally.")
                    else:
                        st.warning("Add properties first (Step 1) to use dedicated mode.")
            else:
                st.info(
                    "LTV Override enabled. This facility is LTV-exempt — "
                    "no collateral properties are required."
                )
        else:
            st.info("Unsecured facility — no collateral required")

        # ── Tie-up: only show if NOT already override
        if not override_ltv:
            use_tie_up = st.checkbox(
                "Tie up Property (additional security)?", value=False, key="sb_use_tie_up",
                help=(
                    "Mark properties as tied/pledged. "
                    "IMPORTANT: Selecting tie-up properties makes this facility LTV-exempt."
                )
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
                        st.warning(
                            f"{len(tie_up_colls)} property/ies selected as tie-up. "
                            "This facility will be LTV-exempt."
                        )
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

# ── Landing page
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
          <div class="step-desc">Enter each collateral property with owner name and Fair Market Value. Properties are optional if all loans use Override.</div>
        </div>
        <div class="step-card">
          <div class="step-num">2</div>
          <div class="step-title">Add Loan Facilities</div>
          <div class="step-desc">Select facility type, principal, collateral mode (pool/dedicated/override), and optionally tie up additional properties (auto LTV-exempt).</div>
        </div>
        <div class="step-card">
          <div class="step-num">3</div>
          <div class="step-title">Analyse &amp; Export</div>
          <div class="step-desc">Review per-facility LTV%, surplus or shortfall, aggregate LTV, override register, and download a professional PDF.</div>
        </div>
      </div>
      <div class="landing-cta">
        <div class="landing-cta-title">Ready to get started?</div>
        <div class="landing-cta-sub">
          Add properties in <b>Step 1</b> (or skip if using Override), then add a loan in <b>Step 2</b>.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Collateral check — skip stop() if all loans are LTV-exempt
if not st.session_state.fmv_sources:
    if not _all_loans_ltv_exempt():
        st.warning(
            "Add at least one property/FMV source in the sidebar (Step 1). "
            "Properties are only optional when all facilities have LTV Override enabled."
        )
        st.stop()
    # All loans are exempt (override / policy-exempt) — no collateral needed, proceed normally

# ── Run engine
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

# ── KPI Row
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

# ── Override / Tie-up info banner
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
            f"<b>LTV-Exempt Facilities:</b> The following facilities are excluded from LTV "
            f"calculation (no collateral FMV consumed): "
            f"{' &nbsp;|&nbsp; '.join(parts)}</div>",
            unsafe_allow_html=True
        )

# ── Status Banner
if overall_pass:
    st.markdown(
        "<div class='status-banner status-pass'>PORTFOLIO APPROVED - All Facilities Within LTV Limits</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='status-banner status-fail'>PORTFOLIO DECLINED - One or More Facilities Exceed Maximum LTV</div>",
        unsafe_allow_html=True
    )

# ── No-FMV alert
no_fmv_loans = [r for r in results if r.get('No_FMV_Error')]
if no_fmv_loans:
    names = ", ".join(f"[{r.get('loan_account_id','?')}] {r['Loan Type']}" for r in no_fmv_loans)
    st.error(
        f"No Collateral Available — the following facilities have no FMV allocated: {names}. "
        f"Add properties or enable Override for these facilities."
    )

# ==========================================
# 🏠 PROPERTY INFORMATION
# ==========================================
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
        "You can add properties in Step 1 if needed as additional/tie-up security."
    )

# ==========================================
# 📋 PORTFOLIO LTV BREAKDOWN
# ==========================================
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

# Aggregate
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

# ==========================================
# 📊 LTV VISUAL SUMMARY
# ==========================================
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
                badge_color  = "#713f12"
                badge_bg     = "#fefce8"
                badge_border = "#fde047"
                badge_label  = "LTV Override"
                ltv_text     = "Overridden"
                surp_cls     = "surplus-na"
                surp_text    = "No LTV Required"
            else:
                badge_color  = "#6b21a8"
                badge_bg     = "#fdf4ff"
                badge_border = "#e9d5ff"
                badge_label  = "Tie-up Exempt"
                ltv_text     = "Tie-up Exempt"
                surp_cls     = "surplus-na"
                surp_text    = "No LTV Required"

            mode_lbl  = "Override" if override_flag else ("Tied" if tieup_flag else "Unsecured")

            card_html = (
                f"<div style='background:linear-gradient(135deg,{badge_bg} 0%,#ffffff 100%); "
                f"border:1.5px solid {badge_border}; border-radius:12px; "
                f"padding:1rem; margin-bottom:0.75rem; opacity:0.92;'>"
                f"<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.15rem;'>"
                f"<div style='font-size:0.75rem; font-weight:700; color:#1e1b4b;'>{row['Loan Type']}</div>"
                f"<div style='font-size:0.65rem; font-weight:700; color:{badge_color}; "
                f"background:{badge_bg}; border:1px solid {badge_border}; "
                f"border-radius:6px; padding:0.1rem 0.35rem;'>{badge_label}</div>"
                f"</div>"
                f"<div style='font-family:monospace; font-size:0.68rem; font-weight:700; color:#4c1d95; "
                f"background:#ede9fe; display:inline-block; padding:0.1rem 0.4rem; "
                f"border-radius:4px; margin-bottom:0.3rem;'>{ac_id}</div>"
                f"<div style='font-size:1.5rem; font-weight:700; color:{badge_color}; "
                f"font-family:monospace;'>{ltv_text}</div>"
                f"<div style='font-size:0.72rem; color:#64748b;'>Principal: Rs.{row['Principal']:,.0f}</div>"
                f"<span class='{surp_cls}'>{surp_text}</span>"
                f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>"
                f"<div style='height:100%; background:{badge_border}; border-radius:99px; width:100%;'></div>"
                f"</div>"
                f"</div>"
            )
            with bar_cols[col_idx]:
                st.markdown(card_html, unsafe_allow_html=True)
            continue

        if no_fmv_err or ltv is None:
            pct_bar   = 100.0
            fill_cls  = "gauge-err"
            s_color   = "#dc2626"
            ltv_text  = "No FMV"
            surp_cls  = "surplus-err"
            surp_text = "No collateral allocated"
        else:
            pct_bar  = min((ltv / max_ltv) * 100, 100)
            fill_cls = "gauge-ok" if ltv <= max_ltv * 0.8 else ("gauge-warn" if ltv <= max_ltv else "gauge-fail")
            s_color  = "#059669" if row['Pass_Status'] else "#dc2626"
            ltv_text = f"{ltv:.2f}%"
            sv       = row.get('Total FMV', 0.0) - row['Principal'] / (max_ltv / 100.0)
            surp_cls  = "surplus-pos" if sv >= 0 else "surplus-neg"
            surp_text = f"Surplus Rs. {sv:,.0f}" if sv >= 0 else f"Short Rs. {abs(sv):,.0f}"

        mode      = row.get('Collateral_Mode', 'pool')
        mode_lbl  = "Pool" if mode == "pool" else "Assigned"
        coll_names = row.get('Collateral_Names', [])
        coll_text  = (
            ", ".join(coll_names[:2]) + ("..." if len(coll_names) > 2 else "")
            if coll_names else "Pool"
        )

        with bar_cols[col_idx]:
            card_html = (
                "<div style='background:white; border:1px solid #ddd6fe; border-radius:12px; "
                "padding:1rem; margin-bottom:0.75rem;'>"
                "<div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.15rem;'>"
                f"<div style='font-size:0.75rem; font-weight:700; color:#1e1b4b;'>{row['Loan Type']}</div>"
                f"<div style='font-size:0.68rem; color:#64748b;'>{mode_lbl}</div>"
                "</div>"
                f"<div style='font-family:monospace; font-size:0.68rem; font-weight:700; color:#4c1d95; "
                f"background:#ede9fe; display:inline-block; padding:0.1rem 0.4rem; "
                f"border-radius:4px; margin-bottom:0.3rem;'>{ac_id}</div>"
                f"<div style='font-size:0.68rem; color:#94a3b8; margin-bottom:0.4rem;'>{coll_text}</div>"
                f"<div style='font-size:1.5rem; font-weight:700; color:{s_color}; font-family:monospace;'>{ltv_text}</div>"
                f"<div style='font-size:0.72rem; color:#64748b;'>Max: {max_ltv:.0f}% &nbsp;·&nbsp; "
                f"FMV: Rs.{row['Total FMV']:,.0f}</div>"
                f"<span class='{surp_cls}'>{surp_text}</span>"
                f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>"
                f"<div class='{fill_cls}' style='width:{pct_bar:.1f}%'></div>"
                "</div>"
                "</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

    agg_col_idx  = len(all_visual) % num_cols
    agg_fill_cls = "gauge-ok" if aggregate_ltv <= 50 else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    agg_color    = "#059669" if aggregate_ltv <= 70 else "#dc2626"
    agg_pct      = min(aggregate_ltv, 100)

    with bar_cols[agg_col_idx]:
        agg_html = (
            "<div style='background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%); "
            "border:1px solid #4338ca; border-radius:12px; padding:1rem; margin-bottom:0.75rem;'>"
            "<div style='font-size:0.7rem; font-weight:700; color:#a5b4fc; "
            "text-transform:uppercase; margin-bottom:0.3rem;'>AGGREGATE</div>"
            f"<div style='font-size:1.5rem; font-weight:700; color:{agg_color}; "
            f"font-family:monospace;'>{aggregate_ltv:.2f}%</div>"
            f"<div style='font-size:0.74rem; color:#c7d2fe;'>"
            f"Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>"
            f"<div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>"
            f"<div class='{agg_fill_cls}' style='width:{agg_pct:.1f}%'></div>"
            "</div>"
            "</div>"
        )
        st.markdown(agg_html, unsafe_allow_html=True)

else:
    st.info("No facilities with active LTV calculations in portfolio.")

# ==========================================
# 📋 LTV OVERRIDE & TIE-UP REGISTER  (table format)
# ==========================================
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

            tied_names     = []
            tied_owners    = []
            tied_fmv_total = 0.0
            for cid in r.get('tied_property_ids', []):
                src = fmv_src_map.get(cid)
                if src:
                    tied_names.append(src.get('Plot', ''))
                    tied_owners.append(src.get('Owner', '') or 'N/A')
                    tied_fmv_total += src.get('Amount', 0.0)

            unique_owners = list(dict.fromkeys(tied_owners))  # dedupe, preserve order

            register_rows.append({
                "A/C No.":            ac_id,
                "Facility Type":      r['Loan Type'],
                "Principal (Rs.)":    f"Rs. {r['Principal']:,.0f}",
                "Exempt Type":        exempt_label,
                "Tied Properties":    ", ".join(tied_names) if tied_names else "—",
                "Tied Owner(s)":      ", ".join(unique_owners) if unique_owners else "—",
                "Tied FMV (Rs.)":     f"Rs. {tied_fmv_total:,.0f}" if tied_fmv_total > 0 else "—",
                "LTV Requirement":    "No LTV Required",
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
            "Tie-up properties serve as additional/secondary security only and do not reduce LTV exposure."
            "</div>",
            unsafe_allow_html=True
        )

# ── Manage Portfolio
with st.expander("Manage Portfolio - Remove Loans", expanded=False):
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
