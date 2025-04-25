import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

from utils.amortization import calculate_minimum_payment, generate_amortization_schedule
from utils.strategies import simulate_baseline, simulate_full_strategy
from charts.visuals import plot_loan_timeline_plotly, plot_strategy_comparison_plotly

# Detect browser width and set layout mode
screen_width = streamlit_js_eval(js_expressions="screen.width", key="screen_width")
layout_mode = "mobile" if screen_width and screen_width < 700 else "desktop"

st.set_page_config(page_title="Student Loan Simulator", layout="wide")
st.title("🎓 Student Loan Payoff Simulator")
st.markdown("Simulate your loan repayment plan, see how extra payments make a difference, and visualize your path to debt freedom.")

st.header("Step 1: Enter Your Loan Details")

# Collapse/Expand control
if "loan_expanded" not in st.session_state:
    st.session_state.loan_expanded = True

col_expand, col_collapse = st.columns([1, 1])
with col_expand:
    if st.button("🔼 Expand All Loan Fields"):
        st.session_state.loan_expanded = True
with col_collapse:
    if st.button("🔽 Collapse All Loan Fields"):
        st.session_state.loan_expanded = False

num_loans = st.number_input("How many loans do you want to enter?", min_value=1, max_value=10, value=3)
loan_inputs = []

for i in range(num_loans):
    with st.expander(f"Loan {i + 1}", expanded=st.session_state.loan_expanded):
        if layout_mode == "mobile":
            cols = [st] * 4  # simulate stacked layout
        else:
            cols = st.columns(4)
        with cols[0]:
            loan_name = st.text_input(f"Loan Name {i}", value=f"Loan {chr(65+i)}", key=f"name_{i}")
        with cols[1]:
            balance = st.number_input(f"Balance {i}", value=10000, min_value=0, key=f"balance_{i}")
        with cols[2]:
            rate = st.number_input(f"Interest Rate {i}", value=5.0, min_value=0.0, key=f"rate_{i}")
        with cols[3]:
            term = st.number_input(f"Term {i}", value=120, min_value=1, max_value=360, key=f"term_{i}")

        loan_inputs.append({
            "loan_name": loan_name,
            "balance": balance,
            "interest_rate": rate,
            "term_months": term
        })

# --- Show Loan Summary Table ---
if loan_inputs:
    st.subheader("📋 Loan Summary")
    loan_summary = []
    for loan in loan_inputs:
        min_payment = calculate_minimum_payment(loan["balance"], loan["interest_rate"], loan["term_months"])
        loan_summary.append({
            "Loan Name": loan["loan_name"],
            "Balance ($)": f"${loan['balance']:,.2f}",
            "Interest Rate (%)": f"{loan['interest_rate']}%",
            "Term (months)": loan["term_months"],
            "Minimum Payment ($)": f"${min_payment:,.2f}"
        })

    df_summary = pd.DataFrame(loan_summary)
    st.dataframe(df_summary, use_container_width=True)

    total_min_payment = sum(
        calculate_minimum_payment(l["balance"], l["interest_rate"], l["term_months"]) for l in loan_inputs
    )
    st.markdown(f"**💵 Combined Minimum Monthly Payment: ${total_min_payment:,.2f}**")
    st.markdown("### Do you have any extra money in your budget to apply toward your loans?")

# --- Step 2: Strategy Selection ---
st.header("Step 2: Strategy Selection")

strategy = st.selectbox("Repayment Strategy", options=["Avalanche", "Snowball"], index=0)

# Dynamic explanation
if strategy == "Avalanche":
    st.markdown("""
    **Avalanche Method:**  
    This method focuses on paying off the **loan with the highest interest rate first**, while making minimum payments on the rest.  
    It helps you **pay less in total interest** and become debt-free faster.  
    Best for those who want to **maximize savings over time**.
    """)
elif strategy == "Snowball":
    st.markdown("""
    **Snowball Method:**  
    This method pays off the **smallest loan balance first** to build momentum.  
    It gives you quick wins and motivation early on, then rolls payments into the next loan.  
    Best for those who prefer **psychological motivation** over strict efficiency.
    """)

extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0, value=150)

if st.button("Simulate Repayment"):
    st.success("Calculating your optimized repayment plan...")

    # Baseline calculation
    baseline_interest, baseline_months, _ = simulate_baseline(loan_inputs)

    # Strategy calculation
    strategy_loans = [loan.copy() for loan in loan_inputs]
    schedule_df = simulate_full_strategy(strategy_loans, extra_payment, strategy=strategy.lower())
    total_interest = schedule_df["Interest Paid"].sum()
    final_month = schedule_df["Month"].max()

    # Summary
    st.subheader("📊 Summary Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Interest Saved", f"${baseline_interest - total_interest:,.2f}")
        st.metric("Time Saved", f"{baseline_months - final_month} months")
    with col2:
        st.metric("Total Interest (Standard)", f"${baseline_interest:,.2f}")
        st.metric("Total Interest (Strategy)", f"${total_interest:,.2f}")

    # Charts
    st.subheader("📈 Loan Payoff Timeline")
    plot_loan_timeline_plotly(schedule_df, loan_inputs)

    st.subheader("📉 Aggressive vs. Minimum Payment")
    plot_strategy_comparison_plotly(loan_inputs, schedule_df, extra_payment)

    # Optional CSV export (future)
    # st.download_button("Download Schedule CSV", schedule_df.to_csv(), file_name="loan_schedule.csv")
