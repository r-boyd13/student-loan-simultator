import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You will receive the minimum monthly payment, total interest paid, and a full amortization schedule along with a graph showing the loan payoff over time.
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

    for month in range(months):
        interest = balance * r  # Calculate monthly interest
        principal = min_payment - interest  # Subtract interest from payment to calculate principal
        balance = max(0, balance - principal)  # Reduce balance by principal
        total_interest += interest  # Track total interest paid
        schedule.append({
            "Month": month + 1,
            "Principal Payment": round(principal, 2),
            "Interest Payment": round(interest, 2),
            "Remaining Balance": round(balance, 2)
        })
    return schedule, total_interest

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
    amortization_schedule, total_interest = simulate_amortization_schedule(balance, interest_rate, min_payment, loan_term_months)
    balance_history = simulate_downpayment_graph(balance, interest_rate, min_payment, loan_term_months)

    # Display the minimum monthly payment and total interest
    st.write(f"**Your minimum monthly payment**: ${min_payment:.2f}")
    st.write(f"**The amount of interest paid over the course of the loan**: ${total_interest:,.2f}")

    # Display amortization schedule as a table
    amortization_df = pd.DataFrame(amortization_schedule)
    st.subheader("📊 Amortization Schedule")
    st.write(amortization_df)

    # Plot the simulated downpayment graph (loan balance over time)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(balance_history, label=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%)")
    ax.set_title("Simulated Loan Downpayment Over Time")
    ax.set_xlabel("Months")
    ax.set_ylabel("Remaining Balance ($)")
    ax.grid(True)
    ax.legend()
    
    st.pyplot(fig)
