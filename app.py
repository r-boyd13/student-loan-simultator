import streamlit as st
import pandas as pd
from utils.amortization import calculate_minimum_payment, generate_amortization_schedule
from utils.strategies import simulate_full_strategy
from charts.visuals import plot_loan_timeline, plot_strategy_comparison

st.set_page_config(page_title="Student Loan Simulator", layout="wide")
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your student loan information below. You can simulate multiple loans, see a full amortization breakdown, and compare repayment strategies like Avalanche (highest interest first).

This tool will show:
- Your loan balances over time
- When each loan is paid off
- Total interest saved by paying extra monthly
""")

# Step 1: Collect loan input
tabs = st.tabs(["Loan Inputs", "Repayment Settings", "Results"])

with tabs[0]:
    st.subheader("Enter Your Loans")
    loan_data = []

    col1, col2, col3 = st.columns(3)
    with col1:
        loan_names = [st.text_input(f"Loan {i+1} Name", f"Loan {chr(65+i)}") for i in range(3)]
    with col2:
        balances = [st.number_input(f"Balance {i+1} ($)", min_value=0.0, value=5000.0, step=500.0) for i in range(3)]
    with col3:
        rates = [st.number_input(f"Interest Rate {i+1} (%)", min_value=0.0, value=5.0, step=0.1) for i in range(3)]

    terms = [120] * 3  # 10-year default term

    loans = [
        {"loan_name": loan_names[i], "balance": balances[i], "interest_rate": rates[i], "term_months": terms[i]}
        for i in range(3) if balances[i] > 0
    ]

with tabs[1]:
    st.subheader("Repayment Strategy")
    strategy = st.selectbox("Choose a strategy:", ["Avalanche"], index=0)
    extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0.0, value=150.0, step=25.0)

with tabs[2]:
    if st.button("Simulate Repayment"):
        # Run strategy simulation
        tracked_loans = simulate_full_strategy(loans, extra_payment, strategy="avalanche")

        # Display loan timeline chart
        st.subheader("📈 Loan Payoff Timeline")
        plot_loan_timeline(tracked_loans)

        # Strategy comparison
        st.subheader("📊 Minimum Payment vs. Aggressive Strategy")
        plot_strategy_comparison(loans, extra_payment)

        # Summary results
        st.subheader("📊 Repayment Summary")
        # Use amortization to compare baseline vs accelerated
        total_interest_standard = sum(generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )["Interest Paid"].sum() for loan in loans)

        accelerated_df = pd.concat(tracked_loans.values())
        total_interest_accelerated = accelerated_df["Remaining Balance"].diff(periods=-1).fillna(0).sum()

        payoff_months = accelerated_df["Month"].max()
        st.markdown(f"**Interest Saved:** ${total_interest_standard - total_interest_accelerated:,.2f}")
        st.markdown(f"**Months to Payoff:** {int(payoff_months)}")
        st.markdown(f"**Strategy Used:** {strategy}")

st.markdown("---")
st.caption("Built by Ryan | [GitHub Repo](https://github.com/r-boyd13/student-loan-simulator)")
