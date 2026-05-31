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
        pw = st.secrets["passwords"]
        for k in pw:
            if str(k).strip() == str(username).strip():
                if str(pw[k]).strip() == str(password).strip():
                    return True
        return False
    except Exception:
        return False


def _show_login():
    # ── 1. CSS for card + honeypot
    st.markdown("""
    <style>
        #MainMenu, footer, header { visibility: hidden; }
        .stApp {
            background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%) !important;
        }
        .block-container { padding-top: 3rem !important; }

        /* ── Honeypot: invisible, catches browser autofill ── */
        .hp-wrap {
            position: absolute !important;
            left: -9999px !important;
            top: -9999px !important;
            opacity: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
            z-index: -1 !important;
        }

        /* ── Card ── */
        .login-card {
            background: #ffffff;
            border-radius: 20px;
            padding: 2.5rem 2rem 1.5rem;
            box-shadow: 0 8px 40px rgba(124,58,237,0.18);
            border: 1px solid #ede9fe;
        }
        .login-header { text-align: center; margin-bottom: 1.8rem; }
        .login-icon   { font-size: 3rem; line-height: 1; }
        .login-title  {
            font-size: 1.5rem; font-weight: 800; color: #1e1b4b;
            margin-top: 0.4rem; letter-spacing: -0.02em;
        }
        .login-badge {
            display: inline-block; background: #ede9fe; color: #6d28d9;
            font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
            text-transform: uppercase; padding: 0.2rem 0.8rem;
            border-radius: 99px; margin-top: 0.4rem;
        }
        .field-label {
            font-size: 0.75rem; font-weight: 700; color: #374151;
            text-transform: uppercase; letter-spacing: 0.07em;
            margin-bottom: 0.3rem; display: block;
        }
        .field-wrap { margin-bottom: 1rem; }
        div[data-testid="stTextInput"] > div > div > input {
            border-radius: 10px !important;
            border: 1.5px solid #e5e7eb !important;
            padding: 0.7rem 1rem !important;
            font-size: 0.95rem !important;
            background: #f9fafb !important;
            color: #111827 !important;
        }
        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: #7c3aed !important;
            box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
            background: #fff !important;
        }
        div[data-testid="stTextInput"] label { display: none !important; }
        div.stButton > button {
            background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
            color: white !important; border: none !important;
            border-radius: 10px !important; font-weight: 700 !important;
            font-size: 1rem !important; padding: 0.7rem !important;
            width: 100% !important;
            box-shadow: 0 4px 14px rgba(124,58,237,0.35) !important;
            transition: all 0.2s !important; margin-top: 0.5rem !important;
        }
        div.stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(124,58,237,0.45) !important;
        }
        .err-box {
            background: #fef2f2; border: 1.5px solid #fca5a5;
            color: #991b1b; border-radius: 10px;
            padding: 0.65rem 1rem; font-size: 0.85rem;
            font-weight: 600; margin-top: 0.8rem;
            text-align: center; line-height: 1.6;
        }
        .ok-box {
            background: #d1fae5; border: 1.5px solid #059669;
            color: #065f46; border-radius: 10px;
            padding: 0.65rem 1rem; font-size: 0.85rem;
            font-weight: 600; margin-top: 0.8rem;
            text-align: center; line-height: 1.6;
        }
        .login-footer {
            text-align: center; font-size: 0.72rem;
            color: #9ca3af; margin-top: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

    if "_login_error" not in st.session_state:
        st.session_state["_login_error"] = ""

    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        # ── 2. Card header (HTML)
        st.markdown("""
        <div class="login-card">
            <div class="login-header">
                <div class="login-icon">🏦</div>
                <div class="login-title">LTV Analysis Engine</div>
                <div class="login-badge">Secure Sign In</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 3. HONEYPOT: hidden fields that absorb browser autofill
        st.markdown('<div class="hp-wrap">', unsafe_allow_html=True)
        _hp_user = st.text_input("hp_u", key="_hp_u",
                                 label_visibility="collapsed")
        _hp_pass = st.text_input("hp_p", key="_hp_p",
                                 label_visibility="collapsed", type="password")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── 4. JavaScript to force-disable autofill on real inputs
        st.markdown("""
        <script>
        (function(){
            function disableAutofill(){
                document.querySelectorAll('input[type="text"],input[type="password"]')
                .forEach(function(inp){
                    var ph = (inp.placeholder||'').toLowerCase();
                    var sk = (inp.getAttribute('data-testid')||'').toLowerCase();
                    if(ph.indexOf('enter username')!==-1 || ph.indexOf('enter password')!==-1
                       || sk.indexOf('stTextInput')!==-1){
                        inp.setAttribute('autocomplete','off');
                        inp.setAttribute('name','_' + Math.random().toString(36).slice(2,8));
                    }
                });
            }
            disableAutofill();
            setTimeout(disableAutofill, 300);
            setTimeout(disableAutofill, 800);
            setTimeout(disableAutofill, 1500);
        })();
        </script>
        """, unsafe_allow_html=True)

        # ── 5. Real username field
        st.markdown("<span class='field-label'>👤 &nbsp;USER NAME</span>",
                    unsafe_allow_html=True)
        username = st.text_input(
            label="__user__",
            placeholder="e.g. admin",
            key="_u",
            label_visibility="collapsed",
        )

        # ── 6. Real password field
        st.markdown("<span class='field-label'>🔒 &nbsp;PASSWORD</span>",
                    unsafe_allow_html=True)
        password = st.text_input(
            label="__pass__",
            placeholder="Enter your password",
            type="password",
            key="_p",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        clicked = st.button("Sign In →", key="_signin_btn",
                            use_container_width=True)

        if clicked:
            u = str(username).strip()
            p = str(password).strip()

            if not u:
                st.session_state["_login_error"] = (
                    "⚠️ Please enter your username."
                )
                st.rerun()
            elif not p:
                st.session_state["_login_error"] = (
                    "⚠️ Please enter your password."
                )
                st.rerun()
            elif _check_credentials(u, p):
                st.session_state["authenticated"] = True
                st.session_state["auth_username"] = u
                st.session_state["_login_error"]  = ""
                st.rerun()
            else:
                try:
                    keys = list(st.secrets["passwords"].keys())
                except Exception:
                    keys = ["(unreadable)"]
                st.session_state["_login_error"] = "❌ Invalid username or password."
                
                st.rerun()

        err = st.session_state.get("_login_error", "")
        if err:
            st.markdown(f"<div class='err-box'>{err}</div>",
                        unsafe_allow_html=True)

        st.markdown(
            "<div class='login-footer'>"
            "🔐 Secured by Streamlit Cloud Secrets</div>",
            unsafe_allow_html=True,
        )


# ── Auth gate
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_username" not in st.session_state:
    st.session_state["auth_username"] = ""

if not st.session_state["authenticated"]:
    _show_login()
    st.stop()


# ==========================================
# 🎨 GLOBAL STYLES
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif; color: #1a1f36;
        letter-spacing: -0.01em;
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
        background-color: #6d28d9 !important;
        border-color: #6d28d9 !important;
        transform: translateY(-1px);
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%);
        padding: 1.25rem 1.5rem; border-radius: 14px;
        border: 1px solid #ddd6fe;
        box-shadow: 0 4px 14px rgba(124,58,237,0.08);
    }
    .metric-label { font-size: 0.75rem; font-weight: 700; color: #7c3aed;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem; }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #1e1b4b;
        font-family: 'DM Mono', monospace; line-height: 1.1; }
    .metric-sub  { font-size: 0.8rem; font-weight: 600; margin-top: 0.3rem; }
    .delta-pos   { color: #059669; }
    .delta-neg   { color: #dc2626; }
    .status-banner {
        padding: 0.9rem 1.5rem; border-radius: 12px; font-weight: 700;
        font-size: 1rem; text-align: center; margin: 1.25rem 0;
    }
    .status-pass { background: #d1fae5; border: 2px solid #059669; color: #065f46; }
    .status-fail { background: #fee2e2; border: 2px solid #dc2626; color: #991b1b; }
    .aggregate-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 1.25rem 1.5rem; border-radius: 14px;
        border: 1px solid #4338ca;
        box-shadow: 0 4px 14px rgba(30,27,75,0.18);
    }
    .aggregate-label { font-size: 0.75rem; font-weight: 700; color: #a5b4fc;
        text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.35rem; }
    .aggregate-value { font-size: 1.7rem; font-weight: 700; color: #ffffff;
        font-family: 'DM Mono', monospace; line-height: 1.1; }
    .aggregate-sub { font-size: 0.8rem; font-weight: 600;
        margin-top: 0.3rem; color: #c7d2fe; }
    .ltv-gauge-wrap { margin-top: 0.4rem; height: 7px; background: #e2e8f0;
        border-radius: 99px; overflow: hidden; }
    .gauge-ok   { height: 100%; border-radius: 99px; background: #059669; }
    .gauge-warn { height: 100%; border-radius: 99px; background: #f59e0b; }
    .gauge-fail { height: 100%; border-radius: 99px; background: #dc2626; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# ⚙️ DEFAULT LTV POLICY
# ==========================================
DEFAULT_LTV_POLICY = [
    {"Loan Type": "Home Loan",                "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Mortgage Loan",            "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Auto Loan",                "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "First Time Home Buyer",    "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Personal Term Loan (PTL)", "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Education Loan",           "Max LTV%": 50.0,  "Unsecured": False},
    {"Loan Type": "Professional T/L",         "Max LTV%": None,  "Unsecured": False},
    {"Loan Type": "Cash Credit",              "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Permanent WC Loan",        "Max LTV%": 70.0,  "Unsecured": False},
    {"Loan Type": "Personal OD",              "Max LTV%": 50.0,  "Unsecured": True},
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
        s['id'] for s in fmv_sources
        if s['id'] not in assigned_collateral_ids
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
            sharing_loans = [
                l for l in loans if l['_loan_id'] in user_loan_ids
            ]
            total_principal = sum(l['Principal'] for l in sharing_loans)
            for sl in sharing_loans:
                share = (
                    cid_fmv * (sl['Principal'] / total_principal)
                    if total_principal > 0
                    else cid_fmv / len(sharing_loans)
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
        s['Amount'] for s in fmv_sources
        if s['id'] in pool_collateral_ids
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
    pool_participating_sorted = sorted(
        pool_participating, key=waterfall_sort_key
    )
    remaining_pool = pool_fmv
    pool_alloc = {}
    last_idx = len(pool_participating_sorted) - 1

    for i, loan in enumerate(pool_participating_sorted):
        lid     = loan['_loan_id']
        max_ltv = policy.get(loan['Loan Type'])
        if max_ltv is None:
            pool_alloc[lid] = 0.0
            continue
        principal    = loan['Principal']
        already_have = loan_assigned_fmv.get(lid, 0.0)
        req_total    = principal / (max_ltv / 100.0)
        pool_needed  = max(0.0, req_total - already_have)
        allocated = (
            remaining_pool if i == last_idx
            else min(pool_needed, remaining_pool)
        )
        pool_alloc[lid] = allocated
        remaining_pool  = max(0.0, remaining_pool - allocated)

    total_fmv = sum(s['Amount'] for s in fmv_sources)
    results   = []

    for loan in loans:
        lid       = loan['_loan_id']
        lt        = loan['Loan Type']
        max_ltv   = policy.get(lt)
        principal = loan['Principal']
        mode      = loan.get('collateral_mode', 'pool')

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
        pool_fmv_val     = pool_alloc.get(lid, 0.0)
        total_alloc      = assigned_fmv_val + pool_fmv_val
        ltv_pct = (
            principal / total_alloc * 100.0
            if total_alloc > 0 else float('inf')
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
            'LTV%': ltv_pct, 'Pass_Status': passes,
            'Is_Unsecured': False, 'Collateral_Mode': mode,
            'Collateral_Names': assigned_coll_names,
            'Shared_Collateral_Ids': shared_cids,
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
        total_secured_principal / total_fmv * 100.0
        if total_fmv > 0 else 0.0
    )
    overall_pass = all(r['Pass_Status'] for r in results)

    return results, {
        'total_fmv': total_fmv, 'pool_fmv': pool_fmv,
        'remaining_pool': remaining_pool,
        'total_exposure': total_exposure,
        'total_secured_principal': total_secured_principal,
        'total_alloc_fmv': total_alloc_fmv,
        'wtd_ltv': wtd_ltv, 'aggregate_ltv': aggregate_ltv,
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
    total_fmv       = summary['total_fmv']
    total_exposure  = summary['total_exposure']
    wtd_ltv         = summary['wtd_ltv']
    aggregate_ltv   = summary['aggregate_ltv']
    overall_pass    = summary['overall_pass']
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
    kv("Total Loan Exposure:", f"Rs. {total_exposure:,.2f}")
    kv("Total Collateral FMV:", f"Rs. {total_fmv:,.2f}")
    kv("Aggregate LTV%:", f"{aggregate_ltv:.2f}%")
    kv("Weighted Avg LTV% (secured):", f"{wtd_ltv:.2f}%")

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

    assigned_ids     = summary['assigned_collateral_ids']
    collateral_usage = summary['collateral_usage']
    id_to_loan_type  = {
        l['_loan_id']: l['Loan Type'] for l in st.session_state.loans
    }

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(219, 234, 254)
    pdf.cell(75, 7, "Plot / Property Reference", 1, 0, 'C', fill=True)
    pdf.cell(35, 7, "FMV (Rs.)",                 1, 0, 'C', fill=True)
    pdf.cell(30, 7, "Type",                      1, 0, 'C', fill=True)
    pdf.cell(60, 7, "Assigned To",               1, 1, 'C', fill=True)
    pdf.set_font("Arial", "", 8)

    for i, src in enumerate(fmv_sources):
        fid  = src.get('id', i)
        fill = (i % 2 == 0)
        if fill:
            pdf.set_fill_color(248, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        ctype = "Assigned" if fid in assigned_ids else "Pool"
        users = collateral_usage.get(fid, [])
        assigned_to = (
            ", ".join(id_to_loan_type.get(u, str(u)) for u in users)
            if users else "Pool (shared)"
        )
        pdf.cell(75, 6, safe_str(src['Plot']),       1, 0, 'L', fill)
        pdf.cell(35, 6, f"{src['Amount']:,.0f}",     1, 0, 'R', fill)
        pdf.cell(30, 6, safe_str(ctype),             1, 0, 'C', fill)
        pdf.cell(60, 6, safe_str(assigned_to[:30]),  1, 1, 'L', fill)

    pdf.set_font("Arial", "B", 8)
    pdf.set_fill_color(237, 233, 254)
    pdf.cell(75, 6, "TOTAL",              1, 0, 'R', True)
    pdf.cell(35, 6, f"{total_fmv:,.0f}", 1, 0, 'R', True)
    pdf.cell(90, 6, "",                   1, 1, '',  True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(30, 27, 75)
    pdf.cell(0, 8, "FACILITY LTV BREAKDOWN", 0, 1)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)

    col_w = [44, 22, 22, 22, 18, 18, 18, 26]
    hdrs  = [
        "Facility Type", "Principal", "Asgn.FMV", "Pool FMV",
        "Tot.FMV", "LTV%", "MaxLTV", "Status"
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
        if fill:
            pdf.set_fill_color(248, 245, 255)
        else:
            pdf.set_fill_color(255, 255, 255)
        is_unsec   = row.get('Is_Unsecured', False)
        max_ltv    = row.get('Max LTV%')
        ltv_val    = row.get('LTV%')
        ltv_disp   = "N/A" if (is_unsec or ltv_val  is None) else f"{ltv_val:.1f}%"
        max_disp   = "N/A" if (is_unsec or max_ltv  is None) else f"{max_ltv:.0f}%"
        asgn_disp  = "N/A" if is_unsec else f"{row['Assigned FMV']:,.0f}"
        pool_disp  = "N/A" if is_unsec else f"{row['Pool FMV']:,.0f}"
        total_disp = "N/A" if is_unsec else f"{row['Total FMV']:,.0f}"
        status     = "PASS" if row['Pass_Status'] else "FAIL"
        pdf.set_font("Arial", "", 7)
        pdf.cell(col_w[0], 6, safe_str(row['Loan Type']), 1, 0, 'L', fill)
        pdf.cell(col_w[1], 6, f"{row['Principal']:,.0f}", 1, 0, 'R', fill)
        pdf.cell(col_w[2], 6, safe_str(asgn_disp),        1, 0, 'R', fill)
        pdf.cell(col_w[3], 6, safe_str(pool_disp),        1, 0, 'R', fill)
        pdf.cell(col_w[4], 6, safe_str(total_disp),       1, 0, 'R', fill)
        pdf.cell(col_w[5], 6, safe_str(ltv_disp),         1, 0, 'C', fill)
        pdf.cell(col_w[6], 6, safe_str(max_disp),         1, 0, 'C', fill)
        if status == "PASS":
            pdf.set_text_color(5, 150, 105)
        else:
            pdf.set_text_color(220, 38, 38)
        pdf.cell(col_w[7], 6, status, 1, 1, 'C', fill)
        pdf.set_text_color(0, 0, 0)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(30, 27, 75)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        0, 8,
        safe_str(
            f"AGGREGATE LTV: Secured Rs. {total_secured_p:,.0f} / "
            f"Total FMV Rs. {total_fmv:,.0f} = {aggregate_ltv:.2f}%"
        ),
        1, 1, 'C', fill=True
    )
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
        f"padding:0.45rem 0.85rem; font-size:0.8rem; color:#c7d2fe; "
        f"margin-bottom:0.3rem;'>"
        f"👤 Signed in as <b>{st.session_state['auth_username']}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("🚪 Sign Out", type="primary"):
        st.session_state["authenticated"] = False
        st.session_state["auth_username"] = ""
        st.session_state["_login_error"]  = ""
        st.rerun()

    st.markdown(
        "<div style='background:rgba(255,255,255,0.08); border-radius:8px; "
        "padding:0.5rem 0.85rem; font-size:0.78rem; color:#c7d2fe; "
        "margin-bottom:0.25rem;'>"
        "📌 <b>Step 1</b>: Add properties → <b>Step 2</b>: Add loans</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    st.markdown("### 📍 Step 1 — Add Properties")
    sb_plot = st.text_input(
        "Plot / Property Reference",
        placeholder="e.g. Plot No. 42-B, Sector 7", key="sb_plot"
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
                "id": fid, "Plot": sb_plot.strip(), "Amount": sb_fmv,
            })
            st.success(f"✅ Added: {sb_plot.strip()}")
            st.rerun()

    if st.session_state.fmv_sources:
        assigned_in_use = _get_assigned_in_use()
        pool_fmv_avail  = sum(
            s['Amount'] for s in st.session_state.fmv_sources
            if s.get('id') not in assigned_in_use
        )
        total_fmv_all = sum(s['Amount'] for s in st.session_state.fmv_sources)
        st.markdown(
            f"<div style='background:rgba(255,255,255,0.1); border-radius:8px; "
            f"padding:0.6rem 0.9rem; margin:0.5rem 0; font-size:0.85rem;'>"
            f"💰 Total FMV: <b>Rs. {total_fmv_all:,.0f}</b><br>"
            f"🌊 Pool available: <b>Rs. {pool_fmv_avail:,.0f}</b><br>"
            f"📦 Properties: <b>{len(st.session_state.fmv_sources)}</b></div>",
            unsafe_allow_html=True
        )
        for src in st.session_state.fmv_sources:
            src_id  = src.get('id', '?')
            is_used = src_id in assigned_in_use
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.markdown(
                    f"<div style='font-size:0.78rem; color:#c7d2fe; "
                    f"padding:0.2rem 0;'>"
                    f"{'🔒' if is_used else '🌊'} "
                    f"<b>[{src_id}]</b> {src.get('Plot','')}<br>"
                    f"&nbsp;&nbsp;Rs. {src.get('Amount',0):,.0f}</div>",
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
    st.markdown("### 📋 Step 2 — Add Loan Facility")
    policy_dict    = get_policy_dict()
    loan_type_list = list(policy_dict.keys())

    if loan_type_list:
        l_type = st.selectbox(
            "Facility Type", loan_type_list, key="sb_loan_type"
        )
        l_amt = st.number_input(
            "Principal Amount (Rs.)",
            step=10000.0, min_value=0.0, key="sb_loan_principal"
        )
        max_ltv_sel    = policy_dict.get(l_type)
        selected_colls = []
        coll_mode      = "pool"

        if max_ltv_sel is not None:
            st.markdown(
                "<div style='background:rgba(255,255,255,0.06); "
                "border-radius:6px; padding:0.4rem 0.7rem; "
                "font-size:0.74rem; color:#a5b4fc; margin:0.35rem 0;'>"
                "🌊 Pool = shared waterfall | 🔒 Assigned = dedicated "
                "property</div>",
                unsafe_allow_html=True
            )
            use_dedicated = st.checkbox(
                "🔒 Assign dedicated collateral(s) to this loan?",
                value=False, key="sb_use_dedicated",
                help=(
                    "✅ Checked → Link specific properties.\n\n"
                    "☐ Unchecked → Shared pool (default)."
                )
            )
            coll_mode = "assigned" if use_dedicated else "pool"

            if use_dedicated:
                if st.session_state.fmv_sources:
                    already_assigned = _get_assigned_in_use()
                    coll_options = {}
                    for s in st.session_state.fmv_sources:
                        sid  = s.get('id')
                        base = (
                            f"[{sid}] {s.get('Plot','?')} "
                            f"— Rs.{s.get('Amount',0):,.0f}"
                        )
                        label = (
                            f"⚠️ {base} [in use]"
                            if sid in already_assigned
                            else f"✅ {base}"
                        )
                        coll_options[label] = sid
                    sel_labels = st.multiselect(
                        "Select Collateral(s)",
                        options=list(coll_options.keys()),
                        key="sb_sel_colls"
                    )
                    selected_colls = [
                        coll_options[lbl] for lbl in sel_labels
                    ]
                    overlap = [
                        c for c in selected_colls if c in already_assigned
                    ]
                    if overlap:
                        st.warning(
                            "⚠️ FMV split proportionally by principal."
                        )
                    if selected_colls and l_amt > 0:
                        sel_fmv = sum(
                            s.get('Amount', 0)
                            for s in st.session_state.fmv_sources
                            if s.get('id') in selected_colls
                        )
                        st.markdown(
                            f"<div style='background:rgba(255,255,255,0.1); "
                            f"border-radius:6px; padding:0.5rem 0.75rem; "
                            f"font-size:0.8rem;'>"
                            f"🏠 Selected FMV: <b>Rs. {sel_fmv:,.0f}</b>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                else:
                    st.warning("⚠️ Add properties first (Step 1)")

        if max_ltv_sel is None:
            st.markdown(
                "<div style='background:rgba(245,158,11,0.15); "
                "border-left:3px solid #f59e0b; padding:0.5rem 0.75rem; "
                "border-radius:6px; font-size:0.8rem; color:#fde68a; "
                "margin-top:0.5rem;'>⚡ Unsecured — no FMV required</div>",
                unsafe_allow_html=True
            )
        else:
            priority_lbl = (
                "HIGH (50%)" if max_ltv_sel <= 50 else "NORMAL (70%)"
            )
            mode_lbl = (
                "🔒 Dedicated" if coll_mode == "assigned"
                else "🌊 Shared Pool"
            )
            st.markdown(
                f"<div style='background:rgba(255,255,255,0.1); "
                f"border-radius:6px; padding:0.5rem 0.75rem; "
                f"font-size:0.8rem; margin-top:0.5rem;'>"
                f"🔒 Max LTV: <b>{max_ltv_sel:.0f}%</b> | {priority_lbl}<br>"
                f"📌 Mode: <b>{mode_lbl}</b></div>",
                unsafe_allow_html=True
            )

        if st.button("Add to Portfolio", type="primary"):
            if l_amt <= 0:
                st.error("Principal must be > 0")
            elif coll_mode == "assigned" and not selected_colls:
                st.error("Select at least one property")
            else:
                lid = st.session_state.loan_id_counter
                st.session_state.loan_id_counter += 1
                st.session_state.loans.append({
                    "Loan Type":               l_type,
                    "Principal":               l_amt,
                    "_loan_id":                lid,
                    "collateral_mode":         coll_mode,
                    "assigned_collateral_ids": selected_colls,
                })
                ml = (
                    "🔒 Dedicated" if coll_mode == "assigned"
                    else "🌊 Pool"
                )
                st.success(f"✅ Added {l_type} ({ml})")
                st.rerun()

    if st.session_state.loans:
        st.markdown("---")
        st.markdown("**Current Portfolio**")
        for loan in st.session_state.loans:
            mi = {"pool": "🌊", "assigned": "🔒"}.get(
                loan.get('collateral_mode', 'pool'), "🌊"
            )
            st.markdown(
                f"<div style='font-size:0.76rem; color:#c7d2fe; "
                f"padding:0.15rem 0;'>"
                f"{mi} {loan['Loan Type']}<br>"
                f"&nbsp;&nbsp;Rs. {loan['Principal']:,.0f}</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")
    if st.button("🔄 Reset Everything", type="primary"):
        st.session_state.loans           = []
        st.session_state.fmv_sources     = []
        st.session_state.ltv_policy      = copy.deepcopy(DEFAULT_LTV_POLICY)
        st.session_state.loan_id_counter = 0
        st.session_state.fmv_id_counter  = 0
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

if not st.session_state.loans:
    st.markdown("""
    <div style='text-align:center; padding:3.5rem 2rem;
         background:linear-gradient(135deg,#ffffff 0%,#f5f3ff 100%);
         border-radius:16px; box-shadow:0 4px 16px rgba(124,58,237,0.08);'>
        <div style='font-size:2.5rem; margin-bottom:0.75rem;'>🏦</div>
        <h3 style='color:#6d28d9; margin-bottom:0.75rem;'>
            LTV Analysis Engine</h3>
        <p style='color:#64748b; font-size:1rem;'>
            Use the sidebar to:<br>
            1️⃣ &nbsp;<b>Step 1</b>: Add collateral / FMV sources<br>
            2️⃣ &nbsp;<b>Step 2</b>: Add loan facilities<br>
            3️⃣ &nbsp;View multi-collateral LTV analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if not st.session_state.fmv_sources:
    st.warning(
        "⚠️ Add at least one property/FMV source in the sidebar (Step 1)."
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

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total Exposure</div>
        <div class='metric-value'>Rs.{total_exposure:,.0f}</div>
        <div class='metric-sub' style='color:#64748b;'>
            {len(st.session_state.loans)} facilities</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Total FMV Pool</div>
        <div class='metric-value'>Rs.{total_fmv:,.0f}</div>
        <div class='metric-sub delta-pos'>
            {len(st.session_state.fmv_sources)} properties</div>
    </div>""", unsafe_allow_html=True)
with k3:
    gc = (
        "gauge-ok" if wtd_ltv <= 50
        else ("gauge-warn" if wtd_ltv <= 65 else "gauge-fail")
    )
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-label'>Weighted Avg LTV%</div>
        <div class='metric-value'>{wtd_ltv:.2f}%</div>
        <div class='ltv-gauge-wrap'>
            <div class='{gc}' style='width:{min(wtd_ltv,100):.1f}%'></div>
        </div>
    </div>""", unsafe_allow_html=True)
with k4:
    agc = (
        "gauge-ok" if aggregate_ltv <= 50
        else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    )
    st.markdown(f"""<div class='aggregate-card'>
        <div class='aggregate-label'>Aggregate LTV%</div>
        <div class='aggregate-value'>{aggregate_ltv:.2f}%</div>
        <div class='aggregate-sub'>
            Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
        <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
            <div class='{agc}' style='width:{min(aggregate_ltv,100):.1f}%'>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

if overall_pass:
    st.markdown(
        "<div class='status-banner status-pass'>"
        "✅ PORTFOLIO APPROVED — All Within LTV Limits</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div class='status-banner status-fail'>"
        "⚠️ PORTFOLIO DECLINED — Exceeds LTV Limits</div>",
        unsafe_allow_html=True
    )

st.markdown("### 🗂️ Collateral Assignment Matrix")
collateral_usage  = summary['collateral_usage']
assigned_coll_ids = summary['assigned_collateral_ids']
pool_coll_ids     = summary['pool_collateral_ids']
loan_ids_ordered  = [l['_loan_id'] for l in st.session_state.loans]

matrix_data = []
for src in st.session_state.fmv_sources:
    src_id = src.get('id', '?')
    row = {
        "Property": (
            f"{src.get('Plot','?')} (Rs.{src.get('Amount',0):,.0f})"
        ),
        "Type": "Assigned" if src_id in assigned_coll_ids else "Pool",
    }
    users = collateral_usage.get(src_id, [])
    for lid in loan_ids_ordered:
        loan = next(
            (l for l in st.session_state.loans if l['_loan_id'] == lid),
            None
        )
        if loan is None:
            row[f"L{lid}"] = "—"
            continue
        mode = loan.get('collateral_mode', 'pool')
        a_ids = loan.get('assigned_collateral_ids', [])
        if src_id in a_ids:
            row[f"L{lid}"] = (
                "⚡ Shared" if (lid in users and len(users) > 1)
                else "✅ Assigned"
            )
        elif src_id in pool_coll_ids and mode == 'pool':
            row[f"L{lid}"] = "🌊 Pool"
        else:
            row[f"L{lid}"] = "—"
    matrix_data.append(row)

if matrix_data:
    matrix_df = pd.DataFrame(matrix_data)
    rename_map = {}
    for lid in loan_ids_ordered:
        loan = next(
            (l for l in st.session_state.loans if l['_loan_id'] == lid),
            None
        )
        if loan:
            rename_map[f"L{lid}"] = (
                f"{loan['Loan Type'][:14]} "
                f"(Rs.{loan['Principal']/1e5:.1f}L)"
            )
    st.dataframe(
        matrix_df.rename(columns=rename_map),
        hide_index=True, use_container_width=True
    )
    st.markdown(
        "<div style='font-size:0.82rem; color:#64748b; margin-top:0.25rem;'>"
        "✅ Assigned = dedicated | "
        "⚡ Shared = split proportionally | "
        "🌊 Pool = waterfall</div>",
        unsafe_allow_html=True
    )

st.markdown("### 📋 Portfolio LTV Breakdown")


def display_sort_key(r):
    m = r.get('Max LTV%')
    if m is None:
        return (2, 0)
    return (0 if m <= 50 else 1, -(r.get('Principal', 0)))


sorted_display = sorted(results, key=display_sort_key)
disp_rows      = []

for r in sorted_display:
    is_unsec   = r['Is_Unsecured']
    ltv_val    = r.get('LTV%')
    max_ltv    = r.get('Max LTV%')
    mode       = r.get('Collateral_Mode', 'pool')
    coll_names = r.get('Collateral_Names', [])
    mode_disp  = {
        "pool": "🌊 Pool", "assigned": "🔒 Assigned"
    }.get(mode, "🌊 Pool")
    priority = (
        "Unsecured" if is_unsec
        else ("HIGH (50%)" if (max_ltv or 99) <= 50 else "NORMAL (70%)")
    )
    coll_disp = (
        ", ".join(coll_names) if coll_names
        else ("Pool" if not is_unsec else "—")
    )
    disp_rows.append({
        "Facility":      r['Loan Type'],
        "Priority":      priority,
        "Mode":          mode_disp,
        "Collateral(s)": coll_disp,
        "Principal":     f"Rs. {r['Principal']:,.0f}",
        "Assigned FMV":  (
            "N/A" if is_unsec else f"Rs. {r['Assigned FMV']:,.0f}"
        ),
        "Pool FMV":      (
            "N/A" if is_unsec else f"Rs. {r['Pool FMV']:,.0f}"
        ),
        "Total FMV":     (
            "N/A" if is_unsec else f"Rs. {r['Total FMV']:,.0f}"
        ),
        "LTV%":          (
            "N/A" if (is_unsec or ltv_val is None)
            else f"{ltv_val:.2f}%"
        ),
        "Max LTV":       (
            "N/A" if (is_unsec or max_ltv is None)
            else f"{max_ltv:.0f}%"
        ),
        "Status": "✅ PASS" if r['Pass_Status'] else "❌ FAIL",
    })

disp_rows.append({
    "Facility":      "── AGGREGATE ──",
    "Priority":      "—", "Mode": "—", "Collateral(s)": "All",
    "Principal":     f"Rs. {total_secured_principal:,.0f}",
    "Assigned FMV":  "—", "Pool FMV": "—",
    "Total FMV":     f"Rs. {total_fmv:,.0f}",
    "LTV%":          f"{aggregate_ltv:.2f}%",
    "Max LTV":       "—",
    "Status":        "✅ PASS" if aggregate_ltv <= 70 else "❌ FAIL",
})
st.dataframe(pd.DataFrame(disp_rows), hide_index=True, use_container_width=True)

st.markdown("### 📊 LTV Visual Summary")
secured_disp = [r for r in sorted_display if not r['Is_Unsecured']]

if secured_disp:
    num_cols = min(len(secured_disp) + 1, 4)
    bar_cols = st.columns(num_cols)

    for i, row in enumerate(secured_disp):
        col_idx = i % num_cols
        ltv     = row['LTV%'] if row['LTV%'] is not None else 0
        max_ltv = row['Max LTV%'] or 100
        pct     = min((ltv / max_ltv) * 100, 100)
        fill_cls = (
            "gauge-ok" if ltv <= max_ltv * 0.8
            else ("gauge-warn" if ltv <= max_ltv else "gauge-fail")
        )
        s_color = "#059669" if row['Pass_Status'] else "#dc2626"
        p_label = "HIGH PRIORITY" if max_ltv <= 50 else "NORMAL"
        p_color = "#7c3aed" if max_ltv <= 50 else "#0891b2"
        mode    = row.get('Collateral_Mode', 'pool')
        mode_bd = {
            "pool": "🌊 Pool", "assigned": "🔒 Assigned"
        }.get(mode, "🌊 Pool")
        cn = row.get('Collateral_Names', [])
        ct = (
            ", ".join(cn[:2]) + ("..." if len(cn) > 2 else "")
            if cn else "Pool"
        )
        with bar_cols[col_idx]:
            st.markdown(f"""
            <div style='background:white; border:1px solid #ddd6fe;
                        border-radius:12px; padding:1rem;
                        margin-bottom:0.75rem;'>
                <div style='display:flex;justify-content:space-between;
                            margin-bottom:0.2rem;'>
                    <div style='font-size:0.68rem;font-weight:700;
                                color:{p_color};text-transform:uppercase;'>
                        {p_label}</div>
                    <div style='font-size:0.68rem;font-weight:600;
                                color:#64748b;'>{mode_bd}</div>
                </div>
                <div style='font-size:0.82rem;font-weight:700;
                            color:#1e1b4b;margin-bottom:0.1rem;'>
                    {row['Loan Type']}</div>
                <div style='font-size:0.68rem;color:#94a3b8;
                            margin-bottom:0.25rem;'>🏠 {ct}</div>
                <div style='font-size:1.5rem;font-weight:700;
                            color:{s_color};
                            font-family:DM Mono,monospace;'>{ltv:.2f}%</div>
                <div style='font-size:0.72rem;color:#64748b;'>
                    Max: {max_ltv:.0f}% | FMV: Rs.{row['Total FMV']:,.0f}
                </div>
                <div style='font-size:0.68rem;color:#94a3b8;
                            margin-top:0.1rem;'>
                    Assigned: Rs.{row['Assigned FMV']:,.0f} |
                    Pool: Rs.{row['Pool FMV']:,.0f}
                </div>
                <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
                    <div class='{fill_cls}' style='width:{pct:.1f}%'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    aci = len(secured_disp) % num_cols
    afc = (
        "gauge-ok" if aggregate_ltv <= 50
        else ("gauge-warn" if aggregate_ltv <= 65 else "gauge-fail")
    )
    ac = "#059669" if aggregate_ltv <= 70 else "#dc2626"
    with bar_cols[aci]:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1e1b4b 0%,#312e81 100%);
                    border:1px solid #4338ca; border-radius:12px;
                    padding:1rem; margin-bottom:0.75rem;'>
            <div style='font-size:0.7rem;font-weight:700;color:#a5b4fc;
                        text-transform:uppercase;margin-bottom:0.2rem;'>
                AGGREGATE</div>
            <div style='font-size:0.82rem;font-weight:700;color:#e0e7ff;
                        margin-bottom:0.25rem;'>
                Total Loans / Total FMV</div>
            <div style='font-size:1.5rem;font-weight:700;color:{ac};
                        font-family:DM Mono,monospace;'>
                {aggregate_ltv:.2f}%</div>
            <div style='font-size:0.74rem;color:#c7d2fe;'>
                Rs.{total_secured_principal:,.0f} / Rs.{total_fmv:,.0f}</div>
            <div class='ltv-gauge-wrap' style='margin-top:0.5rem;'>
                <div class='{afc}' style='width:{min(aggregate_ltv,100):.1f}%'>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("No secured facilities in portfolio.")

with st.expander("⚙️ Manage Portfolio — Remove Loans", expanded=False):
    if not st.session_state.loans:
        st.info("No loans added yet.")
    else:
        for loan in st.session_state.loans:
            lc1, lc2, lc3 = st.columns([3, 2, 1])
            mi = {"pool": "🌊", "assigned": "🔒"}.get(
                loan.get('collateral_mode', 'pool'), "🌊"
            )
            with lc1:
                st.markdown(
                    f"**{mi} {loan['Loan Type']}**  "
                    f"Rs. {loan['Principal']:,.0f}"
                )
            with lc2:
                cn = _get_collateral_names(
                    loan.get('assigned_collateral_ids', []),
                    st.session_state.fmv_sources,
                )
                st.markdown(
                    f"<span style='font-size:0.8rem;color:#64748b;'>"
                    f"{'  |  '.join(cn) if cn else 'Pool'}</span>",
                    unsafe_allow_html=True
                )
            with lc3:
                if st.button("Remove",
                             key=f"rm_{loan['_loan_id']}"):
                    st.session_state.loans = [
                        l for l in st.session_state.loans
                        if l['_loan_id'] != loan['_loan_id']
                    ]
                    st.rerun()

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
                            st.session_state.fmv_sources, summary,
                        )
                        sn = (
                            report_name.strip()
                            .replace(' ', '_')
                            .replace('/', '-')
                            .replace('\\', '-')
                        )
                        st.session_state['generated_pdf'] = pdf_bytes
                        st.session_state['generated_pdf_name'] = (
                            f"LTV_{sn}_{datetime.now().strftime('%Y%m%d')}"
                            f".pdf"
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
