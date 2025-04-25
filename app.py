import streamlit as st
from utils.amortization import calculate_minimum_payment, generate_amortization_schedule
from utils.strategies import simulate_baseline, simulate_full_strategy
from charts.visuals import plot_loan_timeline_plotly, plot_strategy_comparison_plotly

st.set_page_config(page_title="Student Loan Simulator", layout="wide")
st.title("🎓 Student Loan Payoff Simulator")
st.markdown("Simulate your loan repayment plan, see how extra payments make a difference, and visualize your path to debt freedom.")

st.header("Step 1: Enter Your Loan Details")

loan_inputs = []
default_loans = [
    {"name": "Loan A", "balance": 15000, "rate": 5.5, "term": 120},
    {"name": "Loan B", "balance": 8000, "rate": 4.2, "term": 120},
    {"name": "Loan C", "balance": 5000, "rate": 6.0, "term": 120},
]

for i in range(3):
    with st.expander(f"Loan {i + 1}", expanded=(i == 0)):
        cols = st.columns(4)

        with cols[0]:
            loan_name = st.text_input(f"Name", value=default_loans[i]["name"], key=f"name_{i}")
        with cols[1]:
            balance = st.number_input("Balance ($)", value=default_loans[i]["balance"], min_value=0, key=f"balance_{i}")
        with cols[2]:
            rate = st.number_input("Interest Rate (%)", value=default_loans[i]["rate"], min_value=0.0, key=f"rate_{i}")
        with cols[3]:
            term = st.number_input("Term (months)", value=default_loans[i]["term"], min_value=1, max_value=360, key=f"term_{i}")

        loan_inputs.append({
            "loan_name": loan_name,
            "balance": balance,
            "interest_rate": rate,
            "term_months": term
        })

st.header("Step 2: Strategy Selection")

extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0, value=150)
strategy = st.selectbox("Repayment Strategy", options=["Avalanche"], index=0)

if st.button("Simulate Repayment"):
    st.success("Calculating your optimized repayment plan...")

    # Baseline calculation
    baseline_interest, baseline_months, _ = simulate_baseline(loan_inputs)

    # Strategy calculation
    strategy_loans = [loan.copy() for loan in loan_inputs]
    schedule_df = simulate_full_strategy(strategy_loans, extra_payment, strategy="avalanche")
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
    plot_loan_timeline_plotly(schedule_df)

    st.subheader("📉 Aggressive vs. Minimum Payment")
    plot_strategy_comparison_plotly(loan_inputs, schedule_df, extra_payment)

    # Optional CSV export (future)
    # st.download_button("Download Schedule CSV", schedule_df.to_csv(), file_name="loan_schedule.csv")
