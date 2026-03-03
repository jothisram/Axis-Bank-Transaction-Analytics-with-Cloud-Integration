import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils.styles import (
    AXIS_CSS, navbar, metric_card, section_header,
    format_inr, info_row, COLORS
)
from frontend.utils.api import post, get

st.set_page_config(
    page_title="Admin | Axis Bank",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(AXIS_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  ADMIN LOGIN WITH TOTP
# ══════════════════════════════════════════════════
if not st.session_state.get("token") or st.session_state.get("role") != "admin":
    st.markdown(navbar("Admin Control Panel"), unsafe_allow_html=True)

    # TOTP Setup mode
    if st.session_state.get("admin_totp_setup_mode"):
        qr_data = st.session_state.get("admin_qr_b64","")
        st.markdown("""
        <div style="max-width:480px;margin:32px auto;background:white;border-radius:24px;
                    padding:36px;box-shadow:0 12px 60px rgba(151,20,77,0.14);border-top:6px solid #97144D;">
            <div style="text-align:center;">
                <div style="font-size:22px;font-weight:700;color:#97144D;margin-bottom:8px;">
                    🔐 Setup Two-Factor Authentication
                </div>
                <div style="font-size:13px;color:#6B7280;margin-bottom:20px;">
                    Scan this QR code with Google Authenticator or Authy
                </div>
            </div>
        """, unsafe_allow_html=True)
        if qr_data:
            st.markdown(f"""
            <div style="text-align:center;margin:16px 0;">
                <img src="data:image/png;base64,{qr_data}"
                     style="border-radius:12px;border:3px solid rgba(151,20,77,0.15);"/>
            </div>
            <div style="background:#FDF2F6;border-radius:10px;padding:10px 14px;font-size:12px;
                        color:#7C1B3A;text-align:center;margin-bottom:16px;">
                After scanning, enter the 6-digit code from your authenticator app below
            </div>
            """, unsafe_allow_html=True)

        setup_code = st.text_input("Enter 6-digit TOTP code to activate MFA", max_chars=6, key="admin_setup_code")
        setup_user = st.session_state.get("admin_setup_user","")

        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Activate MFA", key="admin_activate_btn"):
                if len(setup_code) == 6:
                    resp, code = post("/auth/admin/totp/verify", {
                        "username": setup_user,
                        "totp_code": setup_code
                    })
                    if code == 200:
                        st.success("✅ MFA activated! You can now login with TOTP.")
                        for k in ["admin_totp_setup_mode","admin_qr_b64","admin_setup_user"]:
                            st.session_state.pop(k, None)
                        st.rerun()
                    else:
                        st.error(f"❌ {resp.get('detail','Invalid code')}")
                else:
                    st.warning("Enter a 6-digit code.")
        with colB:
            if st.button("↩ Back to Login", key="admin_back_setup"):
                for k in ["admin_totp_setup_mode","admin_qr_b64","admin_setup_user"]:
                    st.session_state.pop(k, None)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # Normal login
    _, lc, _ = st.columns([1, 1.3, 1])
    with lc:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <div class="login-logo-text">AXIS <span>BANK</span></div>
            </div>
            <div class="login-title">⚙️ Admin Login</div>
            <div class="login-subtitle">Secure admin portal with Multi-Factor Authentication</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-form-body">', unsafe_allow_html=True)
        adm_user = st.text_input("Username", placeholder="Enter your username", key="adm_user")
        adm_pass = st.text_input("Password", type="password", placeholder="••••••••••", key="adm_pass")

        totp_enabled_hint = st.session_state.get("admin_needs_totp", False)
        adm_totp = ""
        if totp_enabled_hint:
            st.markdown("""
            <div style="background:#FDF2F6;border-radius:10px;padding:10px;font-size:12px;color:#97144D;
                        margin:8px 0;border-left:3px solid #97144D;">
                🔐 Enter the 6-digit code from your Authenticator app
            </div>""", unsafe_allow_html=True)
            adm_totp = st.text_input("TOTP Code (Google Authenticator)", max_chars=6, key="adm_totp")

        if st.button("🔐 Login", key="admin_login_btn"):
            if adm_user and adm_pass:
                payload = {"username": adm_user, "password": adm_pass}
                if adm_totp:
                    payload["totp_code"] = adm_totp
                with st.spinner("Authenticating..."):
                    resp, code = post("/auth/admin/login", payload)
                if code == 200:
                    st.session_state["token"] = resp["access_token"]
                    st.session_state["role"]  = "admin"
                    st.session_state["name"]  = resp["name"]
                    st.session_state.pop("admin_needs_totp", None)
                    st.success("✅ Admin access granted!")
                    st.rerun()
                elif code == 403 and resp.get("detail") == "TOTP_REQUIRED":
                    st.session_state["admin_needs_totp"] = True
                    st.info("🔐 TOTP required. Enter the code from your authenticator app.")
                    st.rerun()
                else:
                    st.error(f"❌ {resp.get('detail','Invalid credentials')}")
            else:
                st.warning("Enter credentials.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Setup MFA option
        st.write("")
        with st.expander("🔑 Setup Google Authenticator MFA (first-time setup)"):
            s_user = st.text_input("Username", placeholder="Enter your username", key="setup_user")
            s_pass = st.text_input("Password", type="password", key="setup_pass")
            if st.button("Generate QR Code", key="gen_qr_btn", use_container_width=True):
                if s_user and s_pass:
                    resp, code = post("/auth/admin/totp/setup", {"username": s_user, "password": s_pass})
                    if code == 200:
                        st.session_state["admin_totp_setup_mode"] = True
                        st.session_state["admin_qr_b64"]  = resp["qr_code_base64"]
                        st.session_state["admin_setup_user"] = s_user
                        st.rerun()
                    else:
                        st.error(f"❌ {resp.get('detail','Setup failed')}")
                else:
                    st.warning("Enter credentials.")

    colH, _ = st.columns(2)
    with colH:
        if st.button("← Back to Home", key="admin_home_btn"):
            st.switch_page("app.py")
    st.stop()

# ══════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════════
user_name = st.session_state.get("name","Admin")
st.markdown(navbar("Admin Control Panel", user_name, "admin"), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### ⚙️ {user_name}")
    st.markdown("---")
    page = st.radio("Navigate to", [
        "📊 System Overview",
        "✅ Manager Approvals",
        "👥 All Managers",
        "🏦 Branch Performance",
        "🔄 Branch Comparison",
        "👤 Customer Lookup",
        "📈 Global Analytics",
        "🏆 Top Customers",
    ], key="admin_page")
    st.markdown("---")
    if st.button("🚪 Logout", key="admin_logout"):
        for k in ["token","role","name","admin_needs_totp"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── Loaders ───────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_overview():
    data, _ = get("/admin/overview")
    return data or {}

@st.cache_data(ttl=60)
def load_pending():
    data, _ = get("/admin/pending_managers")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=60)
def load_all_managers():
    data, _ = get("/admin/all_managers")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=120)
def load_branch_perf():
    data, _ = get("/admin/branch_performance")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=120)
def load_customers(limit=500, search=None, branch=None):
    params = {"limit": limit}
    if search: params["search"] = search
    if branch: params["branch"] = branch
    data, _ = get("/admin/all_customers", params)
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=120)
def load_monthly():
    data, _ = get("/admin/monthly_overview")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=120)
