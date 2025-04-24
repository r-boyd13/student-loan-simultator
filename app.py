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
balance = st.number_input("Loan Balance ($)", min_value=0, value=20000)
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
    
    # Display minimum payment and related calculations
    st.write(f"**Minimum Monthly Payment**: ${min_payment:.2f}")

    # User input for extra monthly payment
    extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0.0, value=0.0)
    
    # New monthly payment with extra payment
    new_payment = min_payment + extra_payment

    # Simulate loan payoff with new payment
    balance_remaining = balance
    months_remaining = 0
    total_interest_new = 0
    total_principal_new = 0
    while balance_remaining > 0:
        interest = balance_remaining * (interest_rate / 100 / 12)
        principal = new_payment - interest
        balance_remaining -= principal
        total_interest_new += interest
        total_principal_new += principal
        months_remaining += 1
        if balance_remaining < 0:  # Avoid going negative
            break

    # Recalculate the new payoff date
    current_date = datetime.today()
    new_payoff_date = current_date + relativedelta(months=months_remaining)
    new_payoff_date_str = new_payoff_date.strftime('%m-%d-%Y')

    # Display results with the new payment
    st.subheader("📊 Results with Extra Payment")
    st.write(f"**New Monthly Payment**: ${new_payment:.2f}")
    st.write(f"**New Loan Payoff Date**: {new_payoff_date_str}")
    st.write(f"**Total Payments**: ${new_payment * months_remaining:,.2f}")
    st.write(f"**Total Principal Paid**: ${total_principal_new:,.2f}")
    st.write(f"**Total Interest Paid**: ${total_interest_new:,.2f}")

    # Create amortization schedule for the new payment
    new_amortization_schedule = []
    balance_remaining = balance
    for month in range(months_remaining):
        interest = balance_remaining * (interest_rate / 100 / 12)
        principal = new_payment - interest
        balance_remaining -= principal
        new_amortization_schedule.append({
            "Month": month + 1,
            "Principal Payment": round(principal, 2),
            "Interest Payment": round(interest, 2),
            "Remaining Balance": round(balance_remaining, 2)
        })
    
    # Display amortization schedule as a table
    new_amortization_df = pd.DataFrame(new_amortization_schedule)
    st.subheader("📊 Amortization Schedule with Extra Payments")
    st.write(new_amortization_df)

    # Create interactive graph using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot loan balance decrease over time with both payment scenarios
    balance_history = simulate_downpayment_graph(balance, interest_rate, min_payment, loan_term_months)
    ax.plot(balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%) - Min Payment", color="royalblue", linewidth=3)
    
    # Plot the new payment balance
    new_balance_history = simulate_downpayment_graph(balance, interest_rate, new_payment, months_remaining)
    ax.plot(new_balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%) - Extra Payment", color="darkorange", linewidth=3)

    ax.set_title("Simulated Loan Downpayment Over Time (With Extra Payments)")
    ax.set_xlabel("Months")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
