import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Title
st.title("🎓 Student Loan Payoff Simulator")

# Markdown instructions
st.markdown("""
Enter your loan details below. You will receive the minimum monthly payment, total interest paid, total principal, and a full amortization schedule along with a graph showing the loan payoff over time.
""")

# Use Streamlit session state to store values and prevent reloading
if 'min_payment' not in st.session_state:
    st.session_state.min_payment = 0
    st.session_state.balance_history = []
    st.session_state.amortization_schedule = []
    st.session_state.total_interest = 0
    st.session_state.total_principal = 0

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

# Form for dynamic input and updates
with st.form(key='loan_form'):
    extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0.0, value=0.0)
    submit_button = st.form_submit_button("Calculate Payments")

if submit_button:
    # Calculate the minimum payment and simulate payoff
    min_payment = calculate_min_payment(balance, interest_rate, loan_term_months)
    st.session_state.min_payment = min_payment  # Store in session state

    # Calculate amortization schedule and total payments
    amortization_schedule, total_interest, total_principal = simulate_amortization_schedule(balance, interest_rate, min_payment, loan_term_months)
    balance_history = simulate_downpayment_graph(balance, interest_rate, min_payment, loan_term_months)

    # Store amortization data in session state
    st.session_state.amortization_schedule = amortization_schedule
    st.session_state.total_interest = total_interest
    st.session_state.total_principal = total_principal
    st.session_state.balance_history = balance_history

    # Calculate the estimated payoff date
    current_date = datetime.today()
    payoff_date = current_date + relativedelta(months=loan_term_months)
    payoff_date_str = payoff_date.strftime('%m-%d-%Y')

    # Display results for the minimum payment
    st.write(f"**Minimum Monthly Payment**: ${min_payment:.2f}")
    st.write(f"**Loan Payoff Date**: {payoff_date_str}")
    st.write(f"**Total Payments**: ${min_payment * loan_term_months:,.2f}")
    st.write(f"**Total Principal Paid**: ${total_principal:,.2f}")
    st.write(f"**Total Interest Paid**: ${total_interest:,.2f}")

    # Display amortization schedule as a table
    amortization_df = pd.DataFrame(amortization_schedule)
    st.subheader("📊 Amortization Schedule")
    st.write(amortization_df)

    # Recalculate if extra payment is added
    new_payment = min_payment + extra_payment
    new_amortization_schedule, new_total_interest, new_total_principal = simulate_amortization_schedule(balance, interest_rate, new_payment, loan_term_months)
    new_balance_history = simulate_downpayment_graph(balance, interest_rate, new_payment, loan_term_months)

    # New payoff date based on increased payment
    new_payoff_date = current_date + relativedelta(months=len(new_balance_history) - 1)
    new_payoff_date_str = new_payoff_date.strftime('%m-%d-%Y')

    # Display results with the new payment
    st.subheader("📊 Results with Extra Payment")
    st.write(f"**New Monthly Payment**: ${new_payment:.2f}")
    st.write(f"**New Loan Payoff Date**: {new_payoff_date_str}")
    st.write(f"**Total Payments**: ${new_payment * len(new_balance_history):,.2f}")
    st.write(f"**Total Principal Paid**: ${new_total_principal:,.2f}")
    st.write(f"**Total Interest Paid**: ${new_total_interest:,.2f}")

    # Display amortization schedule as a table for the increased payment
    new_amortization_df = pd.DataFrame(new_amortization_schedule)
    st.subheader("📊 Amortization Schedule with Extra Payments")
    st.write(new_amortization_df)

    # Create interactive graph using Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot loan balance decrease over time with both payment scenarios
    ax.plot(balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%) - Min Payment", color="royalblue", linewidth=3)
    ax.plot(new_balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%) - Extra Payment", color="darkorange", linewidth=3)

    ax.set_title("Simulated Loan Downpayment Over Time (With Extra Payments)")
    ax.set_xlabel("Months")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)
