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
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

        #MainMenu, footer, header { visibility: hidden; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

        .stApp {
            background: #040D18 !important;
            background-image:
                radial-gradient(ellipse at 30% 20%, rgba(8,145,178,0.07) 0%, transparent 55%),
                radial-gradient(ellipse at 80% 80%, rgba(6,182,212,0.04) 0%, transparent 50%) !important;
        }
        .stApp::before {
            content: '';
            position: fixed; inset: 0;
            background-image: radial-gradient(rgba(8,145,178,0.18) 1px, transparent 1px);
            background-size: 32px 32px;
            pointer-events: none; z-index: 0;
        }
        .block-container {
            max-width: 440px !important;
            padding-top: 7vh !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            position: relative; z-index: 1;
        }

        /* ── CARD */
        .lg-card {
            background: #07111E;
            border: 1px solid #0E2438;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 32px 80px rgba(0,0,0,0.8), 0 0 0 1px rgba(8,145,178,0.06);
        }
        .lg-bar {
            height: 3px;
            background: linear-gradient(90deg, transparent 0%, #0891B2 25%, #22D3EE 55%, #0891B2 80%, transparent 100%);
            box-shadow: 0 0 18px rgba(8,145,178,0.7);
        }
        .lg-body { padding: 2.25rem 2rem 1.85rem; }

        .lg-brand { text-align: center; margin-bottom: 1.85rem; }
        .lg-icon {
            display: inline-flex; align-items: center; justify-content: center;
            width: 54px; height: 54px;
            background: linear-gradient(135deg, #0C2035, #091728);
            border: 1px solid rgba(8,145,178,0.45);
            border-radius: 14px; font-size: 1.55rem; margin-bottom: 0.9rem;
            box-shadow: 0 0 24px rgba(8,145,178,0.18);
        }
        .lg-name {
            font-size: 1.22rem; font-weight: 700; color: #E8F6FF;
            letter-spacing: -0.02em; margin-bottom: 0.22rem;
        }
        .lg-sub {
            font-size: 0.67rem; font-weight: 600; letter-spacing: 0.13em;
            text-transform: uppercase; color: #0891B2;
        }
        .lg-rule {
            height: 1px;
            background: linear-gradient(90deg, transparent, #0E2438, transparent);
            margin: 1.3rem 0;
        }
        .lg-lbl {
            font-size: 0.62rem; font-weight: 600; letter-spacing: 0.11em;
            text-transform: uppercase; color: #3A6A88; display: block;
            margin-bottom: 0.3rem;
        }

        div[data-testid="stTextInput"] label { display: none !important; }
        div[data-testid="stTextInput"] > div > div > input {
            background: #040D18 !important; border: 1px solid #0E2438 !important;
            border-radius: 9px !important; color: #E8F6FF !important;
            font-size: 0.92rem !important; padding: 0.65rem 0.9rem !important;
            transition: all 0.2s !important;
        }
        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: #0891B2 !important;
            box-shadow: 0 0 0 3px rgba(8,145,178,0.14) !important;
            background: #060F1A !important;
        }
        div[data-testid="stTextInput"] > div > div > input::placeholder { color: #1A3A52 !important; }

        div.stButton > button {
            background: linear-gradient(135deg, #0891B2, #0669A0) !important;
            color: #E8F6FF !important; border: none !important; border-radius: 9px !important;
            font-weight: 700 !important; font-size: 0.88rem !important;
            letter-spacing: 0.03em !important; padding: 0.68rem !important;
            width: 100% !important; transition: all 0.2s !important;
            box-shadow: 0 4px 18px rgba(8,145,178,0.32) !important;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #22D3EE, #0891B2) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 26px rgba(8,145,178,0.48) !important;
        }

        .lg-err {
            background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25);
            border-radius: 8px; color: #FCA5A5; font-size: 0.79rem;
            line-height: 1.55; padding: 0.68rem 0.9rem; margin-top: 0.8rem;
        }
        .lg-foot {
            text-align: center; font-size: 0.62rem; color: #102030;
            padding: 0.85rem 2rem;
            border-top: 1px solid rgba(14,36,56,0.8);
            letter-spacing: 0.07em;
        }
        div[data-testid="stVerticalBlock"] > div { gap: 0.38rem !important; }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    st.markdown(
        '<div class="lg-card"><div class="lg-bar"></div><div class="lg-body">',
        unsafe_allow_html=True
    )
    st.markdown("""
        <div class="lg-brand">
            <div class="lg-icon">🏦</div>
            <div class="lg-name">LTV Analysis Engine</div>
            <div class="lg-sub">Credit Risk &nbsp;·&nbsp; Secure Portal</div>
        </div>
        <div class="lg-rule"></div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="lg-lbl">Username</span>', unsafe_allow_html=True)
    username = st.text_input(
        label="u", placeholder="Enter your username", key="_login_u",
        label_visibility="collapsed", autocomplete="username"
    )
    st.markdown('<span class="lg-lbl" style="margin-top:.6rem;display:block;">Password</span>', unsafe_allow_html=True)
    password = st.text_input(
        label="p", placeholder="Enter your password", type="password",
        key="_login_p", label_visibility="collapsed", autocomplete="current-password"
    )
    st.markdown('<div style="margin-top:.9rem"></div>', unsafe_allow_html=True)
    clicked = st.button("Sign In →", key="_login_btn", use_container_width=True)

    if clicked:
        u, p = str(username).strip(), str(password).strip()
        if not u:
            st.session_state["_login_error"] = "⚠️ Username is required."
            st.rerun()
        elif not p:
            st.session_state["_login_error"] = "⚠️ Password is required."
            st.rerun()
        elif _check_credentials(u, p):
            st.session_state.update({"authenticated": True, "auth_username": u, "_login_error": ""})
            st.rerun()
        else:
            all_pw = _get_all_passwords()
            if u in all_pw:
                msg = f"<b>Username and password appear swapped.</b><br>Try username <code>admin</code> with password <code>{u}</code>."
            else:
                msg = "Invalid credentials. Please check and try again."
            st.session_state["_login_error"] = msg
            st.rerun()

    err = st.session_state.get("_login_error", "")
    if err:
        st.markdown(f'<div class="lg-err">{err}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lg-foot">🔐 &nbsp;SECURED CONNECTION &nbsp;·&nbsp; AUTHORISED PERSONNEL ONLY</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)


# ── Auth init
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    _show_login()
    st.stop()


# ==========================================
# 🎨 MAIN APP STYLES  — Slate + Cyan palette
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #D8EEF8;
    letter-spacing: -0.005em;
}

/* ── Page background */
.main {
    background: #06111D !important;
    background-image:
        radial-gradient(ellipse at 5% 0%, rgba(8,145,178,0.07) 0%, transparent 40%),
        radial-gradient(ellipse at 95% 100%, rgba(6,182,212,0.04) 0%, transparent 40%) !important;
}
.block-container { max-width: 97% !important; padding-top: 1.1rem !important; }

/* ── Number / data display */
.mono { font-family: 'DM Mono', monospace; }

/* ── Inputs */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #040D18 !important; border: 1px solid #0E2438 !important;
    border-radius: 8px !important; color: #D8EEF8 !important;
    font-size: 0.88rem !important; padding: 0.58rem 0.8rem !important;
    transition: all 0.18s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: #0891B2 !important;
    box-shadow: 0 0 0 3px rgba(8,145,178,0.13) !important;
    background: #060F1A !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #1A3A52 !important; }

/* ── Selectbox */
div[data-baseweb="select"] > div {
    background: #040D18 !important; border: 1px solid #0E2438 !important;
    border-radius: 8px !important; color: #D8EEF8 !important;
}

/* ── Sidebar */
[data-testid="stSidebar"] {
    background: #040D18 !important;
    border-right: 1px solid #0E2438 !important;
}
[data-testid="stSidebar"] * { color: #8ABBD0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #C8E6F4 !important; }
[data-testid="stSidebar"] div[data-testid="stTextInput"] input,
[data-testid="stSidebar"] div[data-testid="stNumberInput"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background: #060F1A !important; border-color: #0E2438 !important;
    color: #C8E6F4 !important;
}

/* ── Primary buttons */
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0891B2, #0669A0) !important;
    border: none !important; color: #E8F6FF !important;
    border-radius: 8px !important; font-weight: 700 !important;
    transition: all 0.18s !important;
    box-shadow: 0 2px 12px rgba(8,145,178,0.28) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #22D3EE, #0891B2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(8,145,178,0.42) !important;
}

/* ── Secondary buttons (remove) */
div.stButton > button[kind="secondary"],
div.stButton > button[data-testid="baseButton-secondary"] {
    background: rgba(14,36,56,0.7) !important;
    border: 1px solid #0E2438 !important; color: #4A7090 !important;
    border-radius: 6px !important; font-size: 0.72rem !important;
    font-weight: 600 !important; transition: all 0.15s !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: rgba(239,68,68,0.4) !important;
    color: #FCA5A5 !important;
}

/* ── Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 10px !important; overflow: hidden;
    border: 1px solid #0E2438 !important;
}

/* ── Expander */
[data-testid="stExpander"] {
    background: #060F1A !important; border: 1px solid #0E2438 !important;
    border-radius: 10px !important;
}

/* ── Alerts */
[data-testid="stAlert"] {
    background: rgba(8,145,178,0.06) !important;
    border-color: #0E2438 !important; color: #7AB8D0 !important;
    border-radius: 8px !important;
}

/* ── Checkbox */
[data-testid="stCheckbox"] { color: #7AB8D0 !important; }

/* ── Multiselect tag */
span[data-baseweb="tag"] {
    background: rgba(8,145,178,0.15) !important;
    border: 1px solid rgba(8,145,178,0.3) !important;
    border-radius: 5px !important;
}

/* ── Headings */
h1 { font-weight: 700 !important; color: #E8F6FF !important; letter-spacing: -0.025em !important; }
h2, h3 { font-weight: 600 !important; color: #BDD8EE !important; }

/* ── Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060F1A; }
::-webkit-scrollbar-thumb { background: #0E2438; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #0891B2; }

/* ── Form container tweak */
[data-testid="stForm"] {
    background: #060F1A !important;
    border: 1px solid #0E2438 !important;
    border-radius: 12px !important;
    padding: 1rem 1.1rem !important;
}

/* ────────────────────────────────────────
   COMPONENTS
──────────────────────────────────────── */

/* Section header */
.sec-head {
    display: flex; align-items: center; gap: 0.7rem;
    margin: 1.4rem 0 0.8rem;
}
.sec-head-lbl {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0891B2; white-space: nowrap;
}
.sec-head-line {
    height: 1px; flex: 1;
    background: linear-gradient(90deg, #0E2438, transparent);
}

/* KPI cards */
.kpi {
    background: linear-gradient(145deg, #09192A 0%, #071526 100%);
    border: 1px solid #0E2438; border-radius: 12px;
    padding: 1rem 1.2rem 0.95rem; position: relative; overflow: hidden;
    transition: border-color 0.18s;
}
.kpi::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, rgba(8,145,178,0.5), transparent);
}
.kpi:hover { border-color: #163858; }
.kpi-lbl {
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #3A6A88; margin-bottom: 0.38rem;
}
.kpi-val {
    font-family: 'DM Mono', monospace; font-size: 1.5rem;
    font-weight: 600; color: #D8EEF8; line-height: 1.15; letter-spacing: -0.02em;
}
.kpi-sub { font-size: 0.7rem; font-weight: 500; margin-top: 0.22rem; color: #2A5070; }
.kpi-pos { color: #10B981 !important; }
.kpi-neg { color: #EF4444 !important; }

/* Accent KPI (cyan highlight) */
.kpi-accent {
    background: linear-gradient(145deg, #061824 0%, #041220 100%);
    border: 1px solid #0891B2; border-radius: 12px;
    padding: 1rem 1.2rem 0.95rem; position: relative; overflow: hidden;
    box-shadow: 0 0 24px rgba(8,145,178,0.1);
}
.kpi-accent::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #0891B2 40%, #22D3EE 60%, #0891B2, transparent);
    box-shadow: 0 0 8px rgba(8,145,178,0.8);
}
.kpi-accent-lbl {
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #0891B2; margin-bottom: 0.38rem;
}
.kpi-accent-val {
    font-family: 'DM Mono', monospace; font-size: 1.5rem;
    font-weight: 600; color: #22D3EE; line-height: 1.15; letter-spacing: -0.02em;
}
.kpi-accent-sub { font-size: 0.7rem; color: #0E5A72; margin-top: 0.22rem; }

/* Gauge */
.gauge { height: 4px; background: #0A1E30; border-radius: 99px; overflow: hidden; margin-top: 0.5rem; }
.g-ok   { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #059669, #10B981); }
.g-warn { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #B45309, #F59E0B); }
.g-fail { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #991B1B, #EF4444); }

/* Status banners */
.s-pass {
    background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.22);
    border-left: 3px solid #10B981; border-radius: 10px; color: #6EE7B7;
    font-weight: 700; font-size: 0.88rem; padding: 0.8rem 1.2rem;
    margin: 0.9rem 0; display: flex; align-items: center; gap: 0.55rem;
}
.s-fail {
    background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.22);
    border-left: 3px solid #EF4444; border-radius: 10px; color: #FCA5A5;
    font-weight: 700; font-size: 0.88rem; padding: 0.8rem 1.2rem;
    margin: 0.9rem 0; display: flex; align-items: center; gap: 0.55rem;
}

/* ── COLLATERAL CARDS GRID */
.coll-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.7rem;
    margin-top: 0.8rem;
}
.coll-card {
    background: #07121E;
    border: 1px solid #0E2438;
    border-radius: 11px;
    padding: 0.9rem 1rem 0.75rem;
    transition: border-color 0.18s, box-shadow 0.18s;
    position: relative;
}
.coll-card:hover { border-color: #163858; box-shadow: 0 4px 18px rgba(0,0,0,0.3); }
.coll-card-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.6rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; border-radius: 5px;
    padding: 0.15rem 0.5rem; margin-bottom: 0.55rem;
}
.badge-pool { background: rgba(8,145,178,0.1); border: 1px solid rgba(8,145,178,0.25); color: #0891B2; }
.badge-asgn { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: #F59E0B; }
.coll-card-ref {
    font-size: 0.82rem; font-weight: 600; color: #BDD8EE;
    line-height: 1.35; margin-bottom: 0.3rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.coll-card-owner {
    font-size: 0.7rem; color: #3A6A88; margin-bottom: 0.45rem;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.coll-card-fmv {
    font-family: 'DM Mono', monospace; font-size: 1.05rem;
    font-weight: 500; color: #D8EEF8; letter-spacing: -0.01em;
}
.coll-empty {
    border: 1px dashed #0E2438; border-radius: 11px;
    padding: 2.5rem 1rem; text-align: center;
    background: rgba(6,15,26,0.4);
}
.coll-empty-icon { font-size: 1.8rem; margin-bottom: 0.5rem; opacity: 0.35; }
.coll-empty-title { font-size: 0.85rem; font-weight: 600; color: #1A3A52; margin-bottom: 0.25rem; }
.coll-empty-sub { font-size: 0.75rem; color: #102030; }

/* Summary bar */
.coll-summary {
    display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 0.1rem;
}
.coll-sum-pill {
    font-size: 0.75rem; font-weight: 600; border-radius: 7px;
    padding: 0.42rem 0.9rem;
}
.sum-pool { background: rgba(8,145,178,0.08); border: 1px solid rgba(8,145,178,0.2); color: #0891B2; }
.sum-asgn { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); color: #F59E0B; }
.sum-total { background: rgba(216,238,248,0.05); border: 1px solid #0E2438; color: #5A8AA8; }

/* Visual summary cards */
.vc {
    background: #07121E; border: 1px solid #0E2438; border-radius: 12px;
    padding: 0.95rem 1rem; margin-bottom: 0.6rem; transition: border-color 0.18s;
}
.vc:hover { border-color: #163858; }
.vc-title { font-size: 0.74rem; font-weight: 700; color: #BDD8EE; margin-bottom: 0.08rem; }
.vc-mode  { font-size: 0.62rem; color: #2A5070; margin-bottom: 0.45rem; }
.vc-pct   { font-family: 'DM Mono', monospace; font-size: 1.4rem; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
.vc-meta  { font-size: 0.67rem; color: #2A5070; margin-top: 0.08rem; }
.vc-surp-ok  { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); color: #6EE7B7; border-radius: 5px; padding: 0.15rem 0.5rem; font-size: 0.67rem; font-weight: 600; display: inline-block; margin-top: 0.38rem; }
.vc-surp-bad { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);  color: #FCA5A5; border-radius: 5px; padding: 0.15rem 0.5rem; font-size: 0.67rem; font-weight: 600; display: inline-block; margin-top: 0.38rem; }
.vc-agg {
    background: linear-gradient(145deg, #061824, #041220);
    border: 1px solid rgba(8,145,178,0.35); border-radius: 12px;
    padding: 0.95rem 1rem; margin-bottom: 0.6rem;
    box-shadow: 0 0 20px rgba(8,145,178,0.07);
}

/* Sidebar elements */
.sb-div { height: 1px; background: linear-gradient(90deg, #0E2438, transparent); margin: 0.7rem 0; }
.sb-step {
    font-size: 0.63rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #0891B2 !important;
    display: flex; align-items: center; gap: 0.45rem; margin: 0.4rem 0 0.6rem;
}
.sb-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 17px; height: 17px; border-radius: 50%;
    background: rgba(8,145,178,0.12); border: 1px solid rgba(8,145,178,0.35);
    font-size: 0.6rem; font-weight: 800; color: #0891B2;
}
.sb-stat {
    background: rgba(8,145,178,0.05); border: 1px solid rgba(8,145,178,0.14);
    border-radius: 7px; padding: 0.45rem 0.7rem; font-size: 0.73rem; margin: 0.35rem 0;
    color: #7AAFC8 !important;
}
.sb-stat b { color: #0891B2 !important; font-family: 'DM Mono', monospace; }
.sb-hint {
    background: rgba(8,145,178,0.05); border-left: 2px solid rgba(8,145,178,0.4);
    border-radius: 0 6px 6px 0; padding: 0.4rem 0.65rem; font-size: 0.7rem;
    color: #2A6A88 !important; margin: 0.25rem 0 0.45rem; line-height: 1.5;
}
.sb-hint b { color: #0891B2 !important; font-family: 'DM Mono', monospace; }
.sb-hint-warn {
    background: rgba(245,158,11,0.05); border-left: 2px solid rgba(245,158,11,0.35);
    border-radius: 0 6px 6px 0; padding: 0.38rem 0.65rem; font-size: 0.7rem;
    color: #8A6A10 !important; margin: 0.25rem 0;
}
.sb-loan {
    border-left: 2px solid #0E2438; padding: 0.22rem 0 0.22rem 0.6rem;
    margin: 0.12rem 0; font-size: 0.71rem; color: #3A6A88 !important;
}
.sb-loan span { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: #0891B2 !important; }

/* ── LANDING PAGE */
.lp { max-width: 1040px; margin: 0 auto; padding: 1.5rem 0 3rem; }

.lp-hero {
    position: relative; border-radius: 18px; overflow: hidden;
    padding: 3.25rem 2.75rem 2.85rem; margin-bottom: 1.75rem;
    background: linear-gradient(140deg, #040E1C 0%, #061728 55%, #040C18 100%);
    border: 1px solid #0E2438;
    box-shadow: 0 0 60px rgba(8,145,178,0.06), 0 24px 70px rgba(0,0,0,0.5);
}
.lp-hero::before {
    content: ''; position: absolute; inset: 0;
    background-image: radial-gradient(rgba(8,145,178,0.16) 1px, transparent 1px);
    background-size: 26px 26px; pointer-events: none;
}
.lp-hero::after {
    content: ''; position: absolute; top: 0; left: 8%; right: 8%; height: 2px;
    background: linear-gradient(90deg, transparent, #0891B2 30%, #22D3EE 55%, #0891B2 80%, transparent);
    box-shadow: 0 0 16px rgba(8,145,178,0.65);
}
.lp-eye {
    font-size: 0.67rem; font-weight: 700; letter-spacing: 0.17em;
    text-transform: uppercase; color: #0891B2; margin-bottom: 0.8rem;
    position: relative; display: flex; align-items: center; gap: 0.5rem;
}
.lp-eye::before { content: ''; width: 18px; height: 1px; background: #0891B2; }
.lp-title {
    font-size: 2.55rem; font-weight: 700; color: #fff;
    letter-spacing: -0.04em; line-height: 1.1; margin-bottom: 0.8rem;
    position: relative;
}
.lp-title span { color: #22D3EE; }
.lp-desc {
    font-size: 0.95rem; color: #3A6A88; max-width: 520px;
    line-height: 1.72; margin-bottom: 1.65rem; position: relative;
}
.lp-tags { display: flex; flex-wrap: wrap; gap: 0.45rem; position: relative; }
.lp-tag {
    background: rgba(8,145,178,0.07); border: 1px solid rgba(8,145,178,0.18);
    border-radius: 99px; padding: 0.26rem 0.82rem; font-size: 0.68rem;
    font-weight: 600; color: #3A7A94; letter-spacing: 0.03em;
}

.lp-metrics {
    position: absolute; right: 2.75rem; top: 50%; transform: translateY(-50%);
    display: flex; flex-direction: column; gap: 0.65rem;
}
.lp-met {
    background: rgba(8,145,178,0.06); border: 1px solid rgba(8,145,178,0.16);
    border-radius: 10px; padding: 0.55rem 1.1rem; text-align: right; min-width: 130px;
}
.lp-met-v {
    font-family: 'DM Mono', monospace; font-size: 1.28rem; font-weight: 600;
    color: #0891B2; line-height: 1;
}
.lp-met-l {
    font-size: 0.6rem; color: #1A4A62; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase; margin-top: 0.18rem;
}

.lp-steps {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 0.9rem; margin-bottom: 1.35rem;
}
.lp-sc {
    background: #07121E; border: 1px solid #0E2438; border-radius: 13px;
    padding: 1.4rem 1.25rem; transition: border-color 0.18s, transform 0.18s;
}
.lp-sc:hover { border-color: rgba(8,145,178,0.35); transform: translateY(-2px); }
.lp-sc-n {
    font-family: 'DM Mono', monospace; font-size: 0.62rem; font-weight: 600;
    color: #0891B2; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.65rem;
}
.lp-sc-ico { font-size: 1.45rem; margin-bottom: 0.55rem; display: block; }
.lp-sc-t { font-size: 0.95rem; font-weight: 700; color: #BDD8EE; margin-bottom: 0.4rem; }
.lp-sc-d { font-size: 0.78rem; color: #2A5070; line-height: 1.6; }

.lp-feats {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.7rem; margin-bottom: 1.35rem;
}
.lp-ft {
    background: #07121E; border: 1px solid #0E2438; border-radius: 11px;
    padding: 1rem; transition: border-color 0.18s;
}
.lp-ft:hover { border-color: #163858; }
.lp-ft-i { font-size: 1.15rem; margin-bottom: 0.45rem; }
.lp-ft-t { font-size: 0.8rem; font-weight: 700; color: #BDD8EE; margin-bottom: 0.18rem; }
.lp-ft-d { font-size: 0.72rem; color: #2A5070; line-height: 1.52; }

.lp-cta {
    background: linear-gradient(135deg, #07121E, #061020);
    border: 1px solid rgba(8,145,178,0.22); border-radius: 13px;
    padding: 1.4rem 1.85rem; display: flex; align-items: center;
    justify-content: space-between; gap: 1rem;
}
.lp-cta-l h3 { font-size: 1rem; font-weight: 700; color: #C8E6F4; margin-bottom: 0.18rem; }
.lp-cta-l p { font-size: 0.78rem; color: #2A5070; margin: 0; }
.lp-cta-r {
    background: linear-gradient(135deg, #0891B2, #0669A0);
    color: #E8F6FF; font-weight: 700; font-size: 0.83rem;
    padding: 0.58rem 1.4rem; border-radius: 8px; white-space: nowrap;
    box-shadow: 0 4px 16px rgba(8,145,178,0.32);
}

@media (max-width: 800px) {
    .lp-steps, .lp-feats { grid-template-columns: 1fr; }
    .lp-metrics { display: none; }
    .lp-title { font-size: 1.7rem; }
    .lp-cta { flex-direction: column; }
    .coll-grid { grid-template-columns: repeat(2, 1fr); }
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
    existing_od = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional OD")
    existing_tl = sum(l['Principal'] for l in existing_loans if l['Loan Type'] == "Professional T/L")
    new_od = existing_od + (l_amt if l_type == "Professional OD" else 0.0)
    new_tl = existing_tl + (l_amt if l_type == "Professional T/L" else 0.0)
    if l_type == "Professional OD" and new_od > PROFESSIONAL_OD_CAP:
        return False, f"Professional OD total (Rs. {new_od:,.0f}) would exceed the individual cap of Rs. {PROFESSIONAL_OD_CAP:,.0f}."
    if l_type == "Professional T/L" and new_tl > PROFESSIONAL_TL_CAP:
        return False, f"Professional T/L total (Rs. {new_tl:,.0f}) would exceed the individual cap of Rs. {PROFESSIONAL_TL_CAP:,.0f}."
    if (new_od + new_tl) > PROFESSIONAL_COMBINED_CAP:
        return False, f"Combined Professional OD + T/L total (Rs. {(new_od+new_tl):,.0f}) would exceed the combined cap of Rs. {PROFESSIONAL_COMBINED_CAP:,.0f}."
    return True, ""


# ==========================================
# 🧮 PORTFOLIO LTV ENGINE  — LOGIC UNCHANGED
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
    assigned_collateral_ids = {cid for cid, users in collateral_usage.items() if users}
    pool_collateral_ids = {s['id'] for s in fmv_sources if s['id'] not in assigned_collateral_ids}
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
                share = (cid_fmv * (sl['Principal'] / total_principal) if total_principal > 0 else cid_fmv / len(sharing_loans))
                if sl['_loan_id'] in loan_collateral_shares:
                    loan_collateral_shares[sl['_loan_id']][cid] = share
    loan_assigned_fmv = {}
    for loan in loans:
        lid = loan['_loan_id']
        loan_assigned_fmv[lid] = sum(loan_collateral_shares.get(lid, {}).values()) if loan.get('collateral_mode') == 'assigned' else 0.0
    pool_fmv = sum(s['Amount'] for s in fmv_sources if s['id'] in pool_collateral_ids)

    def waterfall_sort_key(loan):
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None: return (2, 0)
        return (0 if max_ltv <= 50 else 1, -loan['Principal'])

    pool_participating = [l for l in loans if policy.get(l['Loan Type']) is not None and l.get('collateral_mode', 'pool') == 'pool']
    pool_participating_sorted = sorted(pool_participating, key=waterfall_sort_key)
    remaining_pool = pool_fmv
    pool_alloc = {}
    last_idx = len(pool_participating_sorted) - 1
    for i, loan in enumerate(pool_participating_sorted):
        lid = loan['_loan_id']
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            pool_alloc[lid] = 0.0; continue
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
            results.append({**loan, 'Max LTV%': None, 'Assigned FMV': 0.0, 'Pool FMV': 0.0, 'Total FMV': 0.0, 'LTV%': None, 'Pass_Status': True, 'Is_Unsecured': True, 'Collateral_Mode': mode, 'Collateral_Names': [], 'Shared_Collateral_Ids': []})
            continue
        assigned_fmv_val = loan_assigned_fmv.get(lid, 0.0)
        pool_fmv_val = pool_alloc.get(lid, 0.0)
        total_alloc = assigned_fmv_val + pool_fmv_val
        ltv_pct = principal / total_alloc * 100.0 if total_alloc > 0 else float('inf')
        passes = (ltv_pct <= max_ltv) if total_alloc > 0 else False
        assigned_coll_names = _get_collateral_names(loan.get('assigned_collateral_ids', []), fmv_sources)
        shared_cids = [cid for cid in loan.get('assigned_collateral_ids', []) if len(collateral_usage.get(cid, [])) > 1]
        results.append({**loan, 'Max LTV%': max_ltv, 'Assigned FMV': assigned_fmv_val, 'Pool FMV': pool_fmv_val, 'Total FMV': total_alloc, 'LTV%': ltv_pct, 'Pass_Status': passes, 'Is_Unsecured': False, 'Collateral_Mode': mode, 'Collateral_Names': assigned_coll_names, 'Shared_Collateral_Ids': shared_cids})

    secured_results = [r for r in results if not r['Is_Unsecured']]
    total_secured_principal = sum(r['Principal'] for r in secured_results)
    total_exposure = sum(r['Principal'] for r in results)
    total_alloc_fmv = sum(r['Total FMV'] for r in secured_results)
    wtd_ltv = total_secured_principal / total_alloc_fmv * 100.0 if total_alloc_fmv > 0 else 0.0
    aggregate_ltv = total_secured_principal / total_fmv * 100.0 if total_fmv > 0 else 0.0
    overall_pass = all(r['Pass_Status'] for r in results)
    return results, {
        'total_fmv': total_fmv, 'pool_fmv': pool_fmv, 'remaining_pool': remaining_pool,
        'total_exposure': total_exposure, 'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv, 'wtd_ltv': wtd_ltv, 'aggregate_ltv': aggregate_ltv,
        'overall_pass': overall_pass, 'collateral_usage': collateral_usage,
        'assigned_collateral_ids': assigned_collateral_ids, 'pool_collateral_ids': pool_collateral_ids,
    }


# ==========================================
# 📄 PDF ENGINE — LOGIC UNCHANGED
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
        self.cell(0, 10, safe_str(f'Page {self.page_no()} | LTV Engine | {datetime.now().strftime("%B %d, %Y")}'), 0, 0, 'C')


def generate_pdf(client_name, results, fmv_sources, summary):
    pdf = PDFReport()
    pdf.add_page()
    total_fmv = summary['total_fmv']
    total_exposure = summary['total_exposure']
    aggregate_ltv = summary['aggregate_ltv']
    overall_pass = summary['overall_pass']
    total_secured_p = summary['total_secured_principal']

    pdf.set_font("Arial", "B", 12); pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "EXECUTIVE SUMMARY", 0, 1)
    pdf.set_draw_color(226, 232, 240); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(4)

    def kv(label, value):
        pdf.set_font("Arial", "", 10); pdf.cell(80, 6, safe_str(label), 0, 0)
        pdf.set_font("Arial", "B", 10); pdf.cell(0, 6, safe_str(str(value)), 0, 1)

    kv("Client Name:", client_name)
    kv("Analysis Date:", datetime.now().strftime("%B %d, %Y"))
    kv("Total Secured Exposure:", f"Rs. {total_secured_p:,.2f}")
    kv("Total Loan Exposure (All Facilities):", f"Rs. {total_exposure:,.2f}")
    kv("Total Collateral FMV:", f"Rs. {total_fmv:,.2f}")
    kv("Aggregate LTV%:", f"{aggregate_ltv:.2f}%")
    pdf.ln(3)
    res_text = "APPROVED - Within LTV Limits" if overall_pass else "DECLINED - Exceeds LTV Limits"
    pdf.set_text_color(5, 150, 105) if overall_pass else pdf.set_text_color(220, 38, 38)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, safe_str(f"Assessment Result: {res_text}"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "COLLATERAL / FMV SOURCES", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)
    col_w_fmv = [70, 35, 25, 60]
    pdf.set_font("Arial", "B", 7); pdf.set_fill_color(237, 233, 254)
    for h, w in zip(["Plot / Property Reference", "FMV (Rs.)", "Type", "Owner"], col_w_fmv):
        pdf.cell(w, 7, h, 1, 0, 'C', fill=True)
    pdf.ln()
    pdf.set_font("Arial", "", 8)
    assigned_ids = summary['assigned_collateral_ids']
    for i, src in enumerate(fmv_sources):
        fid = src.get('id', i); fill = (i % 2 == 0)
        pdf.set_fill_color(248, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        ctype = "Assigned" if fid in assigned_ids else "Pool"
        owner = src.get('Owner', '—') or '—'
        pdf.cell(col_w_fmv[0], 6, safe_str(src['Plot']), 1, 0, 'L', fill)
        pdf.cell(col_w_fmv[1], 6, f"{src['Amount']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w_fmv[2], 6, safe_str(ctype), 1, 0, 'C', fill)
        pdf.cell(col_w_fmv[3], 6, safe_str(owner[:30]), 1, 1, 'L', fill)
    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w_fmv[0], 6, "TOTAL", 1, 0, 'R', True)
    pdf.cell(col_w_fmv[1], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w_fmv[2] + col_w_fmv[3], 6, "", 1, 1, '', True)

    pdf.ln(5); pdf.set_font("Arial", "B", 12); pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "FACILITY LTV BREAKDOWN", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(3)
    col_w = [40, 20, 20, 20, 18, 14, 14, 24, 20]
    hdrs = ["Facility Type", "Principal", "Asgn.FMV", "Pool FMV", "Tot.FMV", "LTV%", "Max%", "Surplus/(Dfct)", "Status"]
    pdf.set_font("Arial", "B", 7); pdf.set_fill_color(237, 233, 254)
    for i, h in enumerate(hdrs):
        pdf.cell(col_w[i], 7, h, 1, 0, 'C', fill=True)
    pdf.ln()

    def display_sort(r):
        m = r.get('Max LTV%')
        if m is None: return (2, 0)
        return (0 if m <= 50 else 1, -(r.get('Principal', 0)))

    for idx, row in enumerate(sorted(results, key=display_sort)):
        fill = (idx % 2 == 0)
        pdf.set_fill_color(248, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        is_unsec = row.get('Is_Unsecured', False)
        max_ltv = row.get('Max LTV%'); ltv_val = row.get('LTV%')
        ltv_disp = "N/A" if (is_unsec or ltv_val is None) else f"{ltv_val:.1f}%"
        max_disp = "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%"
        asgn_disp = "N/A" if is_unsec else f"{row['Assigned FMV']:,.0f}"
        pool_disp = "N/A" if is_unsec else f"{row['Pool FMV']:,.0f}"
        total_disp = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"
        if is_unsec or max_ltv is None:
            surplus_disp = "N/A"; surplus_val = None
        else:
            req_fmv = row['Principal'] / (max_ltv / 100.0)
            actual_fmv = row.get('Total FMV', 0.0); surplus_val = actual_fmv - req_fmv
            surplus_disp = f"+{surplus_val:,.0f}" if surplus_val >= 0 else f"({abs(surplus_val):,.0f})"
        status = "PASS" if row['Pass_Status'] else "FAIL"
        pdf.set_font("Arial", "", 8)
        pdf.cell(col_w[0], 6, safe_str(row['Loan Type']), 1, 0, 'L', fill)
        pdf.cell(col_w[1], 6, f"{row['Principal']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w[2], 6, safe_str(asgn_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[3], 6, safe_str(pool_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[4], 6, safe_str(total_disp), 1, 0, 'R', fill)
        pdf.cell(col_w[5], 6, safe_str(ltv_disp), 1, 0, 'C', fill)
        pdf.cell(col_w[6], 6, safe_str(max_disp), 1, 0, 'C', fill)
        if surplus_val is None: pdf.set_text_color(100, 116, 139)
        elif surplus_val >= 0: pdf.set_text_color(5, 150, 105)
        else: pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[7], 6, safe_str(surplus_disp), 1, 0, 'R', fill)
        pdf.set_text_color(0, 0, 0)
        pdf.set_text_color(5, 150, 105) if status == "PASS" else pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[8], 6, status, 1, 1, 'C', fill)
        pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", "B", 8); pdf.set_fill_color(237, 233, 254)
    pdf.cell(col_w[0], 6, "AGGREGATE (ALL FACILITIES)", 1, 0, 'L', True)
    pdf.cell(col_w[1], 6, f"{total_exposure:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[2], 6, "-", 1, 0, 'R', True)
    pdf.cell(col_w[3], 6, "-", 1, 0, 'R', True)
    pdf.cell(col_w[4], 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(col_w[5], 6, f"{aggregate_ltv:.1f}%", 1, 0, 'C', True)
    pdf.cell(col_w[6], 6, "-", 1, 0, 'C', True)
    pdf.cell(col_w[7], 6, "-", 1, 0, 'R', True)
    pdf.cell(col_w[8], 6, "PASS" if overall_pass else "FAIL", 1, 1, 'C', True)
    pdf.ln(2); pdf.set_font("Arial", "I", 7); pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, safe_str("Surplus/(Dfct): +value = excess collateral  |  (value) = shortfall"), 0, 1, 'L')
    pdf.cell(0, 5, safe_str("Aggregate LTV% computed on secured principal vs total FMV only."), 0, 1, 'L')
    pdf.set_text_color(0, 0, 0)
    pdf_data = pdf.output(dest='S')
    return pdf_data.encode('latin-1') if isinstance(pdf_data, str) else bytes(pdf_data)


# ==========================================
# 📐 SIDEBAR — Loan facility only
# ==========================================
with st.sidebar:
    st.markdown(f"""
        <div style="padding:.4rem 0 .2rem;">
            <div style="display:flex;align-items:center;gap:.55rem;margin-bottom:.7rem;">
                <span style="font-size:1.25rem;">🏦</span>
                <div>
                    <div style="font-size:.85rem;font-weight:700;color:#C8E6F4 !important;">LTV Engine</div>
                    <div style="font-size:.6rem;color:#0891B2 !important;font-weight:600;letter-spacing:.1em;text-transform:uppercase;">Credit Risk Division</div>
                </div>
            </div>
            <div style="background:rgba(8,145,178,.06);border:1px solid rgba(8,145,178,.18);border-radius:7px;padding:.32rem .68rem;display:flex;align-items:center;justify-content:space-between;">
                <span style="font-size:.7rem;color:#5A8AA8 !important;">👤 {st.session_state['auth_username']}</span>
                <span style="font-size:.58rem;color:#0891B2 !important;font-weight:700;letter-spacing:.07em;">ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Sign Out", type="primary", use_container_width=True):
        st.session_state.update({"authenticated": False, "auth_username": "", "_login_error": ""})
        st.rerun()

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-step"><span class="sb-num">1</span>Add Loan Facility</div>', unsafe_allow_html=True)

    policy_dict = get_policy_dict()
    loan_type_list = list(policy_dict.keys())

    if loan_type_list:
        l_type = st.selectbox("Facility Type", loan_type_list, key="sb_loan_type",
                              help="Credit facility type")
        l_amt = st.number_input("Principal Amount (Rs.)", step=10000.0, min_value=0.0,
                                key="sb_loan_principal", help="Sanctioned or proposed loan amount")
        max_ltv_sel = policy_dict.get(l_type)

        # Smart hints
        if max_ltv_sel is not None and l_amt > 0:
            req_fmv = l_amt / (max_ltv_sel / 100.0)
            pool_avail = sum(s['Amount'] for s in st.session_state.fmv_sources)
            ok = pool_avail >= req_fmv
            st.markdown(
                f'<div class="sb-hint">Policy max: <b>{max_ltv_sel:.0f}%</b><br>'
                f'Required FMV: <b>Rs. {req_fmv:,.0f}</b><br>'
                f'{"✅" if ok else "⚠️"} Pool FMV: <b>Rs. {pool_avail:,.0f}</b></div>',
                unsafe_allow_html=True
            )
        elif max_ltv_sel is None:
            cap_lbl = ""
            if l_type == "Professional OD":
                cap_lbl = f"Individual cap: Rs. {PROFESSIONAL_OD_CAP:,.0f}"
            elif l_type == "Professional T/L":
                cap_lbl = f"Individual cap: Rs. {PROFESSIONAL_TL_CAP:,.0f}"
            st.markdown(
                f'<div class="sb-hint-warn">⚡ Unsecured — no collateral required'
                + (f'<br>{cap_lbl}' if cap_lbl else '') + '</div>',
                unsafe_allow_html=True
            )

        selected_colls = []
        coll_mode = "pool"

        if max_ltv_sel is not None:
            use_dedicated = st.checkbox("🔒 Assign dedicated collateral(s)?", value=False, key="sb_use_dedicated",
                                        help="Uncheck = shared waterfall pool. Check = pin specific properties.")
            coll_mode = "assigned" if use_dedicated else "pool"
            if use_dedicated:
                if st.session_state.fmv_sources:
                    already_assigned = _get_assigned_in_use()
                    coll_options = {}
                    for s in st.session_state.fmv_sources:
                        sid = s.get('id')
                        base = f"{s.get('Plot','?')} — Rs.{s.get('Amount',0):,.0f}"
                        label = f"⚠️ {base} [in use]" if sid in already_assigned else f"✅ {base}"
                        coll_options[label] = sid
                    sel_labels = st.multiselect("Select Collateral(s)", options=list(coll_options.keys()), key="sb_sel_colls")
                    selected_colls = [coll_options[lbl] for lbl in sel_labels]
                    if selected_colls and max_ltv_sel and l_amt > 0:
                        sel_fmv = sum(s['Amount'] for s in st.session_state.fmv_sources if s.get('id') in selected_colls)
                        req = l_amt / (max_ltv_sel / 100.0)
                        ok2 = sel_fmv >= req
                        if any(c in already_assigned for c in selected_colls):
                            st.warning("⚠️ Shared property — FMV split proportionally.")
                        else:
                            st.markdown(
                                f'<div class="sb-hint">Selected FMV: <b>Rs. {sel_fmv:,.0f}</b><br>'
                                f'Required: <b>Rs. {req:,.0f}</b> {"✅" if ok2 else "⚠️ Shortfall"}</div>',
                                unsafe_allow_html=True
                            )
                else:
                    st.warning("⚠️ Add properties first (main page above)")

        if st.button("Add to Portfolio", type="primary", use_container_width=True):
            if l_amt <= 0:
                st.error("Principal must be greater than zero.")
            elif coll_mode == "assigned" and not selected_colls:
                st.error("Select at least one property for dedicated mode.")
            else:
                cap_ok, cap_msg = _check_professional_caps(l_type, l_amt, st.session_state.loans)
                if not cap_ok:
                    st.error(f"🚫 {cap_msg}")
                else:
                    lid = st.session_state.loan_id_counter
                    st.session_state.loan_id_counter += 1
                    st.session_state.loans.append({
                        "Loan Type": l_type, "Principal": l_amt, "_loan_id": lid,
                        "collateral_mode": coll_mode, "assigned_collateral_ids": selected_colls,
                    })
                    st.success(f"Added — {'🔒 Dedicated' if coll_mode=='assigned' else '🌊 Pool'}")
                    st.rerun()

    # Portfolio list
    if st.session_state.loans:
        st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
        total_exp_sb = sum(l['Principal'] for l in st.session_state.loans)
        st.markdown(
            f'<div class="sb-stat">Portfolio &nbsp;·&nbsp; <b>Rs. {total_exp_sb:,.0f}</b>'
            f' &nbsp;·&nbsp; {len(st.session_state.loans)} facilities</div>',
            unsafe_allow_html=True
        )
        for loan in st.session_state.loans:
            mi = {"pool": "🌊", "assigned": "🔒"}.get(loan.get('collateral_mode', 'pool'), "🌊")
            st.markdown(
                f'<div class="sb-loan">{mi} {loan["Loan Type"]}<br>'
                f'<span>Rs. {loan["Principal"]:,.0f}</span></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
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
# 🖥️ MAIN AREA
# ==========================================
st.markdown(
    '<div style="font-size:1.55rem;font-weight:700;color:#E8F6FF;letter-spacing:-0.025em;'
    'line-height:1.1;margin-bottom:1rem;">LTV Analysis Engine</div>',
    unsafe_allow_html=True
)

# ==========================================
# 🏠 COLLATERAL REGISTER — always visible
# ==========================================
st.markdown("""
<div class="sec-head">
    <span class="sec-head-lbl">🏠 Collateral Register</span>
    <div class="sec-head-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Horizontal entry form
with st.form("prop_form", clear_on_submit=True):
    f1, f2, f3, f4 = st.columns([3, 2.2, 2, 1])
    with f1:
        form_plot = st.text_input(
            "Property Reference",
            placeholder="e.g. Plot 42-B, Sector 7, New Delhi",
            help="Legal description or plot reference from title deed"
        )
    with f2:
        form_owner = st.text_input(
            "Owner / Mortgagor Name",
            placeholder="e.g. Ramesh Kumar Sharma",
            help="Registered owner as per title deed"
        )
    with f3:
        form_fmv = st.number_input(
            "Fair Market Value (Rs.)",
            min_value=0.0, step=50000.0,
            help="Valuation from approved valuer report"
        )
    with f4:
        st.markdown('<div style="padding-top:1.72rem"></div>', unsafe_allow_html=True)
        prop_submitted = st.form_submit_button(
            "Add →", use_container_width=True, type="primary"
        )

if prop_submitted:
    if not form_plot.strip():
        st.error("Property reference is required.")
    elif form_fmv <= 0:
        st.error("Fair Market Value must be greater than zero.")
    else:
        fid = _next_fmv_id()
        st.session_state.fmv_sources.append({
            "id": fid,
            "Plot": form_plot.strip(),
            "Owner": form_owner.strip(),
            "Amount": form_fmv,
        })
        st.rerun()

# ── Property card grid
assigned_in_use_main = _get_assigned_in_use()

if st.session_state.fmv_sources:
    total_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources)
    n_pool_all = sum(1 for s in st.session_state.fmv_sources if s.get('id') not in assigned_in_use_main)
    n_asgn_all = sum(1 for s in st.session_state.fmv_sources if s.get('id') in assigned_in_use_main)
    pool_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources if s.get('id') not in assigned_in_use_main)
    asgn_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources if s.get('id') in assigned_in_use_main)

    st.markdown(
        f'<div class="coll-summary">'
        f'<span class="coll-sum-pill sum-total">📦 {len(st.session_state.fmv_sources)} properties &nbsp;·&nbsp; Rs. {total_fmv_all:,.0f} total FMV</span>'
        f'<span class="coll-sum-pill sum-pool">🌊 Pool: {n_pool_all} &nbsp;·&nbsp; Rs. {pool_fmv_all:,.0f}</span>'
        + (f'<span class="coll-sum-pill sum-asgn">🔒 Assigned: {n_asgn_all} &nbsp;·&nbsp; Rs. {asgn_fmv_all:,.0f}</span>' if n_asgn_all else '')
        + '</div>',
        unsafe_allow_html=True
    )

    per_row = 4
    srcs = st.session_state.fmv_sources
    for row_start in range(0, len(srcs), per_row):
        chunk = srcs[row_start: row_start + per_row]
        cols = st.columns(per_row)
        for j, src in enumerate(chunk):
            sid = src.get('id', '?')
            is_asgn = sid in assigned_in_use_main
            badge = ('<span class="coll-card-badge badge-asgn">🔒 Assigned</span>'
                     if is_asgn else
                     '<span class="coll-card-badge badge-pool">🌊 Pool</span>')
            owner_txt = src.get('Owner', '') or '—'
            with cols[j]:
                st.markdown(f"""
                <div class="coll-card">
                    {badge}
                    <div class="coll-card-ref" title="{src.get('Plot','')}">
                        {src.get('Plot','')}
                    </div>
                    <div class="coll-card-owner">👤 {owner_txt}</div>
                    <div class="coll-card-fmv">Rs.&nbsp;{src.get('Amount',0):,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✕ Remove", key=f"rm_prop_{sid}", use_container_width=True):
                    st.session_state.fmv_sources = [
                        s for s in st.session_state.fmv_sources if s.get('id') != sid
                    ]
                    for loan in st.session_state.loans:
                        asgn = loan.get('assigned_collateral_ids', [])
                        if sid in asgn:
                            asgn.remove(sid)
                    st.rerun()
else:
    st.markdown("""
    <div class="coll-empty">
        <div class="coll-empty-icon">🏠</div>
        <div class="coll-empty-title">No properties registered</div>
        <div class="coll-empty-sub">Enter a property reference, owner name and FMV above, then click Add →</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 🏠 LANDING PAGE (no loans yet)
# ==========================================
if not st.session_state.loans:
    st.markdown("""
    <div class="lp">
      <div class="lp-hero">
        <div class="lp-eye">Credit Risk · Institutional Analysis</div>
        <div class="lp-title">Institutional-Grade<br><span>LTV Analysis</span></div>
        <div class="lp-desc">
            Precision loan-to-value assessment with multi-collateral waterfall allocation,
            dedicated assignment, and one-click audit-ready PDF reporting.
        </div>
        <div class="lp-tags">
            <span class="lp-tag">✦ Waterfall Engine</span>
            <span class="lp-tag">✦ Dedicated Assignment</span>
            <span class="lp-tag">✦ Surplus &amp; Shortfall</span>
            <span class="lp-tag">✦ PDF Export</span>
            <span class="lp-tag">✦ 16 Facility Types</span>
        </div>
        <div class="lp-metrics">
            <div class="lp-met"><div class="lp-met-v">16</div><div class="lp-met-l">Facility Types</div></div>
            <div class="lp-met"><div class="lp-met-v">50–80%</div><div class="lp-met-l">LTV Range</div></div>
            <div class="lp-met"><div class="lp-met-v">∞</div><div class="lp-met-l">Properties</div></div>
        </div>
      </div>

      <div class="lp-steps">
        <div class="lp-sc">
          <div class="lp-sc-n">STEP 01</div>
          <div class="lp-sc-ico">🏠</div>
          <div class="lp-sc-t">Register Collateral</div>
          <div class="lp-sc-d">Enter each property with owner name and Fair Market Value using the register above. Properties join the shared waterfall pool or can be pinned to a specific facility.</div>
        </div>
        <div class="lp-sc">
          <div class="lp-sc-n">STEP 02</div>
          <div class="lp-sc-ico">📋</div>
          <div class="lp-sc-t">Add Loan Facilities</div>
          <div class="lp-sc-d">Use the sidebar to select a facility type and principal. Choose Shared Pool (waterfall order) or Dedicated Assignment to lock specific properties to a single loan.</div>
        </div>
        <div class="lp-sc">
          <div class="lp-sc-n">STEP 03</div>
          <div class="lp-sc-ico">📊</div>
          <div class="lp-sc-t">Analyse &amp; Export</div>
          <div class="lp-sc-d">Review per-facility LTV%, surplus or shortfall, and aggregate portfolio LTV. Download a structured PDF report for credit committee review.</div>
        </div>
      </div>

      <div class="lp-feats">
        <div class="lp-ft"><div class="lp-ft-i">🧮</div><div class="lp-ft-t">Waterfall Allocation</div><div class="lp-ft-d">Stricter 50% LTV loans funded first — strict policy priority throughout.</div></div>
        <div class="lp-ft"><div class="lp-ft-i">🔒</div><div class="lp-ft-t">Dedicated Assignment</div><div class="lp-ft-d">Pin any property exclusively to a facility. FMV split proportionally when shared.</div></div>
        <div class="lp-ft"><div class="lp-ft-i">📐</div><div class="lp-ft-t">Surplus &amp; Shortfall</div><div class="lp-ft-d">Per-facility excess collateral or deficit shown inline and in PDF.</div></div>
        <div class="lp-ft"><div class="lp-ft-i">👤</div><div class="lp-ft-t">Owner Tracking</div><div class="lp-ft-d">Mortgagor name recorded per property and printed on every report.</div></div>
      </div>

      <div class="lp-cta">
        <div class="lp-cta-l">
          <h3>Ready to begin?</h3>
          <p>Register properties above, then add loan facilities using the sidebar.</p>
        </div>
        <div class="lp-cta-r">← Sidebar: Add Facilities</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.fmv_sources:
    st.warning("⚠️ Register at least one property above before running the analysis.")
    st.stop()

# ── Run engine
results, summary = run_portfolio_ltv(st.session_state.loans, st.session_state.fmv_sources)
total_fmv = summary['total_fmv']
total_exposure = summary['total_exposure']
total_secured_principal = summary['total_secured_principal']
total_alloc_fmv = summary['total_alloc_fmv']
wtd_ltv = summary['wtd_ltv']
aggregate_ltv = summary['aggregate_ltv']
overall_pass = summary['overall_pass']

# ── KPI Row
st.markdown('<div style="margin-top:.75rem"></div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="kpi">
        <div class="kpi-lbl">Total Exposure</div>
        <div class="kpi-val">Rs.&nbsp;{total_exposure:,.0f}</div>
        <div class="kpi-sub">{len(st.session_state.loans)} facilities</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi">
        <div class="kpi-lbl">Total Collateral FMV</div>
        <div class="kpi-val">Rs.&nbsp;{total_fmv:,.0f}</div>
        <div class="kpi-sub kpi-pos">{len(st.session_state.fmv_sources)} properties</div>
    </div>""", unsafe_allow_html=True)
with k3:
    wc = "#10B981" if wtd_ltv <= 50 else ("#F59E0B" if wtd_ltv <= 65 else "#EF4444")
    gc = "g-ok" if wtd_ltv <= 50 else ("g-warn" if wtd_ltv <= 65 else "g-fail")
    st.markdown(f"""<div class="kpi">
        <div class="kpi-lbl">Weighted Avg LTV</div>
        <div class="kpi-val" style="color:{wc};">{wtd_ltv:.2f}%</div>
        <div class="gauge"><div class="{gc}" style="width:{min(wtd_ltv,100):.1f}%"></div></div>
    </div>""", unsafe_allow_html=True)
with k4:
    agc = "g-ok" if aggregate_ltv <= 50 else ("g-warn" if aggregate_ltv <= 65 else "g-fail")
    st.markdown(f"""<div class="kpi-accent">
        <div class="kpi-accent-lbl">Aggregate LTV</div>
        <div class="kpi-accent-val">{aggregate_ltv:.2f}%</div>
        <div class="kpi-accent-sub">Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
        <div class="gauge"><div class="{agc}" style="width:{min(aggregate_ltv,100):.1f}%"></div></div>
    </div>""", unsafe_allow_html=True)

# ── Status banner
if overall_pass:
    st.markdown('<div class="s-pass">✅ &nbsp;PORTFOLIO APPROVED — All Facilities Within LTV Policy Limits</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="s-fail">⚠️ &nbsp;PORTFOLIO DECLINED — One or More Facilities Exceed Maximum LTV</div>', unsafe_allow_html=True)

# ==========================================
# 📋 PORTFOLIO LTV BREAKDOWN TABLE
# ==========================================
st.markdown('<div class="sec-head"><span class="sec-head-lbl">📋 Portfolio LTV Breakdown</span><div class="sec-head-line"></div></div>', unsafe_allow_html=True)

def display_sort_key(r):
    m = r.get('Max LTV%')
    if m is None: return (2, 0)
    return (0 if m <= 50 else 1, -(r.get('Principal', 0)))

sorted_display = sorted(results, key=display_sort_key)
disp_rows = []
for r in sorted_display:
    is_unsec = r['Is_Unsecured']; ltv_val = r.get('LTV%'); max_ltv = r.get('Max LTV%')
    if is_unsec or max_ltv is None:
        surplus_disp = "N/A"
    else:
        req_fmv = r['Principal'] / (max_ltv / 100.0)
        sv = r.get('Total FMV', 0.0) - req_fmv
        surplus_disp = f"+Rs. {sv:,.0f}" if sv >= 0 else f"(Rs. {abs(sv):,.0f})"
    disp_rows.append({
        "Facility": r['Loan Type'],
        "Principal": f"Rs. {r['Principal']:,.0f}",
        "Assigned FMV": "N/A" if is_unsec else f"Rs. {r['Assigned FMV']:,.0f}",
        "Pool FMV": "N/A" if is_unsec else f"Rs. {r['Pool FMV']:,.0f}",
        "Total FMV": "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}",
        "LTV%": "N/A" if (is_unsec or ltv_val is None) else f"{ltv_val:.2f}%",
        "Max LTV": "N/A" if (is_unsec or max_ltv is None) else f"{max_ltv:.0f}%",
        "Surplus/(Shortfall)": surplus_disp,
        "Status": "✅ PASS" if r['Pass_Status'] else "❌ FAIL",
    })

disp_rows.append({
    "Facility": "── AGGREGATE ──",
    "Principal": f"Rs. {total_exposure:,.0f}",
    "Assigned FMV": "—", "Pool FMV": "—",
    "Total FMV": f"Rs. {total_fmv:,.0f}",
    "LTV%": f"{aggregate_ltv:.2f}%", "Max LTV": "—",
    "Surplus/(Shortfall)": "—",
    "Status": "✅ PASS" if aggregate_ltv <= 70 else "❌ FAIL",
})
st.dataframe(pd.DataFrame(disp_rows), hide_index=True, use_container_width=True)

# ==========================================
# 📊 LTV VISUAL SUMMARY
# ==========================================
st.markdown('<div class="sec-head"><span class="sec-head-lbl">📊 LTV Visual Summary</span><div class="sec-head-line"></div></div>', unsafe_allow_html=True)

secured_disp = [r for r in sorted_display if not r['Is_Unsecured']]
if secured_disp:
    num_cols = min(len(secured_disp) + 1, 4)
    bar_cols = st.columns(num_cols)
    for i, row in enumerate(secured_disp):
        ltv = row['LTV%'] if row['LTV%'] is not None else 0
        max_ltv = row['Max LTV%'] or 100
        pct = min((ltv / max_ltv) * 100, 100)
        fc = "g-ok" if ltv <= max_ltv * 0.8 else ("g-warn" if ltv <= max_ltv else "g-fail")
        sc = "#10B981" if row['Pass_Status'] else "#EF4444"
        mode = row.get('Collateral_Mode', 'pool')
        mb = {"pool": "🌊 Pool", "assigned": "🔒 Dedicated"}.get(mode, "🌊 Pool")
        cnames = row.get('Collateral_Names', [])
        ct = (", ".join(cnames[:2]) + ("…" if len(cnames) > 2 else "")) if cnames else "Pool"
        req_c = row['Principal'] / (max_ltv / 100.0)
        sv_c = row.get('Total FMV', 0.0) - req_c
        surp_html = (f"<span class='vc-surp-ok'>↑ Surplus Rs. {sv_c:,.0f}</span>" if sv_c >= 0
                     else f"<span class='vc-surp-bad'>↓ Short Rs. {abs(sv_c):,.0f}</span>")
        with bar_cols[i % num_cols]:
            st.markdown(f"""
            <div class="vc">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div class="vc-title">{row['Loan Type']}</div>
                    <div class="vc-mode">{mb}</div>
                </div>
                <div style="font-size:.62rem;color:#1A3A52;margin-bottom:.42rem;">🏠 {ct}</div>
                <div class="vc-pct" style="color:{sc};">{ltv:.2f}%</div>
                <div class="vc-meta">Max {max_ltv:.0f}% &nbsp;·&nbsp; FMV Rs.{row['Total FMV']:,.0f}</div>
                {surp_html}
                <div class="gauge" style="margin-top:.45rem;"><div class="{fc}" style="width:{pct:.1f}%"></div></div>
            </div>""", unsafe_allow_html=True)

    agg_col = len(secured_disp) % num_cols
    agc2 = "g-ok" if aggregate_ltv <= 50 else ("g-warn" if aggregate_ltv <= 65 else "g-fail")
    ac = "#10B981" if aggregate_ltv <= 70 else "#EF4444"
    with bar_cols[agg_col]:
        st.markdown(f"""
        <div class="vc-agg">
            <div style="font-size:.6rem;font-weight:700;color:#0891B2;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.32rem;">Aggregate</div>
            <div class="vc-pct" style="color:{ac};">{aggregate_ltv:.2f}%</div>
            <div style="font-size:.68rem;color:#0E5A72;margin-top:.08rem;">Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
            <div class="gauge" style="margin-top:.45rem;"><div class="{agc2}" style="width:{min(aggregate_ltv,100):.1f}%"></div></div>
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
            mi = {"pool": "🌊", "assigned": "🔒"}.get(loan.get('collateral_mode', 'pool'), "🌊")
            with lc1:
                st.markdown(f"**{mi} {loan['Loan Type']}** &nbsp; Rs. {loan['Principal']:,.0f}")
            with lc2:
                cnames = _get_collateral_names(loan.get('assigned_collateral_ids', []), st.session_state.fmv_sources)
                st.markdown(f"<span style='font-size:.77rem;color:#2A5070;'>{'  ·  '.join(cnames) if cnames else 'Shared Pool'}</span>", unsafe_allow_html=True)
            with lc3:
                if st.button("Remove", key=f"rm_loan_{loan['_loan_id']}"):
                    st.session_state.loans = [l for l in st.session_state.loans if l['_loan_id'] != loan['_loan_id']]
                    st.rerun()

# ── PDF Export
with st.expander("📄 Generate PDF Report", expanded=True):
    ec1, ec2 = st.columns([3, 1])
    with ec1:
        report_name = st.text_input(
            "Client / Portfolio Name",
            placeholder="e.g. Ramesh Kumar Sharma — Q3 Credit Review",
            label_visibility="collapsed",
            help="Name printed on the PDF report header"
        )
    with ec2:
        if st.button("Generate PDF", type="primary", use_container_width=True):
            if not report_name.strip():
                st.error("Enter a client or portfolio name.")
            else:
                with st.spinner("Generating report..."):
                    try:
                        pdf_bytes = generate_pdf(report_name.strip(), results, st.session_state.fmv_sources, summary)
                        safe_name = report_name.strip().replace(' ', '_').replace('/', '-').replace('\\', '-')
                        st.session_state['generated_pdf'] = pdf_bytes
                        st.session_state['generated_pdf_name'] = f"LTV_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
                        st.rerun()
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

    if 'generated_pdf' in st.session_state:
        st.markdown("---")
        st.success("✅ Report ready.")
        st.download_button(
            label="⬇️ Download PDF Report",
            data=st.session_state['generated_pdf'],
            file_name=st.session_state['generated_pdf_name'],
            mime="application/pdf",
            type="secondary",
        )
