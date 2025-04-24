import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You will receive the minimum monthly payment, total interest paid, total principal, and a full amortization schedule along with a graph showing the loan payoff over time.
""")

# Default to 1 loan and allow adding more (up to 5)
num_loans = st.number_input("How many loans do you have?", min_value=1, max_value=5, value=1)

# Initialize lists to store loan details
loan_names = []
loan_balances = []
interest_rates = []
loan_terms_months = []  # Loan term in months

# Loop to create input fields for each loan
for i in range(num_loans):
    with st.expander(f"Loan {i + 1}", expanded=True):
        name = st.text_input(f"Name of Loan {i + 1}", key=f"name_{i}")
        balance = st.number_input(f"Loan Balance for Loan {i + 1} ($)", min_value=0, value=10000, key=f"balance_{i}")
        interest_rate = st.number_input(f"Interest Rate for Loan {i + 1} (%)", min_value=0.0, value=6.54, key=f"rate_{i}")  # Default to 6.54%
        loan_term_months = st.number_input(f"Loan Term for Loan {i + 1} (Months)", min_value=1, max_value=360, value=120, key=f"term_{i}")  # Default 120 months (10 years)

        # Store loan details in lists
        loan_names.append(name)
        loan_balances.append(balance)
        interest_rates.append(interest_rate)
        loan_terms_months.append(loan_term_months)

# Calculate minimum payment (standard plan)
def calculate_min_payment(balance, rate, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    n = term_months
    if r == 0:
        return balance / n
    return balance * r * (1 + r)**n / ((1 + r)**n - 1)

# Simulate loan payoff over time (calculate monthly breakdown)
def simulate_amortization_schedule(balance, rate, min_payment, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    months = term_months
    schedule = []
    total_interest = 0
    total_principal = 0

    for month in range(months):
        interest = balance * r  # Calculate monthly interest
        principal = min_payment - interest  # Subtract interest from payment to calculate principal
        balance = max(0, balance - principal)  # Reduce balance by principal
        total_interest += interest  # Track total interest paid
        total_principal += principal  # Track total principal paid
        schedule.append({
            "Month": month + 1,
            "Principal Payment": round(principal, 2),
            "Interest Payment": round(interest, 2),
            "Remaining Balance": round(balance, 2)
        })
    return schedule, total_interest, total_principal

# Simulate loan payoff over time for graph (show loan balance decrease)
def simulate_downpayment_graph(balance, rate, min_payment, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    months = term_months
    balance_history = [balance]

    for month in range(months):
        interest = balance * r  # Calculate monthly interest
        principal = min_payment - interest  # Subtract interest from payment to calculate principal
        balance = max(0, balance - principal)  # Reduce balance by principal
        balance_history.append(balance)
    
    return balance_history

# Run simulation when button is clicked
if st.button("Run Simulation"):
    # Initialize lists for all balance histories
    all_balance_histories = []
    combined_balance_history = []  # Initialize as empty list for combining histories

    # Simulate each loan payoff and calculate total combined balance
    for i in range(num_loans):
        balance = loan_balances[i]
        interest_rate = interest_rates[i]
        loan_term_months = loan_terms_months[i]

        # Calculate the standard payment and simulate payoff
        min_payment = calculate_min_payment(balance, interest_rate, loan_term_months)
        balance_history, total_interest, total_principal = simulate_amortization_schedule(balance, interest_rate, min_payment, loan_term_months)
        all_balance_histories.append(balance_history)

        # Initialize combined_balance_history to match the first loan's history
        if len(combined_balance_history) == 0:
            combined_balance_history = balance_history[:]

        # Add this loan's balance history to the combined balance
        if len(balance_history) == len(combined_balance_history):
            combined_balance_history = [x + y for x, y in zip(combined_balance_history, balance_history)]
        else:
            # Handle case where the history lengths differ (by extending the shorter list with zeros)
            if len(balance_history) > len(combined_balance_history):
                combined_balance_history.extend([0] * (len(balance_history) - len(combined_balance_history)))
            else:
                balance_history.extend([0] * (len(combined_balance_history) - len(balance_history)))
            combined_balance_history = [x + y for x, y in zip(combined_balance_history, balance_history)]

        # Display results for each loan
        st.subheader(f"Loan {i + 1} Results")
        st.write(f"**Loan Name**: {loan_names[i]}")
        st.write(f"**Your minimum monthly payment**: ${min_payment:.2f}")
        st.write(f"**Total interest paid for {loan_names[i]}**: ${total_interest:,.2f}")
        st.write(f"**Total principal paid for {loan_names[i]}**: ${total_principal:,.2f}")
        st.write(f"**Total payments for {loan_names[i]}**: ${min_payment * loan_term_months:,.2f}")

        # Display amortization schedule as a table for each loan
        amortization_df = pd.DataFrame(balance_history, columns=["Month", "Remaining Balance"])
        st.write(amortization_df)

    # Plot all loan balances on the same graph
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each loan balance over time
    for i in range(num_loans):
        ax.plot(all_balance_histories[i], label=f"{loan_names[i]} (${loan_balances[i]:,.2f} @ {interest_rates[i]}%)")

    # Plot combined balance
    ax.plot(combined_balance_history, label="Combined Balance", color="black", linestyle="--", linewidth=2)

    ax.set_title("Loan Balances with Proper 10-Year Amortization")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()

    st.pyplot(fig)