def load_global_cat():
    data, _ = get("/admin/global_category")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=60)
def load_top_customers_admin(limit=20):
    data, _ = get("/admin/top_customers", {"limit": limit})
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_branch_compare(b1, b2):
    data, code = get("/admin/branch_compare", {"b1": b1, "b2": b2})
    return data if code == 200 else None

def load_cust_profile(acc):
    data, code = get(f"/admin/customer/{acc}")
    return data if code == 200 else None

def load_cust_monthly(acc):
    data, _ = get(f"/admin/customer/{acc}/monthly")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_cust_categories(acc):
    data, _ = get(f"/admin/customer/{acc}/categories")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_cust_transactions(acc, limit=80):
    data, _ = get(f"/admin/customer/{acc}/transactions", {"limit": limit})
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ══════════════════════════════════════════════════
#  PAGE: SYSTEM OVERVIEW
# ══════════════════════════════════════════════════
if "Overview" in page:
    ov = load_overview()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(metric_card("Total Customers", f"{int(ov.get('total_customers',0)):,}", "Accounts"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Total Branches", f"{int(ov.get('total_branches',0)):,}", "Locations"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Total Deposits", format_inr(ov.get("total_deposits",0)), "Net balance", "green"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Total Credits", format_inr(ov.get("total_credits",0)), "All time"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("Pending Approvals", f"{int(ov.get('pending_managers',0))}", "Managers", "gold"), unsafe_allow_html=True)
    with c6: st.markdown(metric_card("Active Managers", f"{int(ov.get('approved_managers',0))}", "Approved"), unsafe_allow_html=True)

    c7,c8,c9 = st.columns(3)
    with c7: st.markdown(metric_card("Total Transactions", f"{int(float(ov.get('total_transactions',0))):,}", "All accounts"), unsafe_allow_html=True)
    with c8: st.markdown(metric_card("Avg Customer Balance", format_inr(ov.get("avg_balance",0)), "Per account"), unsafe_allow_html=True)
    with c9: st.markdown(metric_card("Total Debits", format_inr(ov.get("total_debits",0)), "All time", "pink"), unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown(section_header("📊 Global Monthly Activity"), unsafe_allow_html=True)
        df_m = load_monthly()
        if not df_m.empty:
            fig = go.Figure()
            fig.add_bar(x=df_m["month"], y=df_m["credit"], name="Credits", marker_color="#10B981")
            fig.add_bar(x=df_m["month"], y=df_m["debit"],  name="Debits",  marker_color="#97144D")
            fig.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                              legend=dict(orientation="h",y=1.12),
                              margin=dict(t=10,b=10), height=320,
                              font=dict(family="Inter,Arial",size=12))
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown(section_header("🏦 Top Branches by Deposits"), unsafe_allow_html=True)
        df_br = load_branch_perf()
        if not df_br.empty:
            top_br = df_br.nlargest(10,"deposits")
            fig2 = px.bar(top_br, x="deposits", y="branch", orientation="h",
                          color_discrete_sequence=["#97144D"],
                          labels={"deposits":"Total Deposits (₹)","branch":""})
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               yaxis={"categoryorder":"total ascending"},
                               margin=dict(t=10,b=10), height=320,
                               font=dict(family="Inter,Arial",size=10))
            st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: MANAGER APPROVALS
# ══════════════════════════════════════════════════
elif "Approvals" in page:
    st.markdown(section_header("✅ Pending Manager Approvals"), unsafe_allow_html=True)
    df_p = load_pending()
    if df_p.empty:
        st.success("✅ No pending approvals — all caught up!")
    else:
        st.info(f"⏳ {len(df_p)} manager(s) awaiting approval")
        for _, row in df_p.iterrows():
            with st.container():
                c1,c2,c3,c4,c5 = st.columns([2.5,3,2,1.5,1.5])
                with c1: st.markdown(f"**{row['name']}**")
                with c2: st.markdown(f"🏦 {row['branch']}")
                with c3: st.markdown(f"🕐 {str(row['created_at'])[:10]}")
                with c4:
                    if st.button("✅ Approve", key=f"app_{row['id']}"):
                        post(f"/admin/approve_manager/{row['id']}", {})
                        st.cache_data.clear()
                        st.success(f"✅ {row['name']} approved!")
                        st.rerun()
                with c5:
                    if st.button("🚫 Block", key=f"blk_{row['id']}"):
                        post(f"/admin/block_manager/{row['id']}", {})
                        st.cache_data.clear()
                        st.warning(f"Blocked {row['name']}")
                        st.rerun()
                st.markdown("<hr style='margin:6px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  PAGE: ALL MANAGERS
# ══════════════════════════════════════════════════
elif "Managers" in page:
    st.markdown(section_header("👥 All Registered Managers"), unsafe_allow_html=True)
    df_m = load_all_managers()
    if not df_m.empty:
        c1, c2 = st.columns(2)
        with c1:
            status_filter = st.selectbox("Filter by Status", ["All","approved","pending","blocked"], key="mgr_filter")
        with c2:
            mgr_search = st.text_input("🔍 Search by name or branch", "", key="mgr_search")
        fdf = df_m.copy()
        if status_filter != "All":
            fdf = fdf[fdf["status"] == status_filter]
        if mgr_search:
            fdf = fdf[fdf["name"].str.contains(mgr_search,case=False,na=False) |
                      fdf["branch"].str.contains(mgr_search,case=False,na=False)]

        # Summary
        c_a, c_p, c_b = st.columns(3)
        with c_a: st.markdown(metric_card("Approved", str(int((df_m["status"]=="approved").sum())), "", "green"), unsafe_allow_html=True)
        with c_p: st.markdown(metric_card("Pending", str(int((df_m["status"]=="pending").sum())), "", "gold"), unsafe_allow_html=True)
        with c_b: st.markdown(metric_card("Blocked", str(int((df_m["status"]=="blocked").sum())), "", "pink"), unsafe_allow_html=True)

        for _, row in fdf.iterrows():
            c1,c2,c3,c4,c5,c6 = st.columns([2.5,3,1.5,1.5,1.5,1.5])
            with c1: st.markdown(f"**{row['name']}**")
            with c2: st.markdown(f"🏦 {row['branch']}")
            with c3:
                badge = {"approved":"badge-approved","pending":"badge-pending","blocked":"badge-blocked"}.get(row["status"],"")
                st.markdown(f'<span class="{badge}">{row["status"].upper()}</span>', unsafe_allow_html=True)
            with c4: st.markdown(f"<small>{str(row['created_at'])[:10]}</small>", unsafe_allow_html=True)
            with c5:
                if row["status"] != "approved":
                    if st.button("✅", key=f"ma_{row['id']}", help="Approve"):
                        post(f"/admin/approve_manager/{row['id']}", {}); st.cache_data.clear(); st.rerun()
            with c6:
                if row["status"] != "blocked":
                    if st.button("🚫", key=f"mb_{row['id']}", help="Block"):
                        post(f"/admin/block_manager/{row['id']}", {}); st.cache_data.clear(); st.rerun()
            st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  PAGE: BRANCH PERFORMANCE
# ══════════════════════════════════════════════════
elif "Branch Performance" in page:
    st.markdown(section_header("🏦 Branch Performance Analytics"), unsafe_allow_html=True)
    df_br = load_branch_perf()
    if not df_br.empty:
        df_br["deposits"] = df_br["deposits"].astype(float)
        df_br["customers"] = df_br["customers"].astype(int)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(df_br.nlargest(15,"deposits"), x="deposits", y="branch",
                         orientation="h",
                         color="customers",
                         color_continuous_scale=["#FCEEF4","#97144D"],
                         labels={"deposits":"Total Deposits (₹)","branch":"","customers":"Customers"})
            fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                              yaxis={"categoryorder":"total ascending"},
                              margin=dict(t=10,b=10), height=420,
                              font=dict(family="Inter,Arial",size=10))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.scatter(df_br, x="customers", y="deposits",
                              text="branch", size="customers",
                              color="avg_balance",
                              color_continuous_scale=["#FCEEF4","#97144D"],
                              labels={"customers":"Number of Customers","deposits":"Total Deposits (₹)"})
            fig2.update_traces(textposition="top center", textfont_size=9)
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               margin=dict(t=20,b=20), height=420,
                               font=dict(family="Inter,Arial",size=10))
            st.plotly_chart(fig2, use_container_width=True)

        # Table
        st.markdown(section_header("📋 Branch Data Table"), unsafe_allow_html=True)
        tbl = df_br.copy()
        tbl["deposits"]     = tbl["deposits"].apply(lambda x: f"₹{float(x):,.0f}")
        tbl["credits"]      = tbl["credits"].apply(lambda x: f"₹{float(x):,.0f}")
        tbl["debits"]       = tbl["debits"].apply(lambda x: f"₹{float(x):,.0f}")
        tbl["avg_balance"]  = tbl["avg_balance"].apply(lambda x: f"₹{float(x):,.0f}")
        st.dataframe(tbl, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: BRANCH COMPARISON
# ══════════════════════════════════════════════════
elif "Comparison" in page:
    st.markdown(section_header("🔄 Branch vs Branch Comparison"), unsafe_allow_html=True)

    df_br = load_branch_perf()
    branch_list = sorted(df_br["branch"].tolist()) if not df_br.empty else []

    cc1, cc2 = st.columns(2)
    with cc1:
        b1 = st.selectbox("🏦 Branch A", branch_list, key="comp_b1")
    with cc2:
        options_b2 = [b for b in branch_list if b != b1]
        b2 = st.selectbox("🏦 Branch B", options_b2, key="comp_b2")

    if b1 and b2:
        if st.button("⚡ Compare Branches", key="compare_btn"):
            with st.spinner("Fetching branch analytics..."):
                comp = load_branch_compare(b1, b2)
            if comp:
                st.session_state["branch_comp_data"] = comp
                st.session_state["branch_comp_b1"]   = b1
                st.session_state["branch_comp_b2"]   = b2
            else:
                st.error("❌ Failed to load comparison data. Make sure the server is running.")

    # Render results from session_state so they survive reruns
    comp      = st.session_state.get("branch_comp_data")
    comp_b1   = st.session_state.get("branch_comp_b1", b1)
    comp_b2   = st.session_state.get("branch_comp_b2", b2)

    # Clear stale results if the user picked different branches
    if comp and (comp_b1 != b1 or comp_b2 != b2):
        comp = None
        st.session_state.pop("branch_comp_data", None)

    if comp:
            s1 = comp["branch1"]["stats"]
            s2 = comp["branch2"]["stats"]

            # Side-by-side KPI table
            st.markdown(section_header("📊 Head-to-Head Metrics"), unsafe_allow_html=True)
            metrics_names = ["customers","total_deposits","total_credits","total_debits",
                             "avg_balance","max_balance","total_transactions"]
            metric_labels = ["Customers","Total Deposits","Total Credits","Total Debits",
                             "Avg Balance","Max Balance","Transactions"]

            def safe_float(val):
                if val is None: return 0.0
                try: return float(val)
                except: return 0.0

            rows_data = []
            for mn, ml in zip(metrics_names, metric_labels):
                v1 = safe_float(s1.get(mn, 0))
                v2 = safe_float(s2.get(mn, 0))
                winner = comp_b1 if v1 > v2 else comp_b2
                rows_data.append({
                    "Metric": ml,
                    comp_b1: format_inr(v1) if "balance" in mn or "deposits" in mn or "credits" in mn or "debits" in mn else f"{int(v1):,}",
                    comp_b2: format_inr(v2) if "balance" in mn or "deposits" in mn or "credits" in mn or "debits" in mn else f"{int(v2):,}",
                    "Winner 🏆": f"🏆 {winner}"
                })
            tbl_df = pd.DataFrame(rows_data)
            st.dataframe(tbl_df, use_container_width=True, hide_index=True)

            # Radar chart
            st.markdown(section_header("🕸️ Performance Radar"), unsafe_allow_html=True)
            radar_metrics = ["customers","total_credits","total_debits","avg_balance","total_transactions"]
            radar_labels  = ["Customers","Credits","Debits","Avg Balance","Transactions"]

            def norm(v1, v2):
                v1_f = safe_float(v1)
                v2_f = safe_float(v2)
                mx = max(v1_f, v2_f)
                if mx == 0: return 0, 0
                return v1_f/mx*100, v2_f/mx*100

            vals1, vals2 = [], []
            for m in radar_metrics:
                n1, n2 = norm(s1.get(m,0), s2.get(m,0))
                vals1.append(n1); vals2.append(n2)
            vals1.append(vals1[0]); vals2.append(vals2[0])
            labels = radar_labels + [radar_labels[0]]

            fig_radar = go.Figure()
            fig_radar.add_scatterpolar(r=vals1, theta=labels, fill="toself",
                                        name=comp_b1, line_color="#97144D",
                                        fillcolor="rgba(151,20,77,0.15)")
            fig_radar.add_scatterpolar(r=vals2, theta=labels, fill="toself",
                                        name=comp_b2, line_color="#10B981",
                                        fillcolor="rgba(16,185,129,0.12)")
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,110])),
                                     paper_bgcolor="white",
                                     legend=dict(orientation="h",y=-0.1),
                                     margin=dict(t=30,b=30),
                                     height=400,
                                     font=dict(family="Inter,Arial",size=12))
            st.plotly_chart(fig_radar, use_container_width=True)

            # Monthly comparison
            col_b1, col_b2 = st.columns(2)
            m1_df = pd.DataFrame(comp["branch1"]["monthly"])
            m2_df = pd.DataFrame(comp["branch2"]["monthly"])

            with col_b1:
                st.markdown(f'<div class="section-header">📈 {comp_b1} — Monthly</div>', unsafe_allow_html=True)
                if not m1_df.empty:
                    fig_m1 = go.Figure()
                    fig_m1.add_bar(x=m1_df["month"], y=m1_df["credit"], name="Credit", marker_color="#10B981")
                    fig_m1.add_bar(x=m1_df["month"], y=m1_df["debit"],  name="Debit",  marker_color="#97144D")
                    fig_m1.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                                         margin=dict(t=10,b=10), height=260,
                                         font=dict(family="Inter,Arial",size=10))
                    st.plotly_chart(fig_m1, use_container_width=True)
            with col_b2:
                st.markdown(f'<div class="section-header">📈 {comp_b2} — Monthly</div>', unsafe_allow_html=True)
                if not m2_df.empty:
                    fig_m2 = go.Figure()
                    fig_m2.add_bar(x=m2_df["month"], y=m2_df["credit"], name="Credit", marker_color="#10B981")
                    fig_m2.add_bar(x=m2_df["month"], y=m2_df["debit"],  name="Debit",  marker_color="#ED1164")
                    fig_m2.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                                         margin=dict(t=10,b=10), height=260,
                                         font=dict(family="Inter,Arial",size=10))
                    st.plotly_chart(fig_m2, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: CUSTOMER LOOKUP
# ══════════════════════════════════════════════════
elif "Lookup" in page:
    st.markdown(section_header("👤 Customer Lookup"), unsafe_allow_html=True)

    search_acc = st.text_input("🔍 Enter Account Number to view full dashboard", placeholder="e.g. 920000000001", key="admin_acc_lookup")
    if st.button("🔍 Load Customer Dashboard", key="admin_load_cust") and search_acc:
        st.session_state["admin_viewed_acc"] = search_acc.strip()

    viewed_acc = st.session_state.get("admin_viewed_acc","")
    if viewed_acc:
        prof = load_cust_profile(viewed_acc)
        if not prof:
            st.error(f"Customer '{viewed_acc}' not found.")
        else:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#97144D,#ED1164);color:white;
                        border-radius:14px;padding:12px 20px;margin-bottom:16px;">
                <b>Viewing: {prof.get('account_holder','')} — {prof.get('account_number','')}</b>
                <span style="opacity:0.8;font-size:13px;"> | Branch: {prof.get('branch','')}</span>
            </div>
            """, unsafe_allow_html=True)

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(metric_card("Balance", format_inr(prof.get("closing_balance",0)), "Current", "green"), unsafe_allow_html=True)
            with c2: st.markdown(metric_card("Total Credits", format_inr(prof.get("total_credits",0)), "All time"), unsafe_allow_html=True)
            with c3: st.markdown(metric_card("Total Debits", format_inr(prof.get("total_debits",0)), "All time", "pink"), unsafe_allow_html=True)
            with c4: st.markdown(metric_card("Transactions", f"{int(prof.get('total_transactions',0)):,}", "Total"), unsafe_allow_html=True)

            col_i, col_c = st.columns([1, 1.5])
            with col_i:
                st.markdown(section_header("📋 Account Info"), unsafe_allow_html=True)
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                for k, v in [
                    ("Account Holder", prof.get("account_holder","")),
                    ("Account No.", prof.get("account_number","")),
                    ("Account Type", prof.get("account_type","")),
                    ("IFSC", prof.get("ifsc_code","")),
                    ("Branch", prof.get("branch","")),
                    ("Customer ID", prof.get("customer_id","")),
                    ("Currency", prof.get("currency","INR")),
                    ("Statement Period", prof.get("statement_period","")),
                ]:
                    st.markdown(info_row(k, str(v)), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col_c:
                st.markdown(section_header("📊 Monthly Activity"), unsafe_allow_html=True)
                df_cm = load_cust_monthly(viewed_acc)
                if not df_cm.empty:
                    fig = go.Figure()
                    fig.add_bar(x=df_cm["month"], y=df_cm["total_credit"], name="Credits", marker_color="#10B981")
                    fig.add_bar(x=df_cm["month"], y=df_cm["total_debit"], name="Debits", marker_color="#97144D")
                    fig.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                                      margin=dict(t=10,b=10), height=280,
                                      legend=dict(orientation="h",y=1.12),
                                      font=dict(family="Inter,Arial",size=11))
                    st.plotly_chart(fig, use_container_width=True)

            # Spending categories
            df_cc = load_cust_categories(viewed_acc)
            if not df_cc.empty:
                c5, c6 = st.columns(2)
                with c5:
                    st.markdown(section_header("🍩 Category Spending"), unsafe_allow_html=True)
                    cat_g = df_cc.groupby("category")["total_spent"].sum().reset_index()
                    fig2 = px.pie(cat_g, names="category", values="total_spent",
                                  color_discrete_sequence=COLORS, hole=0.4)
                    fig2.update_layout(paper_bgcolor="white", margin=dict(t=10,b=10), height=260)
                    st.plotly_chart(fig2, use_container_width=True)
                with c6:
                    st.markdown(section_header("📋 Category Table"), unsafe_allow_html=True)
                    tbl2 = df_cc.copy()
                    tbl2["total_spent"] = tbl2["total_spent"].apply(lambda x: f"₹{float(x):,.2f}")
                    st.dataframe(tbl2[["category","sub_category","total_spent","txn_count"]], use_container_width=True, height=260)

            st.markdown(section_header("💳 Recent Transactions"), unsafe_allow_html=True)
            df_txn = load_cust_transactions(viewed_acc)
            if not df_txn.empty:
                disp = df_txn.copy()
                disp["debit"]  = disp["debit"].apply(lambda x: f"₹{float(x):,.2f}" if float(x)>0 else "—")
                disp["credit"] = disp["credit"].apply(lambda x: f"₹{float(x):,.2f}" if float(x)>0 else "—")
                disp["balance"] = disp["balance"].apply(lambda x: f"₹{float(x):,.2f}")
                st.dataframe(disp[["date","description","transaction_type","debit","credit","balance","category","sub_category"]],
                             use_container_width=True, height=320)

# ══════════════════════════════════════════════════
#  PAGE: GLOBAL ANALYTICS
# ══════════════════════════════════════════════════
elif "Global" in page:
    st.markdown(section_header("📈 Global Transaction Analytics"), unsafe_allow_html=True)
    df_m = load_monthly()
    if not df_m.empty:
        fig = px.area(df_m, x="month", y=["credit","debit"],
                      color_discrete_map={"credit":"#10B981","debit":"#97144D"})
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          margin=dict(t=20,b=20), height=360,
                          legend=dict(orientation="h",y=1.1),
                          font=dict(family="Inter,Arial",size=12))
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(metric_card("Total Transactions", f"{int(df_m['txn_count'].sum()):,}", "All accounts"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Total Credits", format_inr(df_m["credit"].astype(float).sum()), "All time", "green"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Total Debits", format_inr(df_m["debit"].astype(float).sum()), "All time", "pink"), unsafe_allow_html=True)

    # Global category donut
    df_gc = load_global_cat()
    if not df_gc.empty:
        st.markdown(section_header("🍩 Global Spending by Category"), unsafe_allow_html=True)
        c_a, c_b = st.columns(2)
        with c_a:
            df_gc["total_debit"] = df_gc["total_debit"].astype(float)
            fig2 = px.pie(df_gc, names="category", values="total_debit",
                          color_discrete_sequence=COLORS, hole=0.4)
            fig2.update_layout(paper_bgcolor="white", margin=dict(t=10,b=10), height=340)
            st.plotly_chart(fig2, use_container_width=True)
        with c_b:
            fig3 = px.bar(df_gc.nlargest(10,"total_debit"), x="total_debit", y="category",
                          orientation="h", color_discrete_sequence=["#97144D"],
                          labels={"total_debit":"Amount (₹)","category":""})
            fig3.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               yaxis={"categoryorder":"total ascending"},
                               margin=dict(t=10,b=10), height=340,
                               font=dict(family="Inter,Arial",size=11))
            st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: TOP CUSTOMERS
# ══════════════════════════════════════════════════
elif "Top" in page:
    st.markdown(section_header("🏆 Top Customers Across All Branches"), unsafe_allow_html=True)
    df_top = load_top_customers_admin(20)
    if not df_top.empty:
        df_top["closing_balance"] = df_top["closing_balance"].astype(float)
        fig = px.bar(df_top.head(20), x="closing_balance", y="account_holder",
                     orientation="h", color="branch",
                     color_discrete_sequence=COLORS,
                     labels={"closing_balance":"Balance (₹)","account_holder":""})
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          yaxis={"categoryorder":"total ascending"},
                          margin=dict(t=10,b=10), height=480,
                          font=dict(family="Inter,Arial",size=10))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(section_header("📋 Top Customer Table"), unsafe_allow_html=True)
        tbl = df_top.copy()
        tbl["Rank"] = range(1, len(tbl)+1)
        tbl["closing_balance"] = tbl["closing_balance"].apply(lambda x: f"₹{x:,.2f}")
        tbl["total_credits"]   = tbl["total_credits"].apply(lambda x: f"₹{float(x):,.2f}")
        tbl["total_debits"]    = tbl["total_debits"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(tbl[["Rank","account_holder","account_number","branch","account_type",
                           "closing_balance","total_credits","total_debits","total_transactions"]],
                     use_container_width=True, hide_index=True)