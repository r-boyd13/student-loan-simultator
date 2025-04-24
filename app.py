import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Title
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You will receive the minimum monthly payment, total interest paid, total principal, and a full amortization schedule along with a graph showing the loan payoff over time.
""")

# Loan input fields
name = st.text_input("Name of Loan", value="Loan 1")
balance = st.number_input("Loan Balance ($)", min_value=0, value=20000)
interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.54)
loan_term_months = st.number_input("Loan Term (Months)", min_value=1, max_value=360, value=120)  # Default to 120 months (10 years)
extra_payment = st.number_input("Extra Payment ($)", min_value=0, value=0)  # Extra payment input

# Calculate minimum payment (standard plan)
def calculate_min_payment(balance, rate, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    n = term_months  # Loan term in months
    min_payment = balance * (r * (1 + r)**n) / ((1 + r)**n - 1)  # Standard loan formula
    return min_payment

# Calculate loan amortization
def calculate_amortization(balance, rate, term_months, extra_payment=0):
    r = rate / 100 / 12  # Monthly interest rate
    min_payment = calculate_min_payment(balance, rate, term_months)
    total_payment = min_payment + extra_payment
    balance_remaining = balance
    months = []
    balances = []
    principal_paid = []
    interest_paid = []
    
    for month in range(1, term_months + 1):
        interest_for_month = balance_remaining * r
        principal_for_month = total_payment - interest_for_month
        balance_remaining -= principal_for_month
        if balance_remaining < 0:
            balance_remaining = 0
        
        months.append(month)
        balances.append(balance_remaining)
        principal_paid.append(principal_for_month)
        interest_paid.append(interest_for_month)
        
        if balance_remaining <= 0:
            break
            
    return pd.DataFrame({
        'Month': months,
        'Balance': balances,
        'Principal Paid': principal_paid,
        'Interest Paid': interest_paid
    }), total_payment, balance_remaining

# Calculate and display the amortization table
loan_data, total_payment, final_balance = calculate_amortization(balance, interest_rate, loan_term_months, extra_payment)

# Display the table
st.subheader(f"Loan Amortization Schedule for {name}")
st.write(loan_data)

# Display total payment and final balance
st.markdown(f"### Total Payment: ${total_payment:,.2f} per month")
st.markdown(f"### Final Balance after {len(loan_data)} months: ${final_balance:,.2f}")

# Plot the loan balance over time
st.subheader("Loan Balance Over Time")
plt.figure(figsize=(10, 6))
plt.plot(loan_data['Month'], loan_data['Balance'], label="Loan Balance", color="blue")
plt.title(f"{name} Loan Payoff Over Time")
plt.xlabel("Months")
plt.ylabel("Loan Balance ($)")
plt.grid(True)
plt.tight_layout()
st.pyplot(plt)

# Extra payment impact
if extra_payment > 0:
    st.subheader(f"Impact of Extra Payments of ${extra_payment} per Month")
    extra_data, _, _ = calculate_amortization(balance, interest_rate, loan_term_months, extra_payment)
    st.write(extra_data)
    
    # Plot the balance with extra payments
    st.subheader("Loan Balance with Extra Payments")
    plt.figure(figsize=(10, 6))
    plt.plot(extra_data['Month'], extra_data['Balance'], label="Loan Balance with Extra Payments", color="green")
    plt.title(f"{name} Loan Payoff Over Time (With Extra Payments)")
    plt.xlabel("Months")
    plt.ylabel("Loan Balance ($)")
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

# Conclusion and guidance
if extra_payment > 0:
    months_saved = len(loan_data) - len(extra_data)
    st.markdown(f"### You would save **{months_saved} months** and reduce the total interest paid by making an extra payment of ${extra_payment} per month!")
else:
    st.markdown("### Consider adding extra payments to pay off your loan faster and reduce interest.")
