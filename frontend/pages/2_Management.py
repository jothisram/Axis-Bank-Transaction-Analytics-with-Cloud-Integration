import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils.styles import (
    AXIS_CSS, navbar, metric_card, section_header,
    format_inr, info_row, COLORS
)
from frontend.utils.api import post, get

st.set_page_config(
    page_title="Branch Management | Axis Bank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(AXIS_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  LOGIN / REGISTER GATE
# ══════════════════════════════════════════════════
if not st.session_state.get("token") or st.session_state.get("role") != "management":
    st.markdown(navbar("Branch Management Portal"), unsafe_allow_html=True)

    # Load branches for autocomplete
    @st.cache_data(ttl=3600)
    def load_branches_public():
        data, code = get("/management/branches")
        if code == 200 and isinstance(data, list):
            return data
        return []

    branches = load_branches_public()

    tab1, tab2 = st.tabs(["🔐 Manager Login", "📝 Register"])

    # ── LOGIN TAB ─────────────────────────────────
    with tab1:
        _, lc, _ = st.columns([1, 1.4, 1])
        with lc:
            st.markdown("""
            <div class="login-container">
                <div class="login-logo">
                    <div class="login-logo-text">AXIS <span>BANK</span></div>
                </div>
                <div class="login-title">Branch Manager Login</div>
                <div class="login-subtitle">Login with your approved branch manager credentials</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="login-form-body">', unsafe_allow_html=True)
            mgr_name   = st.text_input("Manager Name", placeholder="e.g. Rajesh Kumar", key="ml_name")
            if branches:
                mgr_branch = st.selectbox("Select Your Branch", ["-- Select Branch --"] + sorted(branches), key="ml_branch_sel")
                mgr_branch = "" if mgr_branch == "-- Select Branch --" else mgr_branch
            else:
                mgr_branch = st.text_input("Branch", placeholder="e.g. Coimbatore - RS Puram", key="ml_branch_txt")
            mgr_pass   = st.text_input("Password", type="password", key="ml_pass")
            if st.button("🔐 Login to Dashboard", key="mgmt_login_btn"):
                if mgr_name and mgr_branch and mgr_pass:
                    with st.spinner("Verifying credentials..."):
                        resp, code = post("/auth/management/login", {
                            "name": mgr_name, "branch": mgr_branch, "password": mgr_pass
                        })
                    if code == 200:
                        st.session_state["token"]  = resp["access_token"]
                        st.session_state["role"]   = "management"
                        st.session_state["name"]   = resp["name"]
                        st.session_state["branch"] = resp["branch"]
                        st.success(f"✅ Welcome, {resp['name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {resp.get('detail', 'Login failed')}")
                else:
                    st.warning("⚠️ Please fill all fields.")
            st.markdown('</div>', unsafe_allow_html=True)

    # ── REGISTER TAB ──────────────────────────────
    with tab2:
        _, rc, _ = st.columns([1, 1.4, 1])
        with rc:
            st.markdown("""
            <div class="login-container">
                <div class="login-logo">
                    <div class="login-logo-text">AXIS <span>BANK</span></div>
                </div>
                <div class="login-title">Register as Manager</div>
                <div class="login-subtitle">Submit your registration. Admin will review and approve your access.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="login-form-body">', unsafe_allow_html=True)
            reg_name  = st.text_input("Full Name", placeholder="e.g. Rajesh Kumar", key="rg_name")
            if branches:
                reg_branch = st.selectbox("Select Your Branch", ["-- Select Branch --"] + sorted(branches), key="rg_branch_sel")
                reg_branch = "" if reg_branch == "-- Select Branch --" else reg_branch
            else:
                reg_branch = st.text_input("Branch Name", key="rg_branch_txt")
            reg_pass  = st.text_input("Set Password", type="password", key="rg_pass")
            reg_pass2 = st.text_input("Confirm Password", type="password", key="rg_pass2")

            st.markdown("""
            <div style="background:#FEF3C7;border-radius:10px;padding:10px 14px;
                        font-size:12px;color:#92400E;margin:12px 0;border-left:3px solid #F59E0B;">
                ⏳ After registration, your access will be activated once approved by the admin.
            </div>
            """, unsafe_allow_html=True)

            if st.button("📝 Submit Registration", key="mgmt_reg_btn"):
                if reg_name and reg_branch and reg_pass and reg_pass2:
                    if reg_pass != reg_pass2:
                        st.error("❌ Passwords do not match.")
                    else:
                        with st.spinner("Submitting registration..."):
                            resp, code = post("/auth/management/register", {
                                "name": reg_name, "branch": reg_branch, "password": reg_pass
                            })
                        if code == 200:
                            st.success("✅ Registration submitted! Awaiting admin approval.")
                        else:
                            st.error(f"❌ {resp.get('detail', 'Registration failed')}")
                else:
                    st.warning("⚠️ Please fill all fields.")
            st.markdown('</div>', unsafe_allow_html=True)

    col_b, _ = st.columns(2)
    with col_b:
        if st.button("← Back to Home", key="mgmt_back"):
            st.switch_page("app.py")
    st.stop()

# ══════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════
user_name = st.session_state.get("name", "Manager")
branch    = st.session_state.get("branch", "")
st.markdown(navbar(f"Branch Analytics — {branch}", user_name, "management"), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 🏦 {user_name}")
    st.markdown(f"**Branch:** {branch}")
    st.markdown("---")
    page = st.radio("Navigate to", [
        "📊 Branch Overview",
        "👥 Customers",
        "👤 Customer Detail View",
        "📈 Monthly Activity",
        "🗂️ Category Analysis",
        "🏆 Top Performers"
    ], key="mgmt_page")
    st.markdown("---")
    if st.button("🚪 Logout", key="mgmt_logout"):
        for k in ["token","role","name","branch","mgmt_selected_acc"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── Data Loaders ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_branch_summary():
    data, _ = get("/management/branch_summary")
    return data or {}

@st.cache_data(ttl=300)
def load_customers(limit=500):
    data, _ = get("/management/customers", {"limit": limit})
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_monthly():
    data, _ = get("/management/monthly_activity")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_category():
    data, _ = get("/management/category_breakdown")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_top_customers():
    data, _ = get("/management/top_customers")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_account_types():
    data, _ = get("/management/account_type_distribution")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_cashflow_trend():
    data, _ = get("/management/cashflow_trend")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_customer_profile(acc_no):
    data, code = get(f"/management/customer/{acc_no}")
    return data if code == 200 else None

def load_customer_monthly(acc_no):
    data, _ = get(f"/management/customer/{acc_no}/monthly")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_customer_categories(acc_no):
    data, _ = get(f"/management/customer/{acc_no}/categories")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

def load_customer_transactions(acc_no, limit=100):
    data, _ = get(f"/management/customer/{acc_no}/transactions", {"limit": limit})
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

# ══════════════════════════════════════════════════
#  PAGE: BRANCH OVERVIEW
# ══════════════════════════════════════════════════
if "Overview" in page:
    bs = load_branch_summary()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown(metric_card("Customers", f"{int(bs.get('total_customers',0)):,}", "Active accounts"), unsafe_allow_html=True)
    with c2: st.markdown(metric_card("Total Deposits", format_inr(bs.get("total_deposits",0)), "Closing balances"), unsafe_allow_html=True)
    with c3: st.markdown(metric_card("Total Credits", format_inr(bs.get("total_credits",0)), "All time", "green"), unsafe_allow_html=True)
    with c4: st.markdown(metric_card("Total Debits", format_inr(bs.get("total_debits",0)), "All time", "pink"), unsafe_allow_html=True)
    with c5: st.markdown(metric_card("Avg Balance", format_inr(bs.get("avg_balance",0)), "Per customer"), unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown(section_header("📊 Monthly Credits vs Debits"), unsafe_allow_html=True)
        df_m = load_monthly()
        if not df_m.empty:
            fig = go.Figure()
            fig.add_bar(x=df_m["month"], y=df_m["credit"], name="Credits", marker_color="#10B981")
            fig.add_bar(x=df_m["month"], y=df_m["debit"],  name="Debits",  marker_color="#97144D")
            fig.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                              legend=dict(orientation="h",y=1.12), margin=dict(t=10,b=10),
                              height=300, font=dict(family="Inter,Arial",size=12))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(section_header("🏦 Account Type Distribution"), unsafe_allow_html=True)
        df_at = load_account_types()
        if not df_at.empty:
            fig2 = px.pie(df_at, names="account_type", values="count",
                          color_discrete_sequence=COLORS, hole=0.4)
            fig2.update_layout(paper_bgcolor="white", margin=dict(t=10,b=10), height=300)
            st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(section_header("📈 Net Cash Flow Trend"), unsafe_allow_html=True)
        df_cf = load_cashflow_trend()
        if not df_cf.empty:
            df_cf["net_flow"] = df_cf["net_flow"].astype(float)
            colors = ["#10B981" if v >= 0 else "#EF4444" for v in df_cf["net_flow"]]
            fig3 = go.Figure()
            fig3.add_bar(x=df_cf["month"], y=df_cf["net_flow"],
                         marker_color=colors, name="Net Flow")
            fig3.add_hline(y=0, line_dash="dash", line_color="#9CA3AF")
            fig3.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               margin=dict(t=10,b=10), height=260,
                               font=dict(family="Inter,Arial",size=12))
            st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.markdown(section_header("🏆 Top 10 Customers"), unsafe_allow_html=True)
        df_top = load_top_customers()
        if not df_top.empty:
            df_top["closing_balance"] = df_top["closing_balance"].astype(float)
            fig4 = px.bar(df_top.head(10), x="closing_balance", y="account_holder",
                          orientation="h", color_discrete_sequence=["#97144D"])
            fig4.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               yaxis={"categoryorder":"total ascending"},
                               margin=dict(t=10,b=10), height=260,
                               xaxis_title="Balance (₹)", yaxis_title="",
                               font=dict(family="Inter,Arial",size=11))
            st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: CUSTOMERS TABLE
# ══════════════════════════════════════════════════
elif "Customers" in page and "Detail" not in page:
    st.markdown(section_header(f"👥 Customers — {branch}"), unsafe_allow_html=True)
    df_c = load_customers()
    if not df_c.empty:
        search = st.text_input("🔍 Search by name or account number", "", key="mgmt_cust_search")
        if search:
            mask = (df_c["account_holder"].str.contains(search, case=False, na=False) |
                    df_c["account_number"].astype(str).str.contains(search, na=False))
            df_c = df_c[mask]

        st.markdown(f"<div style='color:#97144D;font-weight:700;margin-bottom:12px;'>{len(df_c):,} customers found</div>", unsafe_allow_html=True)

        # Selectable row for customer detail view
        for _, row in df_c.iterrows():
            c1, c2, c3, c4, c5, c6 = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1])
            with c1: st.markdown(f"**{row['account_holder']}**<br><small style='color:#6B7280;'>{row['account_number']}</small>", unsafe_allow_html=True)
            with c2: st.markdown(f"<span style='font-size:12px;color:#6B7280;'>{row['account_type']}</span>", unsafe_allow_html=True)
            with c3: st.markdown(f"<span style='font-weight:600;color:#10B981;'>₹{float(row['closing_balance']):,.0f}</span>", unsafe_allow_html=True)
            with c4: st.markdown(f"<span style='font-size:12px;color:#6B7280;'>{int(row['total_transactions'])} txns</span>", unsafe_allow_html=True)
            with c5: st.markdown(f"<span style='font-size:12px;color:#6B7280;'>CR: {format_inr(row['total_credits'])}</span>", unsafe_allow_html=True)
            with c6:
                if st.button("👁 View", key=f"view_{row['account_number']}"):
                    st.session_state["mgmt_selected_acc"] = row["account_number"]
                    st.session_state["mgmt_selected_name"] = row["account_holder"]
                    st.rerun()
            st.markdown("<hr style='margin:4px 0;border-color:#F3F4F6;'>", unsafe_allow_html=True)
    else:
        st.info("No customers found in your branch.")

