import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend.utils.styles import AXIS_CSS, navbar

st.set_page_config(
    page_title="Axis Bank Analytics Portal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(AXIS_CSS, unsafe_allow_html=True)

# Redirect if already logged in
if st.session_state.get("role") == "customer":
    st.switch_page("pages/1_Customer.py")
elif st.session_state.get("role") == "management":
    st.switch_page("pages/2_Management.py")
elif st.session_state.get("role") == "admin":
    st.switch_page("pages/3_Admin.py")

st.markdown(navbar("Analytics Portal"), unsafe_allow_html=True)

# Hero section
st.markdown("""
<div style="text-align:center;padding:32px 0 20px 0;">
    <div style="font-size:13px;font-weight:600;letter-spacing:3px;color:#97144D;text-transform:uppercase;margin-bottom:12px;">
        Powered by AWS · Secured by JWT + TOTP MFA
    </div>
    <h1 style="font-size:40px;font-weight:800;color:#282828;margin:0;line-height:1.2;">
        Axis Bank <span style="background:linear-gradient(90deg,#97144D,#ED1164);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Transaction Analytics</span>
    </h1>
    <p style="color:#6B7280;font-size:16px;max-width:580px;margin:14px auto 0;">
        Enterprise-grade banking intelligence platform. Real-time insights for customers,
        branch managers, and system administrators.
    </p>
</div>
""", unsafe_allow_html=True)

# Portal cards
col1, col2, col3 = st.columns([1,1,1])

with col1:
    st.markdown("""
    <div class="portal-card" style="border-top:5px solid #97144D;">
        <div class="portal-icon">👤</div>
        <div class="portal-title">Customer Portal</div>
        <div class="portal-desc">
            View your account balance, transaction history, spending analytics,
            balance trends, and cash flow. Includes an EMI & savings calculator.
        </div>
        <div style="margin-top:20px;">
            <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;">
                <span style="background:#FDF2F6;color:#97144D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">💳 Transactions</span>
                <span style="background:#FDF2F6;color:#97144D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">📊 Spending</span>
                <span style="background:#FDF2F6;color:#97144D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">🧮 Calculator</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("👤 Customer Login", key="cust_btn", use_container_width=True):
        st.switch_page("pages/1_Customer.py")

with col2:
    st.markdown("""
    <div class="portal-card" style="border-top:5px solid #ED1164;">
        <div class="portal-icon">🏦</div>
        <div class="portal-title">Branch Management</div>
        <div class="portal-desc">
            Monitor your branch performance, view customer portfolios,
            analyze spending categories, and track monthly activity trends.
        </div>
        <div style="margin-top:20px;">
            <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;">
                <span style="background:#FFF0F6;color:#ED1164;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">📈 Analytics</span>
                <span style="background:#FFF0F6;color:#ED1164;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">👥 Customers</span>
                <span style="background:#FFF0F6;color:#ED1164;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">🗂️ Categories</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏦 Manager Login", key="mgmt_btn", use_container_width=True):
        st.switch_page("pages/2_Management.py")

with col3:
    st.markdown("""
    <div class="portal-card" style="border-top:5px solid #BE8A2D;">
        <div class="portal-icon">⚙️</div>
        <div class="portal-title">Admin Control Panel</div>
        <div class="portal-desc">
            Full system oversight with TOTP MFA. Approve managers,
            compare branches, lookup any customer, and view global analytics.
        </div>
        <div style="margin-top:20px;">
            <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;">
                <span style="background:#FFFBEB;color:#BE8A2D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">🔐 TOTP MFA</span>
                <span style="background:#FFFBEB;color:#BE8A2D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">🔄 Branch Compare</span>
                <span style="background:#FFFBEB;color:#BE8A2D;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;">🌐 Global BI</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚙️ Admin Login", key="admin_btn", use_container_width=True):
        st.switch_page("pages/3_Admin.py")

# Features strip
st.markdown("""
<div style="margin-top:48px;background:white;border-radius:20px;padding:28px 36px;
            box-shadow:0 2px 20px rgba(0,0,0,0.06);border:1px solid #F3F4F6;">
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;text-align:center;">
        <div>
            <div style="font-size:28px;margin-bottom:8px;">☁️</div>
            <div style="font-weight:700;color:#282828;font-size:14px;">AWS Powered</div>
            <div style="color:#6B7280;font-size:12px;margin-top:4px;">S3 · Lambda · RDS</div>
        </div>
        <div>
            <div style="font-size:28px;margin-bottom:8px;">🔒</div>
            <div style="font-weight:700;color:#282828;font-size:14px;">JWT + TOTP MFA</div>
            <div style="color:#6B7280;font-size:12px;margin-top:4px;">Bank-grade security</div>
        </div>
        <div>
            <div style="font-size:28px;margin-bottom:8px;">📊</div>
            <div style="font-weight:700;color:#282828;font-size:14px;">Real-time Analytics</div>
            <div style="color:#6B7280;font-size:12px;margin-top:4px;">Live dashboard data</div>
        </div>
        <div>
            <div style="font-size:28px;margin-bottom:8px;">🧠</div>
            <div style="font-weight:700;color:#282828;font-size:14px;">Business Intelligence</div>
            <div style="color:#6B7280;font-size:12px;margin-top:4px;">AI-ready architecture</div>
        </div>
    </div>
</div>
<div style="text-align:center;margin-top:28px;color:#9CA3AF;font-size:12px;">
    🔒 Secured with JWT Authentication &nbsp;|&nbsp; AWS RDS PostgreSQL &nbsp;|&nbsp;
    Axis Bank Analytics Platform v2.0 &nbsp;|&nbsp; 2026
</div>
""", unsafe_allow_html=True)