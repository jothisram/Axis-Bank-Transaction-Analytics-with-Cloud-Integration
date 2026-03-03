# Axis Bank Official Color Palette
# Primary:   #97144D (Axis Maroon/Magenta)
# Secondary: #ED1164 (Axis Pink)
# Dark:      #282828 (Charcoal)
# Light:     #F8F9FA
# Gold:      #BE8A2D

AXIS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', Arial, sans-serif !important; box-sizing: border-box; }

/* ── HIDE STREAMLIT DEFAULTS ──────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 1200px; }
[data-testid="stDecoration"] { display: none; }

/* Fix Icon rendering */
.st-icon, .stIcon, [data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', sans-serif !important;
}

/* ── AXIS BANK NAVBAR ─────────────────────────────────────────── */
.axis-navbar {
    background: linear-gradient(135deg, #97144D 0%, #AE275F 50%, #ED1164 100%);
    padding: 16px 32px;
    border-radius: 0 0 20px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    box-shadow: 0 6px 30px rgba(151,20,77,0.45);
    position: relative;
    overflow: hidden;
}
.axis-navbar::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -5%;
    width: 200px;
    height: 200px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
    pointer-events: none;
}
.axis-navbar::after {
    content: '';
    position: absolute;
    bottom: -60%;
    right: 8%;
    width: 150px;
    height: 150px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
    pointer-events: none;
}
.axis-logo {
    color: white;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 2px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.axis-logo span { color: #FFD700; }
.axis-logo-sub {
    font-size: 10px;
    letter-spacing: 3px;
    font-weight: 400;
    color: rgba(255,255,255,0.75);
    display: block;
    margin-top: -4px;
}
.axis-nav-center {
    color: white;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.axis-nav-right {
    color: rgba(255,255,255,0.92);
    font-size: 13px;
    text-align: right;
}
.axis-nav-badge {
    background: rgba(255,255,255,0.18);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 3px;
    border: 1px solid rgba(255,255,255,0.25);
}

/* ── GLASSMORPHISM METRIC CARDS ───────────────────────────────── */
.metric-card {
    background: white;
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04);
    border-left: 4px solid #97144D;
    transition: transform 0.25s cubic-bezier(.4,0,.2,1), box-shadow 0.25s;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 60px; height: 60px;
    background: linear-gradient(135deg, transparent, rgba(151,20,77,0.04));
    border-radius: 0 18px 0 60px;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(151,20,77,0.18);
}
.metric-card-pink  { border-left-color: #ED1164; }
.metric-card-gold  { border-left-color: #BE8A2D; }
.metric-card-green { border-left-color: #10B981; }
.metric-card-blue  { border-left-color: #3B82F6; }
.metric-label {
    color: #6B7280;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.metric-value {
    color: #282828;
    font-size: 26px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -0.5px;
}
.metric-sub {
    color: #97144D;
    font-size: 12px;
    margin-top: 6px;
    font-weight: 500;
}
.metric-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

/* ── SECTION HEADERS ──────────────────────────────────────────── */
.section-header {
    background: linear-gradient(90deg, #97144D, #ED1164);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 18px;
    font-weight: 700;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(151,20,77,0.12);
    display: flex;
    align-items: center;
    gap: 8px;
    line-height: 1.3;
}

/* ── PREMIUM LOGIN CARD ───────────────────────────────────────── */
/* Hide the empty login-container div that Streamlit creates when
   the opening tag is in its own st.markdown() call */
.login-container:not(:has(*)) { display: none !important; }

.login-container {
    max-width: 480px;
    margin: 16px auto 0;
    background: white;
    border-radius: 24px 24px 0 0;
    padding: 36px 40px 28px;
    box-shadow: 0 -2px 20px rgba(151,20,77,0.08);
    border-top: 6px solid #97144D;
    position: relative;
    overflow: hidden;
    text-align: center;
}
.login-container::before {
    content: '';
    position: absolute;
    bottom: -40px;
    right: -40px;
    width: 120px;
    height: 120px;
    background: radial-gradient(circle, rgba(151,20,77,0.06), transparent);
    border-radius: 50%;
    pointer-events: none;
}
.login-logo {
    margin-bottom: 16px;
}
.login-logo-text {
    font-size: 24px;
    font-weight: 800;
    color: #97144D;
    letter-spacing: 3px;
}
.login-logo-text span { color: #ED1164; }
.login-title {
    color: #282828;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
    margin-top: 0;
}
.login-subtitle {
    color: #6B7280;
    font-size: 13px;
    margin-bottom: 4px;
    line-height: 1.6;
    max-width: 340px;
    margin-left: auto;
    margin-right: auto;
}
.login-divider {
    text-align: center;
    color: #9CA3AF;
    font-size: 12px;
    margin: 16px 0;
    position: relative;
}
.login-divider::before, .login-divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 38%;
    height: 1px;
    background: #E5E7EB;
}
.login-divider::before { left: 0; }
.login-divider::after  { right: 0; }
/* Form area below login header - seamless card continuation */
.login-form-body {
    background: white;
    border-radius: 0 0 24px 24px;
    padding: 4px 40px 36px;
    box-shadow: 0 16px 50px rgba(151,20,77,0.12), 0 2px 8px rgba(0,0,0,0.06);
    max-width: 480px;
    margin: 0 auto 24px;
}

/* ── INPUT FIELDS ─────────────────────────────────────────────── */
.stTextInput > div > div > input, .stTextInput > div > div > input[type="password"] {
    border: 1.8px solid #E5E7EB !important;
    border-radius: 12px !important;
    padding: 11px 16px !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    background: #FAFAFA !important;
}
.stTextInput > div > div > input:focus {
    border-color: #97144D !important;
    box-shadow: 0 0 0 3px rgba(151,20,77,0.1) !important;
    background: white !important;
}
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1.8px solid #E5E7EB !important;
}
.stDateInput > div > div > input {
    border-radius: 12px !important;
    border: 1.8px solid #E5E7EB !important;
}

/* ── BUTTONS ──────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #97144D, #ED1164) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 28px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.2s, box-shadow 0.2s !important;
    box-shadow: 0 4px 16px rgba(151,20,77,0.35) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(151,20,77,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── TABLES ───────────────────────────────────────────────────── */
.dataframe {
    border-radius: 14px !important;
    overflow: hidden !important;
    font-size: 13px !important;
    border: 1px solid #F3F4F6 !important;
}
thead tr th {
    background: linear-gradient(135deg, #97144D, #AE275F) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 12px 14px !important;
}
tbody tr:nth-child(even) { background: #FDF2F6 !important; }
tbody tr:hover { background: #FCEEF4 !important; cursor: pointer; }

/* ── TAB STYLING ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #F9FAFB;
    border-radius: 14px;
    padding: 6px;
    border: 1px solid #F3F4F6;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 9px 20px;
    font-weight: 500;
    color: #6B7280;
    background: transparent;
    transition: all 0.2s;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #97144D, #ED1164) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(151,20,77,0.3) !important;
}

/* ── SIDEBAR ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #97144D 0%, #6E0F3B 40%, #3A0A20 100%) !important;
    border-right: 1px solid rgba(237,17,100,0.25) !important;
    box-shadow: 4px 0 24px rgba(151,20,77,0.3) !important;
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at top left, rgba(237,17,100,0.15), transparent 60%),
                radial-gradient(ellipse at bottom right, rgba(190,138,45,0.08), transparent 50%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stSidebar"] * { color: white !important; }
/* Capitalize sidebar nav links so 'app' becomes 'App' */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] li span {
    text-transform: capitalize !important;
}
[data-testid="stSidebar"] .stRadio > div > label {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin: 3px 0 !important;
    transition: all 0.25s ease !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(4px) !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255,255,255,0.16) !important;
    border-color: rgba(237,17,100,0.4) !important;
    transform: translateX(4px) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioLabel"]:has(input:checked) ~ label,
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + div {
    background: rgba(237,17,100,0.3) !important;
    border-color: rgba(237,17,100,0.5) !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }
/* Sidebar nav link styling */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 8px !important;
    padding: 6px 12px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.1) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
    background: rgba(237,17,100,0.25) !important;
    border-left: 3px solid #FFD700 !important;
}

/* ── STATUS BADGES ────────────────────────────────────────────── */
.badge-approved { background: #D1FAE5; color: #065F46; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.badge-pending  { background: #FEF3C7; color: #92400E; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.badge-blocked  { background: #FEE2E2; color: #991B1B; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.badge-cr { background: #D1FAE5; color: #065F46; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-dr { background: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; }

/* ── ALERT BOXES ──────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 12px !important; }

/* ── INFO CARD (customer account info rows) ───────────────────── */
.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #F3F4F6;
    font-size: 13px;
}
.info-row:last-child { border-bottom: none; }
.info-key { color: #6B7280; font-weight: 500; }
.info-val { color: #282828; font-weight: 600; }

/* ── TRANSACTION ROW COLORS ───────────────────────────────────── */
.txn-credit { color: #059669; font-weight: 600; }
.txn-debit  { color: #DC2626; font-weight: 600; }

/* ── LANDING PAGE CARDS ───────────────────────────────────────── */
.portal-card {
    background: white;
    border-radius: 22px;
    padding: 32px 28px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.07);
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
    border: 2px solid transparent;
    height: 100%;
}
.portal-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 48px rgba(151,20,77,0.2);
    border-color: rgba(151,20,77,0.2);
}
.portal-icon { font-size: 52px; margin-bottom: 16px; }
.portal-title { font-size: 18px; font-weight: 700; color: #282828; margin-bottom: 8px; }
.portal-desc { font-size: 13px; color: #6B7280; line-height: 1.5; }

/* ── FLOATING CALCULATOR ──────────────────────────────────────── */
.calc-fab {
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 58px;
    height: 58px;
    background: linear-gradient(135deg, #97144D, #ED1164);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 6px 24px rgba(151,20,77,0.5);
    z-index: 9999;
    transition: transform 0.3s, box-shadow 0.3s;
    border: none;
    color: white;
    font-size: 24px;
}
.calc-fab:hover {
    transform: scale(1.1) rotate(10deg);
    box-shadow: 0 12px 36px rgba(151,20,77,0.6);
}
.calc-panel {
    position: fixed;
    bottom: 100px;
    right: 28px;
    width: 320px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
    z-index: 9998;
    overflow: hidden;
    border: 1px solid rgba(151,20,77,0.15);
}
.calc-header {
    background: linear-gradient(135deg, #97144D, #ED1164);
    color: white;
    padding: 14px 18px;
    font-weight: 700;
    font-size: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.calc-body { padding: 18px; }
.calc-tabs {
    display: flex;
    gap: 6px;
    margin-bottom: 18px;
    background: #F9FAFB;
    border-radius: 10px;
    padding: 4px;
}
.calc-tab {
    flex: 1;
    text-align: center;
    padding: 7px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    color: #6B7280;
    transition: all 0.2s;
}
.calc-tab.active {
    background: linear-gradient(135deg, #97144D, #ED1164);
    color: white;
}
.calc-input {
    width: 100%;
    padding: 9px 13px;
    border: 1.5px solid #E5E7EB;
    border-radius: 10px;
    font-size: 13px;
    margin-bottom: 10px;
    outline: none;
    transition: border-color 0.2s;
}
.calc-input:focus { border-color: #97144D; }
.calc-result {
    background: linear-gradient(135deg, #FDF2F6, #FFF5F9);
    border-radius: 12px;
    padding: 14px;
    margin-top: 12px;
    border: 1.5px solid rgba(151,20,77,0.1);
}
.calc-result-label { font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.8px; }
.calc-result-value { font-size: 22px; font-weight: 800; color: #97144D; margin-top: 4px; }
.calc-btn {
    width: 100%;
    padding: 10px;
    background: linear-gradient(135deg, #97144D, #ED1164);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    margin-top: 10px;
    transition: opacity 0.2s;
}
.calc-btn:hover { opacity: 0.9; }

/* ── CHART CONTAINER ──────────────────────────────────────────── */
.chart-container {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    margin-bottom: 16px;
    border: 1px solid #F3F4F6;
}

/* ── BALANCE GAUGE ────────────────────────────────────────────── */
.balance-gauge-container {
    background: linear-gradient(135deg, #97144D, #AE275F, #ED1164);
    border-radius: 20px;
    padding: 28px 24px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px rgba(151,20,77,0.4);
    position: relative;
    overflow: hidden;
}
.balance-gauge-label { font-size: 12px; letter-spacing: 1.5px; opacity: 0.85; text-transform: uppercase; }
.balance-gauge-value { font-size: 36px; font-weight: 800; margin: 8px 0; letter-spacing: -1px; }
.balance-gauge-sub   { font-size: 12px; opacity: 0.8; }

/* ── PROGRESS BAR ─────────────────────────────────────────────── */
.axis-progress-bar {
    background: #F3F4F6;
    border-radius: 100px;
    height: 8px;
    overflow: hidden;
    margin: 8px 0;
}
.axis-progress-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #97144D, #ED1164);
    transition: width 0.6s ease;
}

/* ── KPIROW ───────────────────────────────────────────────────── */
.kpi-mini {
    background: #F9FAFB;
    border-radius: 12px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid #F3F4F6;
    margin-bottom: 8px;
}
.kpi-mini-icon { font-size: 18px; }
.kpi-mini-label { font-size: 11px; color: #6B7280; }
.kpi-mini-val { font-size: 14px; font-weight: 700; color: #282828; }

</style>
"""

def navbar(title: str, user: str = "", role: str = "") -> str:
    role_badge = {
        "customer":   "👤 Customer",
        "management": "🏦 Branch Manager",
        "admin":      "⚙️ Admin"
    }.get(role, "")
    right_content = ""
    if role_badge and user:
        right_content = f'<span class="axis-nav-badge">{role_badge}</span><br>{user}'
    elif role_badge:
        right_content = f'<span class="axis-nav-badge">{role_badge}</span>'
    elif user:
        right_content = user
    return (
        '<div class="axis-navbar">'
        '<div class="axis-logo">AXIS <span>BANK</span>'
        '<span class="axis-logo-sub">ANALYTICS PORTAL</span></div>'
        f'<div class="axis-nav-center">{title}</div>'
        f'<div class="axis-nav-right">{right_content}</div>'
        '</div>'
    )

def metric_card(label: str, value: str, sub: str = "", color: str = "") -> str:
    extra_cls = f"metric-card-{color}" if color else ""
    sub_html = f"<div class='metric-sub'>{sub}</div>" if sub else ""
    return f"""
    <div class="metric-card {extra_cls}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """

def section_header(title: str) -> str:
    return f'<div class="section-header">{title}</div>'

def format_inr(amount) -> str:
    try:
        val = float(amount)
        if val >= 1_00_00_000:
            return f"₹{val/1_00_00_000:.2f} Cr"
        elif val >= 1_00_000:
            return f"₹{val/1_00_000:.2f} L"
        return f"₹{val:,.2f}"
    except:
        return "₹0.00"

def format_inr_full(amount) -> str:
    try:
        return f"₹{float(amount):,.2f}"
    except:
        return "₹0.00"

def info_row(key: str, val: str) -> str:
    return f"""
    <div class="info-row">
        <span class="info-key">{key}</span>
        <span class="info-val">{val}</span>
    </div>"""

COLORS = ["#97144D","#ED1164","#BE8A2D","#10B981","#3B82F6","#FBBF24","#A78BFA","#F472B6","#34D399","#F87171","#60A5FA","#FC9B6A"]