# ══════════════════════════════════════════════════
#  PAGE: CUSTOMER DETAIL VIEW
# ══════════════════════════════════════════════════
elif "Detail" in page or st.session_state.get("mgmt_selected_acc"):
    selected_acc = st.session_state.get("mgmt_selected_acc","")

    if not selected_acc:
        st.info("Please go to 'Customers' and click '👁 View' on a customer row.")
    else:
        selected_name = st.session_state.get("mgmt_selected_name", selected_acc)

        col_hd, col_btn = st.columns([4, 1])
        with col_hd:
            st.markdown(section_header(f"👤 Customer Dashboard — {selected_name}"), unsafe_allow_html=True)
        with col_btn:
            if st.button("← Back to Customers", key="back_to_cust"):
                st.session_state.pop("mgmt_selected_acc", None)
                st.session_state.pop("mgmt_selected_name", None)
                st.rerun()

        # Or let manager type account number
        if "Customer Detail" in page and not selected_acc:
            typed = st.text_input("Enter Account Number to View", key="mgmt_acc_search")
            if st.button("Load Customer", key="mgmt_load_cust") and typed:
                st.session_state["mgmt_selected_acc"]  = typed
                st.session_state["mgmt_selected_name"] = typed
                st.rerun()

        prof = load_customer_profile(selected_acc)
        if not prof:
            st.error("Customer not found or not in your branch.")
        else:
            # KPI row
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(metric_card("Balance", format_inr(prof.get("closing_balance",0)), "Current", "green"), unsafe_allow_html=True)
            with c2: st.markdown(metric_card("Total Credits", format_inr(prof.get("total_credits",0)), "All time"), unsafe_allow_html=True)
            with c3: st.markdown(metric_card("Total Debits", format_inr(prof.get("total_debits",0)), "All time", "pink"), unsafe_allow_html=True)
            with c4: st.markdown(metric_card("Transactions", f"{int(prof.get('total_transactions',0)):,}", "All time"), unsafe_allow_html=True)

            col_info, col_chart = st.columns([1, 1.5])
            with col_info:
                st.markdown(section_header("📋 Account Info"), unsafe_allow_html=True)
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                for k, v in [
                    ("Account Holder", prof.get("account_holder","")),
                    ("Account No.", prof.get("account_number","")),
                    ("Account Type", prof.get("account_type","")),
                    ("IFSC", prof.get("ifsc_code","")),
                    ("Customer ID", prof.get("customer_id","")),
                    ("Currency", prof.get("currency","INR")),
                    ("Statement Period", prof.get("statement_period","")),
                ]:
                    st.markdown(info_row(k, str(v)), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_chart:
                st.markdown(section_header("📊 Monthly Activity"), unsafe_allow_html=True)
                df_cm = load_customer_monthly(selected_acc)
                if not df_cm.empty:
                    fig = go.Figure()
                    fig.add_bar(x=df_cm["month"], y=df_cm["total_credit"], name="Credits", marker_color="#10B981")
                    fig.add_bar(x=df_cm["month"], y=df_cm["total_debit"], name="Debits", marker_color="#97144D")
                    fig.update_layout(barmode="group", paper_bgcolor="white", plot_bgcolor="white",
                                      margin=dict(t=10,b=10), height=280,
                                      legend=dict(orientation="h",y=1.12),
                                      font=dict(family="Inter,Arial",size=12))
                    st.plotly_chart(fig, use_container_width=True)

            # Category spending
            df_cc = load_customer_categories(selected_acc)
            if not df_cc.empty:
                c5, c6 = st.columns(2)
                with c5:
                    st.markdown(section_header("🍩 Spending by Category"), unsafe_allow_html=True)
                    cat_grp = df_cc.groupby("category")["total_spent"].sum().reset_index()
                    fig2 = px.pie(cat_grp, names="category", values="total_spent",
                                  color_discrete_sequence=COLORS, hole=0.4)
                    fig2.update_layout(paper_bgcolor="white", margin=dict(t=10,b=10), height=260)
                    st.plotly_chart(fig2, use_container_width=True)
                with c6:
                    st.markdown(section_header("📋 Category Table"), unsafe_allow_html=True)
                    tbl = df_cc.copy()
                    tbl["total_spent"] = tbl["total_spent"].apply(lambda x: f"₹{float(x):,.2f}")
                    st.dataframe(tbl[["category","sub_category","total_spent","txn_count"]], use_container_width=True, height=260)

            # Recent transactions
            st.markdown(section_header("💳 Recent Transactions"), unsafe_allow_html=True)
            df_txn = load_customer_transactions(selected_acc, limit=50)
            if not df_txn.empty:
                disp = df_txn.copy()
                disp["debit"]  = disp["debit"].apply(lambda x: f"₹{float(x):,.2f}" if float(x)>0 else "—")
                disp["credit"] = disp["credit"].apply(lambda x: f"₹{float(x):,.2f}" if float(x)>0 else "—")
                disp["balance"] = disp["balance"].apply(lambda x: f"₹{float(x):,.2f}")
                st.dataframe(disp[["date","description","transaction_type","debit","credit","balance","category","sub_category"]],
                             use_container_width=True, height=320)

# ══════════════════════════════════════════════════
#  PAGE: MONTHLY ACTIVITY
# ══════════════════════════════════════════════════
elif "Activity" in page:
    st.markdown(section_header("📈 Monthly Transaction Activity"), unsafe_allow_html=True)
    df_m = load_monthly()
    if not df_m.empty:
        fig = px.line(df_m, x="month", y=["credit","debit"],
                      color_discrete_map={"credit":"#10B981","debit":"#97144D"},
                      markers=True)
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          margin=dict(t=20,b=20), height=340,
                          font=dict(family="Inter,Arial",size=12))
        st.plotly_chart(fig, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(metric_card("Total Credits", format_inr(df_m["credit"].sum()), "All time", "green"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Total Debits", format_inr(df_m["debit"].sum()), "All time", "pink"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Total Transactions", f"{int(df_m['txn_count'].sum()):,}", "All months"), unsafe_allow_html=True)

        st.markdown(section_header("📊 Transaction Volume by Month"), unsafe_allow_html=True)
        fig2 = px.bar(df_m, x="month", y="txn_count",
                      color_discrete_sequence=["#ED1164"],
                      labels={"txn_count":"Transactions","month":"Month"})
        fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                           margin=dict(t=10,b=10), height=280,
                           font=dict(family="Inter,Arial",size=12))
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: CATEGORY ANALYSIS
# ══════════════════════════════════════════════════
elif "Category" in page:
    st.markdown(section_header("🗂️ Spending Category Analysis"), unsafe_allow_html=True)
    df_cat = load_category()
    if not df_cat.empty:
        df_cat["total"] = df_cat["total"].astype(float)
        cat_grp = df_cat.groupby("category")["total"].sum().reset_index()

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(cat_grp, names="category", values="total", hole=0.4,
                         color_discrete_sequence=COLORS)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(paper_bgcolor="white", margin=dict(t=10,b=10), height=340)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(cat_grp.nlargest(10,"total"), x="total", y="category",
                          orientation="h", color_discrete_sequence=["#97144D"],
                          labels={"total":"Amount (₹)","category":""})
            fig2.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               yaxis={"categoryorder":"total ascending"},
                               margin=dict(t=10,b=10), height=340,
                               font=dict(family="Inter,Arial",size=11))
            st.plotly_chart(fig2, use_container_width=True)

        # Sub-category drill-down
        st.markdown(section_header("🔍 Sub-Category Breakdown"), unsafe_allow_html=True)
        selected_cat = st.selectbox("Select Category", sorted(df_cat["category"].unique()), key="mgmt_cat_sel")
        sub_df = df_cat[df_cat["category"] == selected_cat].sort_values("total", ascending=False)
        if not sub_df.empty:
            fig3 = px.bar(sub_df, x="sub_category", y="total",
                          color_discrete_sequence=["#ED1164"],
                          labels={"total":"Amount (₹)","sub_category":"Sub-Category"})
            fig3.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                               margin=dict(t=10,b=10), height=260,
                               font=dict(family="Inter,Arial",size=11))
            st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════
