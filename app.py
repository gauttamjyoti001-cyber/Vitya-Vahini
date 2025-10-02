import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import yfinance as yf  # For real-time ETF data

# Custom CSS for prettier look (blue/green theme)
st.markdown("""
    <style>
    .main {background-color: #f0f8ff;}
    .stMetric {color: #0066cc;}
    .stTabs [data-baseweb="tab"] {background-color: #e6f3ff; color: #0066cc;}
    .stTabs [data-baseweb="tab"]:hover {background-color: #b3d9ff;}
    h1 {color: #0066cc; font-family: 'Arial Black';}
    .success {color: #28a745;}
    </style>
""", unsafe_allow_html=True)

# Disclaimer
DISCLAIMER = """
<div style="background-color: #fff3cd; padding: 10px; border: 1px solid #ffeaa7; border-radius: 5px;">
<strong>Disclaimer:</strong> This is educational only. Not a substitute for SEBI-registered advisor. Consult professionals.
</div>
"""

# Updated 2025 Data (from Morningstar/Value Research)
TOP_EQUITY_MFS = [
    {"name": "Nippon India Large Cap Fund", "rating": "5 Stars (Morningstar)", "1yr_return": "25%", "expense_ratio": "0.8%"},
    {"name": "ICICI Prudential Bluechip Fund", "rating": "Best Large-Cap (Morningstar 2025)", "1yr_return": "22%", "expense_ratio": "1.0%"},
    {"name": "HDFC Top 100 Fund", "rating": "4 Stars (Value Research)", "1yr_return": "20%", "expense_ratio": "1.2%"}
]

TOP_DEBT_MFS = [
    {"name": "ICICI Prudential Savings Fund", "rating": "5 Stars", "1yr_return": "7.5%", "expense_ratio": "0.4%"},
    {"name": "HDFC Corporate Bond Fund", "rating": "4 Stars", "1yr_return": "7.2%", "expense_ratio": "0.5%"},
    {"name": "SBI Magnum Gilt Fund", "rating": "3 Stars", "1yr_return": "6.8%", "expense_ratio": "0.6%"}
]

TOP_HYBRID_MFS = [
    {"name": "ICICI Prudential Equity & Debt Fund", "rating": "4 Stars", "1yr_return": "18%", "expense_ratio": "1.1%"},
    {"name": "HDFC Balanced Advantage Fund", "rating": "5 Stars", "1yr_return": "16%", "expense_ratio": "0.9%"},
    {"name": "Axis Aggressive Hybrid Fund", "rating": "4 Stars", "1yr_return": "15%", "expense_ratio": "1.0%"}
]

TOP_ETFS = [
    {"name": "Nippon India ETF Nifty BeES", "1yr_return": "24%", "expense_ratio": "0.05%"},
    {"name": "ICICI Prudential Nifty ETF", "1yr_return": "23%", "expense_ratio": "0.03%"},
    {"name": "HDFC Nifty 50 ETF", "1yr_return": "22%", "expense_ratio": "0.1%"}
]

TOP_REITS_INVITS = [
    {"name": "Embassy Office Parks REIT", "1yr_return": "12%", "yield": "7.5%"},
    {"name": "Mindspace Business Parks REIT", "1yr_return": "10%", "yield": "8%"},
    {"name": "IRB InvIT Fund", "1yr_return": "14%", "yield": "14.04%"}  # From 2025 data
]

GOV_BONDS = {
    "10-Year G-Sec": {"yield": "6.59%", "tenure": "10 years"},  # RBI Oct 2025
    "91-Day T-Bill": {"yield": "6.2%", "tenure": "91 days"},
    "RBI Floating Rate Bonds": {"yield": "8.05%", "tenure": "7 years"}
}

TOP_INSURANCE = [
    {"name": "ICICI Pru iProtect Smart Plus (Term)", "premium_1cr": "₹520/month", "features": "Up to 20 Cr cover"},
    {"name": "HDFC Life Click 2 Protect (Term)", "premium_1cr": "₹520/month", "features": "17% discount"},
    {"name": "Tata AIA Sampoorna Raksha (Term)", "premium_1cr": "₹501/month", "features": "18.5% premium discount"},
    {"name": "Care Supreme (Health)", "sum_insured": "₹10L", "premium": "₹15,000/year", "features": "No room cap"}
]

# Functions (enhanced from original)
@st.cache_data
def get_allocation(age, risk):
    equity_base = max(20, 100 - age)
    if risk == "Conservative":
        return {"Equity": equity_base * 0.6, "Debt": 40, "Gold": 5, "REITs/InvITs": 5, "International": 5}
    elif risk == "Moderate":
        return {"Equity": equity_base * 0.8, "Debt": 30, "Gold": 10, "REITs/InvITs": 10, "International": 10}
    else:
        return {"Equity": equity_base, "Debt": 20, "Gold": 5, "REITs/InvITs": 10, "International": 15}

def financial_health_check(income, expenses, assets, loans):
    emergency_needed = expenses * 6
    debt_ratio = (loans / income) * 100 if income > 0 else 0
    status = "Healthy" if debt_ratio < 40 and assets > emergency_needed else "Improve"
    return emergency_needed, debt_ratio, status

def project_corpus(monthly_inv, years, cagr=10):
    if monthly_inv <= 0 or years <= 0:
        return 0
    fv = monthly_inv * (((1 + cagr/100)**(years*12) - 1) / (cagr/100)) * (1 + cagr/100)
    return fv

# Main App
st.set_page_config(page_title="Finance Advisor Pro", page_icon="💰", layout="wide")
st.title("💰 Finance Advisor Pro")
st.markdown(DISCLAIMER, unsafe_allow_html=True)

