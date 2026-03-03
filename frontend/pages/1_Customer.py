import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from frontend.utils.styles import (
    AXIS_CSS, navbar, metric_card, section_header,
    format_inr, format_inr_full, info_row, COLORS
)
from frontend.utils.api import post, get

st.set_page_config(
    page_title="Customer Banking | Axis Bank",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(AXIS_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
#  FLOATING CALCULATOR WIDGET
# ══════════════════════════════════════════════════
CALCULATOR_HTML = """
<div id="calcFab" onclick="toggleCalc()" title="Financial Calculator"
     style="position:fixed;bottom:28px;right:28px;width:58px;height:58px;
            background:linear-gradient(135deg,#97144D,#ED1164);
            border-radius:50%;display:flex;align-items:center;justify-content:center;
            cursor:pointer;box-shadow:0 6px 24px rgba(151,20,77,0.5);
            z-index:9999;transition:transform 0.3s,box-shadow 0.3s;font-size:24px;">
  🧮
</div>
<div id="calcPanel" style="display:none;position:fixed;bottom:100px;right:28px;width:320px;
     background:white;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,0.22);
     z-index:9998;overflow:hidden;border:1.5px solid rgba(151,20,77,0.15);
     animation:slideUp 0.25s ease;">
  <style>
    @keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
    .ci { width:100%;padding:9px 13px;border:1.5px solid #E5E7EB;border-radius:10px;
          font-size:13px;margin-bottom:10px;outline:none;font-family:Inter,Arial,sans-serif; }
    .ci:focus { border-color:#97144D; }
    .cb { width:100%;padding:10px;background:linear-gradient(135deg,#97144D,#ED1164);
          color:white;border:none;border-radius:10px;font-weight:700;font-size:13px;
          cursor:pointer;margin-top:8px;font-family:Inter,Arial,sans-serif; }
    .ct { display:flex;gap:5px;margin-bottom:16px;background:#F9FAFB;border-radius:10px;padding:4px; }
    .ctb { flex:1;text-align:center;padding:7px 4px;border-radius:8px;cursor:pointer;
           font-size:11px;font-weight:600;color:#6B7280;border:none;background:transparent;
           font-family:Inter,Arial,sans-serif;transition:all 0.2s; }
    .ctb.a { background:linear-gradient(135deg,#97144D,#ED1164);color:white; }
    .cr { background:linear-gradient(135deg,#FDF2F6,#FFF5F9);border-radius:12px;
          padding:14px;margin-top:12px;border:1.5px solid rgba(151,20,77,0.1);display:none; }
    .crl { font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.8px; }
    .crv { font-size:22px;font-weight:800;color:#97144D;margin-top:4px; }
    .crs { font-size:12px;color:#6B7280;margin-top:2px; }
  </style>
  <div style="background:linear-gradient(135deg,#97144D,#ED1164);color:white;padding:14px 18px;
              font-weight:700;font-size:15px;display:flex;justify-content:space-between;align-items:center;">
    <span>🧮 Financial Calculator</span>
    <span onclick="toggleCalc()" style="cursor:pointer;font-size:18px;opacity:0.8;">✕</span>
  </div>
  <div style="padding:18px;">
    <div class="ct">
      <button class="ctb a" onclick="switchTab('emi',this)">EMI</button>
      <button class="ctb" onclick="switchTab('savings',this)">Savings</button>
      <button class="ctb" onclick="switchTab('compound',this)">Compound</button>
    </div>
    <!-- EMI Calculator -->
    <div id="tab-emi">
      <input class="ci" id="emi-p" type="number" placeholder="Loan Amount (₹)" min="0"/>
      <input class="ci" id="emi-r" type="number" placeholder="Interest Rate (% per year)" step="0.1" min="0"/>
      <input class="ci" id="emi-n" type="number" placeholder="Tenure (months)" min="1"/>
      <button class="cb" onclick="calcEMI()">Calculate EMI</button>
      <div class="cr" id="res-emi">
        <div class="crl">Monthly EMI</div>
        <div class="crv" id="res-emi-val">—</div>
        <div class="crs" id="res-emi-sub"></div>
      </div>
    </div>
    <!-- Savings Calculator -->
    <div id="tab-savings" style="display:none;">
      <input class="ci" id="sv-g" type="number" placeholder="Financial Goal (₹)" min="0"/>
      <input class="ci" id="sv-r" type="number" placeholder="Interest Rate (% per year)" step="0.1" min="0"/>
      <input class="ci" id="sv-n" type="number" placeholder="Time Period (months)" min="1"/>
      <button class="cb" onclick="calcSavings()">Calculate Monthly Savings</button>
      <div class="cr" id="res-sv">
        <div class="crl">Monthly Saving Required</div>
        <div class="crv" id="res-sv-val">—</div>
        <div class="crs" id="res-sv-sub"></div>
      </div>
    </div>
    <!-- Compound Interest Calculator -->
    <div id="tab-compound" style="display:none;">
      <input class="ci" id="ci-p" type="number" placeholder="Principal Amount (₹)" min="0"/>
      <input class="ci" id="ci-r" type="number" placeholder="Interest Rate (% per year)" step="0.1" min="0"/>
      <input class="ci" id="ci-n" type="number" placeholder="Time Period (years)" min="1"/>
      <input class="ci" id="ci-f" type="number" placeholder="Compounding Frequency/year (e.g. 12)" min="1" value="12"/>
      <button class="cb" onclick="calcCI()">Calculate Growth</button>
      <div class="cr" id="res-ci">
        <div class="crl">Final Amount</div>
        <div class="crv" id="res-ci-val">—</div>
        <div class="crs" id="res-ci-sub"></div>
      </div>
    </div>
  </div>
</div>
<script>
function toggleCalc(){
  var p=document.getElementById('calcPanel');
  p.style.display=(p.style.display==='none'?'block':'none');
}
function switchTab(t,btn){
  ['emi','savings','compound'].forEach(function(id){
    var el=document.getElementById('tab-'+id);
    if(el) el.style.display=(id===t?'block':'none');
  });
  document.querySelectorAll('.ctb').forEach(function(b){b.classList.remove('a');});
  btn.classList.add('a');
}
function fmtINR(v){
  if(v>=1e7) return '₹'+(v/1e7).toFixed(2)+' Cr';
  if(v>=1e5) return '₹'+(v/1e5).toFixed(2)+' L';
  return '₹'+v.toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2});
}
function calcEMI(){
  var p=parseFloat(document.getElementById('emi-p').value)||0;
  var r=parseFloat(document.getElementById('emi-r').value)||0;
  var n=parseInt(document.getElementById('emi-n').value)||0;
  if(!p||!r||!n){return;}
  var mr=r/12/100;
  var emi=p*mr*Math.pow(1+mr,n)/(Math.pow(1+mr,n)-1);
  var total=emi*n;
  var interest=total-p;
  var res=document.getElementById('res-emi');
  document.getElementById('res-emi-val').innerText=fmtINR(emi);
  document.getElementById('res-emi-sub').innerText='Total: '+fmtINR(total)+' | Interest: '+fmtINR(interest);
  res.style.display='block';
}
function calcSavings(){
  var g=parseFloat(document.getElementById('sv-g').value)||0;
  var r=parseFloat(document.getElementById('sv-r').value)||0;
  var n=parseInt(document.getElementById('sv-n').value)||0;
  if(!g||!n){return;}
  var mr=r/12/100;
  var sip=mr>0?g*mr/(Math.pow(1+mr,n)-1):g/n;
  var res=document.getElementById('res-sv');
  document.getElementById('res-sv-val').innerText=fmtINR(sip);
  document.getElementById('res-sv-sub').innerText='Total investment: '+fmtINR(sip*n);
  res.style.display='block';
}
function calcCI(){
  var p=parseFloat(document.getElementById('ci-p').value)||0;
  var r=parseFloat(document.getElementById('ci-r').value)||0;
  var n=parseFloat(document.getElementById('ci-n').value)||0;
  var f=parseFloat(document.getElementById('ci-f').value)||12;
  if(!p||!r||!n){return;}
  var A=p*Math.pow(1+r/(100*f),f*n);
  var interest=A-p;
  var res=document.getElementById('res-ci');
  document.getElementById('res-ci-val').innerText=fmtINR(A);
  document.getElementById('res-ci-sub').innerText='Principal: '+fmtINR(p)+' | Interest earned: '+fmtINR(interest);
  res.style.display='block';
}
</script>
"""

# ══════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════
if not st.session_state.get("token") or st.session_state.get("role") != "customer":
    st.markdown(navbar("Customer Banking Portal"), unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class="login-container">
            <div class="login-logo">
                <div class="login-logo-text">AXIS <span>BANK</span></div>
            </div>
            <div class="login-title">Secure Customer Login</div>
            <div class="login-subtitle">Enter your account details to access your personal banking dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-form-body">', unsafe_allow_html=True)
        acc  = st.text_input("Account Number", placeholder="Enter your account number", key="c_acc")
        name = st.text_input("Full Name", placeholder="Enter your name", key="c_name")
        ifsc = st.text_input("IFSC Code", placeholder="Enter your IFSC Code", key="c_ifsc")

        if st.button("🔐 Access My Dashboard", key="cust_login_btn"):
            if acc and name and ifsc:
                with st.spinner("Verifying credentials..."):
                    resp, code = post("/auth/customer/login", {
                        "account_number": acc,
                        "name": name,
                        "ifsc_code": ifsc
                    })
                if code == 200:
                    st.session_state["token"] = resp["access_token"]
                    st.session_state["role"]  = "customer"
                    st.session_state["name"]  = resp["name"]
                    st.success(f"✅ Welcome, {resp['name']}! Loading dashboard...")
                    st.rerun()
                else:
                    st.error(f"❌ {resp.get('detail', 'Login failed. Check your credentials.')}")
            else:
                st.warning("⚠️ Please fill all three fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    col1_, col2_ = st.columns(2)
    with col1_:
        if st.button("← Back to Home", key="cust_back"):
            st.switch_page("app.py")
    st.stop()

# ══════════════════════════════════════════════════
#  DASHBOARD — inject floating calculator
# ══════════════════════════════════════════════════
components.html(CALCULATOR_HTML, height=0, scrolling=False)

user_name = st.session_state.get("name", "Customer")
st.markdown(navbar("My Banking Dashboard", user_name, "customer"), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {user_name}")
    st.markdown("---")
    page = st.radio("Navigate to", [
        "📊 Overview",
        "💳 Transactions",
        "📈 Spending Analysis",
        "📉 Balance Trend",
        "💰 Cash Flow"
    ], key="cust_page")
    st.markdown("---")
    if st.button("🚪 Logout", key="cust_logout"):
        for k in ["token","role","name"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")

# ── Data Loading ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_profile():
    data, _ = get("/customer/profile")
    return data or {}

@st.cache_data(ttl=300)
def load_categories():
    data, _ = get("/customer/categories")
    return data if isinstance(data, dict) else {}

@st.cache_data(ttl=120)
def load_transactions(cat=None, sub_cat=None, typ=None, d_from=None, d_to=None, search=None, limit=200, offset=0):
    params = {"limit": limit, "offset": offset}
    if cat:     params["category"]     = cat
    if sub_cat: params["sub_category"] = sub_cat
    if typ:     params["txn_type"]     = typ
    if d_from:  params["date_from"]    = d_from
    if d_to:    params["date_to"]      = d_to
    if search:  params["search"]       = search
    data, _ = get("/customer/transactions", params)
    if isinstance(data, dict) and "data" in data:
        return pd.DataFrame(data["data"]), data.get("total", 0)
    return pd.DataFrame(), 0

@st.cache_data(ttl=300)
def load_monthly():
    data, _ = get("/customer/summary/monthly")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_category_summary():
    data, _ = get("/customer/summary/category")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_balance_trend():
    data, _ = get("/customer/summary/balance_trend")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_cashflow():
    data, _ = get("/customer/summary/cashflow")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

@st.cache_data(ttl=300)
def load_top_merchants():
    data, _ = get("/customer/summary/top_merchants")
    return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame()

profile  = load_profile()
cat_map  = load_categories()

# ══════════════════════════════════════════════════
#  PAGE: OVERVIEW
# ══════════════════════════════════════════════════
if "Overview" in page:
    # Balance hero card
    closing  = profile.get("closing_balance", 0)
    credits  = profile.get("total_credits", 0)
    debits   = profile.get("total_debits", 0)
    opening  = profile.get("opening_balance", 0)
    txn_cnt  = profile.get("total_transactions", 0)

    col_balance, col_stats = st.columns([1, 2])
    with col_balance:
        st.markdown(f"""
        <div class="balance-gauge-container">
            <div class="balance-gauge-label">💳 Current Balance</div>
            <div class="balance-gauge-value">{format_inr(closing)}</div>
            <div class="balance-gauge-sub">{profile.get('account_type','Savings')} Account</div>
        </div>
        """, unsafe_allow_html=True)
        # Credit/Debit bar
        total_flow = float(credits) + float(debits)
        credit_pct = (float(credits) / total_flow * 100) if total_flow > 0 else 50
        st.markdown(f"""
        <div style="margin-top:18px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#6B7280;margin-bottom:4px;">
                <span>💚 Credits {format_inr(credits)}</span>
                <span>❤️ Debits {format_inr(debits)}</span>
            </div>
            <div class="axis-progress-bar">
                <div class="axis-progress-fill" style="width:{credit_pct:.1f}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_stats:
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            st.markdown(metric_card("Total Credits", format_inr(credits), "All time", "green"), unsafe_allow_html=True)
        with r1c2:
            st.markdown(metric_card("Total Debits", format_inr(debits), "All time", "pink"), unsafe_allow_html=True)
        with r1c3:
            st.markdown(metric_card("Transactions", f"{int(txn_cnt):,}", "Total count"), unsafe_allow_html=True)

        net = float(credits) - float(debits)
        net_color = "green" if net >= 0 else "pink"
        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            st.markdown(metric_card("Net Flow", format_inr(abs(net)), "▲ Surplus" if net >= 0 else "▼ Deficit", net_color), unsafe_allow_html=True)
        with r2c2:
            st.markdown(metric_card("Opening Balance", format_inr(opening), "Statement start"), unsafe_allow_html=True)
        with r2c3:
            avg_txn = float(debits) / int(txn_cnt) if int(txn_cnt) > 0 else 0
            st.markdown(metric_card("Avg Transaction", format_inr(avg_txn), "Per debit"), unsafe_allow_html=True)

    # Account details + Monthly chart
    col_l, col_r = st.columns([1, 1.4])
    with col_l:
        st.markdown(section_header("📋 Account Details"), unsafe_allow_html=True)
        details = [
            ("Account Holder",  profile.get("account_holder", "")),
            ("Account Number",  profile.get("account_number", "")),
            ("Account Type",    profile.get("account_type", "")),
            ("IFSC Code",       profile.get("ifsc_code", "")),
            ("Branch",          profile.get("branch", "")),
            ("Customer ID",     profile.get("customer_id", "")),
            ("Currency",        profile.get("currency", "INR")),
            ("Statement Period",profile.get("statement_period", "")),
        ]
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        for k, v in details:
            st.markdown(info_row(k, v), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown(section_header("📊 Monthly Income vs Expense"), unsafe_allow_html=True)
        df_m = load_monthly()
        if not df_m.empty:
            fig = go.Figure()
            fig.add_bar(x=df_m["month"], y=df_m["total_credit"], name="Income ₹",
                        marker_color="#10B981", marker_line_width=0)
            fig.add_bar(x=df_m["month"], y=df_m["total_debit"], name="Expense ₹",
                        marker_color="#97144D", marker_line_width=0)
            fig.update_layout(
                barmode="group",
                plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", y=1.12),
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                font=dict(family="Inter, Arial", size=12),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available.")

# ══════════════════════════════════════════════════
#  PAGE: TRANSACTIONS
# ══════════════════════════════════════════════════
elif "Transactions" in page:
    st.markdown(section_header("💳 Transaction History"), unsafe_allow_html=True)

    # Filter row
    f1, f2, f3, f4, f5 = st.columns([2, 2, 1.5, 1.5, 1.5])
    with f1:
        cat_options = ["All Categories"] + sorted(cat_map.keys())
        sel_cat = st.selectbox("Category", cat_options, key="txn_cat")
    with f2:
        if sel_cat != "All Categories" and sel_cat in cat_map:
            sub_opts = ["All Sub-Categories"] + sorted(cat_map[sel_cat])
        else:
            sub_opts = ["All Sub-Categories"]
        sel_sub = st.selectbox("Sub-Category", sub_opts, key="txn_sub")
    with f3:
        sel_type = st.selectbox("Type", ["All", "CR", "DR"], key="txn_type")
    with f4:
        d_from = st.date_input("From Date", value=None, key="txn_from")
    with f5:
        d_to = st.date_input("To Date", value=None, key="txn_to")

    cat_val  = None if sel_cat == "All Categories" else sel_cat
    sub_val  = None if sel_sub == "All Sub-Categories" else sel_sub
    type_val = None if sel_type == "All" else sel_type

    df, total_count = load_transactions(
        cat=cat_val,
        sub_cat=sub_val,
        typ=type_val,
        d_from=str(d_from) if d_from else None,
        d_to=str(d_to) if d_to else None,
        limit=200
    )

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:12px;">
        <span style="color:#97144D;font-weight:700;font-size:15px;">
            Showing {len(df):,} of {total_count:,} transactions
        </span>
        {f'<span style="background:#FDF2F6;border-radius:20px;padding:3px 12px;font-size:12px;color:#97144D;font-weight:600;">Category: {cat_val}</span>' if cat_val else ''}
        {f'<span style="background:#FFF5F9;border-radius:20px;padding:3px 12px;font-size:12px;color:#ED1164;font-weight:600;">Sub: {sub_val}</span>' if sub_val else ''}
    </div>
    """, unsafe_allow_html=True)

    if not df.empty:
        display_df = df.copy()
        display_df["debit"]  = display_df["debit"].apply(
            lambda x: f"₹{float(x):,.2f}" if float(x) > 0 else "—")
        display_df["credit"] = display_df["credit"].apply(
            lambda x: f"₹{float(x):,.2f}" if float(x) > 0 else "—")
        display_df["balance"] = display_df["balance"].apply(lambda x: f"₹{float(x):,.2f}")
        display_df = display_df[[
            "date", "description", "reference",
            "transaction_type", "debit", "credit", "balance",
            "category", "sub_category"
        ]].rename(columns={
            "transaction_type": "Type",
            "sub_category": "Sub Category"
        })
        st.dataframe(display_df, use_container_width=True, height=480)
    else:
        st.info("No transactions found for the selected filters.")

# ══════════════════════════════════════════════════
#  PAGE: SPENDING ANALYSIS
# ══════════════════════════════════════════════════
elif "Spending" in page:
    df_cat = load_category_summary()
    df_top = load_top_merchants()

    if not df_cat.empty:
        df_debit = df_cat[df_cat["total_spent"] > 0].copy()
        df_debit["total_spent"] = df_debit["total_spent"].astype(float)

        # Row 1: Donut + Horizontal bar
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(section_header("🍩 Spending by Category"), unsafe_allow_html=True)
            cat_group = df_debit.groupby("category")["total_spent"].sum().reset_index()
            fig_pie = px.pie(
                cat_group, names="category", values="total_spent",
                color_discrete_sequence=COLORS, hole=0.45
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                paper_bgcolor="white", margin=dict(t=20, b=20),
                showlegend=True,
                legend=dict(orientation="v", x=1, y=0.5),
                font=dict(family="Inter, Arial", size=12),
                height=320
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with c2:
            st.markdown(section_header("📊 Top Sub-Categories"), unsafe_allow_html=True)
            top15 = df_debit.nlargest(15, "total_spent")
            fig_bar = px.bar(
                top15, x="total_spent", y="sub_category",
                orientation="h", color="category",
                color_discrete_sequence=COLORS,
                labels={"total_spent": "Amount (₹)", "sub_category": ""}
            )
            fig_bar.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                yaxis={"categoryorder": "total ascending"},
                margin=dict(t=10, b=10, l=10, r=10),
                height=320,
                font=dict(family="Inter, Arial", size=11),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Row 2: Treemap
        st.markdown(section_header("🗺️ Spending Treemap"), unsafe_allow_html=True)
        fig_tree = px.treemap(
            df_debit,
            path=["category", "sub_category"],
            values="total_spent",
            color="total_spent",
            color_continuous_scale=["#FCEEF4", "#AE275F", "#97144D"],
        )
        fig_tree.update_layout(
            paper_bgcolor="white",
            margin=dict(t=10, b=10, l=10, r=10),
            height=380,
            font=dict(family="Inter, Arial")
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        # Row 3: Top merchants + category table
        c3, c4 = st.columns([1, 1])
        with c3:
            st.markdown(section_header("🏪 Top Merchants / Payees"), unsafe_allow_html=True)
            if not df_top.empty:
                df_top["total"] = df_top["total"].astype(float)
                fig_m = px.bar(
                    df_top.head(10), x="total", y="merchant",
                    orientation="h", color_discrete_sequence=["#ED1164"],
                    labels={"total": "Amount (₹)", "merchant": ""}
                )
                fig_m.update_layout(
                    paper_bgcolor="white", plot_bgcolor="white",
                    yaxis={"categoryorder": "total ascending"},
                    margin=dict(t=10, b=10, l=10, r=10),
                    height=300,
                    font=dict(family="Inter, Arial", size=11)
                )
                st.plotly_chart(fig_m, use_container_width=True)
        with c4:
            st.markdown(section_header("📋 Category Breakdown"), unsafe_allow_html=True)
            tbl = df_debit.groupby("category").agg(
                Total_Spent=("total_spent","sum"),
                Transactions=("txn_count","sum")
            ).reset_index().sort_values("Total_Spent", ascending=False)
            tbl["Total_Spent"] = tbl["Total_Spent"].apply(lambda x: f"₹{x:,.2f}")
            tbl["Transactions"] = tbl["Transactions"].astype(int)
            st.dataframe(tbl, use_container_width=True, height=300)
    else:
        st.info("No spending data available.")

# ══════════════════════════════════════════════════
#  PAGE: BALANCE TREND
# ══════════════════════════════════════════════════
elif "Balance" in page:
    df_bal = load_balance_trend()
    if not df_bal.empty:
        df_bal["balance"] = df_bal["balance"].astype(float)
        df_bal["date"] = pd.to_datetime(df_bal["date"])

        st.markdown(section_header("📉 Account Balance Over Time"), unsafe_allow_html=True)

        fig = go.Figure()
        fig.add_scatter(
            x=df_bal["date"], y=df_bal["balance"],
            fill="tozeroy",
            line=dict(color="#97144D", width=2.5),
            fillcolor="rgba(151,20,77,0.08)",
            name="Balance",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Balance: ₹%{y:,.2f}<extra></extra>"
        )
        # Add min/max markers
        min_idx = df_bal["balance"].idxmin()
        max_idx = df_bal["balance"].idxmax()
        fig.add_scatter(
            x=[df_bal.loc[max_idx, "date"]],
            y=[df_bal.loc[max_idx, "balance"]],
            mode="markers+text",
            marker=dict(color="#10B981", size=12, symbol="triangle-up"),
            text=["Peak"],
            textposition="top center",
            name="Peak",
            hovertemplate=f"Peak: ₹{df_bal.loc[max_idx,'balance']:,.2f}<extra></extra>"
        )
        fig.add_scatter(
            x=[df_bal.loc[min_idx, "date"]],
            y=[df_bal.loc[min_idx, "balance"]],
            mode="markers+text",
            marker=dict(color="#EF4444", size=12, symbol="triangle-down"),
            text=["Low"],
            textposition="bottom center",
            name="Lowest",
            hovertemplate=f"Lowest: ₹{df_bal.loc[min_idx,'balance']:,.2f}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            yaxis_title="Balance (₹)",
            xaxis_title="Date",
            margin=dict(t=20, b=20, l=20, r=20),
            height=380,
            hovermode="x unified",
            legend=dict(orientation="h", y=1.12),
            font=dict(family="Inter, Arial", size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Stats
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(metric_card("Current Balance", format_inr(df_bal["balance"].iloc[-1]), "Latest"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Peak Balance", format_inr(df_bal["balance"].max()), str(df_bal.loc[max_idx, "date"].strftime("%d %b %Y")), "green"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Lowest Balance", format_inr(df_bal["balance"].min()), str(df_bal.loc[min_idx, "date"].strftime("%d %b %Y")), "pink"), unsafe_allow_html=True)
        with c4: st.markdown(metric_card("Average Balance", format_inr(df_bal["balance"].mean()), "All time"), unsafe_allow_html=True)
    else:
        st.info("No balance trend data available.")

# ══════════════════════════════════════════════════
#  PAGE: CASH FLOW
# ══════════════════════════════════════════════════
elif "Cash Flow" in page:
    df_cf = load_cashflow()
    if not df_cf.empty:
        df_cf["net_flow"] = df_cf["net_flow"].astype(float)
        df_cf["income"]   = df_cf["income"].astype(float)
        df_cf["expense"]  = df_cf["expense"].astype(float)

        st.markdown(section_header("💰 Monthly Cash Flow Analysis"), unsafe_allow_html=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.6, 0.4], vertical_spacing=0.08)
        fig.add_bar(row=1, col=1, x=df_cf["month"], y=df_cf["income"],
                    name="Income", marker_color="#10B981")
        fig.add_bar(row=1, col=1, x=df_cf["month"], y=df_cf["expense"],
                    name="Expense", marker_color="#97144D")
        colors = ["#10B981" if v >= 0 else "#EF4444" for v in df_cf["net_flow"]]
        fig.add_bar(row=2, col=1, x=df_cf["month"], y=df_cf["net_flow"],
                    name="Net Flow", marker_color=colors)
        fig.add_hline(y=0, row=2, col=1, line_dash="dash", line_color="#6B7280")
        fig.update_layout(
            barmode="group",
            paper_bgcolor="white", plot_bgcolor="white",
            height=480,
            margin=dict(t=20, b=20),
            legend=dict(orientation="h", y=1.05),
            font=dict(family="Inter, Arial", size=12)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary cards
        avg_net = df_cf["net_flow"].mean()
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(metric_card("Avg Monthly Income", format_inr(df_cf["income"].mean()), "Per month", "green"), unsafe_allow_html=True)
        with c2: st.markdown(metric_card("Avg Monthly Expense", format_inr(df_cf["expense"].mean()), "Per month", "pink"), unsafe_allow_html=True)
        with c3: st.markdown(metric_card("Avg Net Flow", format_inr(abs(avg_net)), "▲ Surplus" if avg_net >= 0 else "▼ Deficit", "green" if avg_net >= 0 else "pink"), unsafe_allow_html=True)
        with c4:
            surplus_months = int((df_cf["net_flow"] > 0).sum())
            st.markdown(metric_card("Surplus Months", f"{surplus_months} / {len(df_cf)}", "Months with positive flow"), unsafe_allow_html=True)
    else:
        st.info("No cash flow data available.")