#  PAGE: TOP PERFORMERS
# ══════════════════════════════════════════════════
elif "Performers" in page:
    st.markdown(section_header("🏆 Top Customers by Balance"), unsafe_allow_html=True)
    df_top = load_top_customers()
    if not df_top.empty:
        df_top["closing_balance"]  = df_top["closing_balance"].astype(float)
        df_top["total_credits"]    = df_top["total_credits"].astype(float)
        df_top["total_debits"]     = df_top["total_debits"].astype(float)

        fig = px.bar(df_top.head(15), x="closing_balance", y="account_holder",
                     orientation="h",
                     color="closing_balance",
                     color_continuous_scale=["#FCEEF4","#AE275F","#97144D"],
                     labels={"closing_balance":"Balance (₹)","account_holder":"Customer"})
        fig.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          yaxis={"categoryorder":"total ascending"},
                          margin=dict(t=10,b=10), height=420,
                          font=dict(family="Inter,Arial",size=11))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(section_header("📋 Leaderboard"), unsafe_allow_html=True)
        tbl = df_top.copy()
        tbl["Rank"] = range(1, len(tbl)+1)
        tbl["closing_balance"]  = tbl["closing_balance"].apply(lambda x: f"₹{x:,.2f}")
        tbl["total_credits"]    = tbl["total_credits"].apply(lambda x: f"₹{float(x):,.2f}")
        tbl["total_debits"]     = tbl["total_debits"].apply(lambda x: f"₹{float(x):,.2f}")
        st.dataframe(tbl[["Rank","account_holder","account_number","closing_balance","total_credits","total_debits","total_transactions"]],
                     use_container_width=True)