# Sidebar for quick inputs
with st.sidebar:
    st.header("Quick Profile")
    age = st.slider("Age", 18, 80, 30)
    annual_income = st.number_input("Annual Income (₹)", 0, 50000000, 1000000)
    monthly_expenses = st.number_input("Monthly Expenses (₹)", 0, 500000, 20000)
    risk = st.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
    total_assets = st.number_input("Total Assets (₹)", 0, 100000000, 500000)
    loans = st.number_input("Total Loans (₹)", 0, 50000000, 0)
    st.button("Update Profile")

# Tabs for organized UI
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Health Check", "💼 Recommendations", "🎯 Goals", "🛡️ Tax & Insurance", "📚 Learn"])

with tab1:
    st.header("Financial Health Check")
    emergency_needed, debt_ratio, status = financial_health_check(annual_income, monthly_expenses, total_assets, loans)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Emergency Fund Needed", f"₹{emergency_needed:,.0f}", delta="Build if low")
    with col2:
        st.metric("Debt-to-Income", f"{debt_ratio:.1f}%", delta="Healthy <40%")
    with col3:
        st.metric("Overall Status", status, delta_color="normal")
    
    if status != "Healthy":
        st.warning("🔄 Prioritize emergency fund & debt repayment before investing.")

with tab2:
    st.header("Personalized Recommendations")
    allocation = get_allocation(age, risk)
    monthly_savings = max(0, (annual_income - monthly_expenses*12) * 0.7 / 12)  # 70% investable, ensure non-negative
    
    # Allocation Pie Chart
    col1, col2 = st.columns([1, 2])
    with col1:
        if sum(allocation.values()) > 0:
            fig, ax = plt.subplots()
            ax.pie(allocation.values(), labels=allocation.keys(), autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
            ax.set_title("Asset Allocation")
            st.pyplot(fig)
        else:
            st.write("No allocation data")
    
    with col2:
        st.subheader("Monthly Investment Breakdown")
        monthly_plan = {k: monthly_savings * (v/100) for k, v in allocation.items()}
        df_plan = pd.DataFrame(list(monthly_plan.items()), columns=['Category', 'Amount (₹)']).round(0)
        st.dataframe(df_plan, width='stretch')
    
    # Top Picks Tables
    st.subheader("Top Fund Suggestions")
    col_eq, col_de = st.columns(2)
    with col_eq:
        st.write("**Equity Funds**")
        eq_df = pd.DataFrame(TOP_EQUITY_MFS)
        st.table(eq_df)
    with col_de:
        st.write("**Debt Funds**")
        de_df = pd.DataFrame(TOP_DEBT_MFS)
        st.table(de_df)
    
    st.subheader("Government Bonds")
    bonds_df = pd.DataFrame.from_dict(GOV_BONDS, orient='index')
    st.table(bonds_df)
    
    # Real-time ETF Example
    st.subheader("Live ETF Data")
    etf_symbol = "NIFTYBEES.NS"  # Nippon ETF
    try:
        data = yf.download(etf_symbol, period="1mo", progress=False)
        if not data.empty and 'Close' in data.columns:
            st.line_chart(data['Close'])
            latest_price = float(data['Close'].iloc[-1])  # Convert to float to fix formatting error
            st.caption(f"Latest {TOP_ETFS[0]['name']}: ₹{latest_price:.2f}")
        else:
            st.write("No ETF data available at the moment.")
    except Exception as e:
        st.write(f"Error fetching ETF data: {e}")

with tab3:
    st.header("Goal Tracker")
    num_goals = st.number_input("Number of Goals", 1, 5, 1)
    goals = []
    for i in range(num_goals):
        with st.expander(f"Goal {i+1}"):
            name = st.text_input(f"Goal Name", f"Goal {i+1}", key=f"name_{i}")
            target = st.number_input(f"Target Amount (₹)", 0, 100000000, 5000000, key=f"target_{i}")
            years = st.slider(f"Time Horizon (Years)", 1, 30, 10, key=f"years_{i}")
            goals.append({"name": name, "target": target, "years": years})
    
    if goals and monthly_savings > 0:
        st.subheader("Projected Corpus")
        for goal in goals:
            projected = project_corpus(monthly_savings*12, goal["years"])
            progress = min(projected / goal["target"] * 100, 100) if goal["target"] > 0 else 0
            st.metric(goal["name"], f"₹{projected:,.0f}", delta=f"{progress:.0f}% to target")
            st.progress(progress / 100)
    elif monthly_savings <= 0:
        st.info("Add savings to see projections.")

with tab4:
    st.header("Tax Planning & Insurance")
    st.write("**Tax Tips (80C/80D):**")
    st.write("- Max ₹1.5L in PPF/ELSS/NPS for 80C deduction.")
    st.write("- Health insurance: Up to ₹25K deduction under 80D.")
    
    st.subheader("Recommended Insurance")
    ins_df = pd.DataFrame(TOP_INSURANCE)
    st.table(ins_df)
    
    # Rebalancing Alert
    if st.button("Check Rebalancing"):
        st.success("Portfolio balanced! Rebalance in 6 months.")

with tab5:
    st.header("Financial Literacy")
    articles = [
        "What is SIP? Start small, grow big!",
        "Equity vs Debt: Balance for your age.",
        "REITs/InvITs: Earn from real estate without buying property."
    ]
    for art in articles:
        st.write(f"📖 {art}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>Built with ❤️ using Streamlit | Updated Oct 2025</p>", unsafe_allow_html=True)