import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You will receive the minimum monthly payment, total interest paid, total principal, and a full amortization schedule along with a graph showing the loan payoff over time.
""")

# Loan input fields
name = st.text_input("Name of Loan", value="Loan 1")
balance = st.number_input("Loan Balance ($)", min_value=0, value=10000)
interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.54)
loan_term_months = st.number_input("Loan Term (Months)", min_value=1, max_value=360, value=120)  # Default to 120 months (10 years)

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
    # Calculate the minimum payment and simulate payoff
    min_payment = calculate_min_payment(balance, interest_rate, loan_term_months)
    amortization_schedule, total_interest, total_principal = simulate_amortization_schedule(balance, interest_rate, min_payment, loan_term_months)
    balance_history = simulate_downpayment_graph(balance, interest_rate, min_payment, loan_term_months)

    # Calculate the estimated payoff date
    current_date = datetime.today()
    payoff_date = current_date + relativedelta(months=loan_term_months)
    payoff_date_str = payoff_date.strftime('%m-%d-%Y')

    # Display results
    st.write(f"**Minimum Monthly Payment**: ${min_payment:.2f}")
    st.write(f"**Loan Payoff Date**: {payoff_date_str}")
    st.write(f"**Total Payments**: ${min_payment * loan_term_months:,.2f}")
    st.write(f"**Total Principal Paid**: ${total_principal:,.2f}")
    st.write(f"**Total Interest Paid**: ${total_interest:,.2f}")

    # Display amortization schedule as a table
    amortization_df = pd.DataFrame(amortization_schedule)
    st.subheader("📊 Amortization Schedule")
    st.write(amortization_df)

    # Plot the simulated downpayment graph (loan balance over time)
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%)")

    # Add total remaining balance on the graph
    ax.set_title("Simulated Loan Downpayment Over Time")
    ax.set_xlabel("Months")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()

    # Customize the appearance of the graph
    ax.grid(True)

    # Add annotations for balance at 12-month intervals
    for month in range(0, loan_term_months + 1, 12):  # Every 12 months
        ax.annotate(f"${balance_history[month]:,.2f}", 
                    xy=(month, balance_history[month]), 
                    xytext=(month, balance_history[month] * 1.05), 
                    arrowprops=dict(arrowstyle="->", color="black"),
                    fontsize=10, color="white", ha="center", va="center")

    st.pyplot(fig)
