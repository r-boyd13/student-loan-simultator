import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Title and Description
st.set_page_config(page_title="Student Loan Payoff Simulator", layout="wide")
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
This tool helps you estimate your student loan repayment schedule based on your loan details. Enter your loan information below, and you will receive:
- Minimum monthly payment
- Total interest paid over the course of the loan
- A detailed amortization schedule
- A graph illustrating the impact of making extra payments
""")

# Loan input fields
st.sidebar.header("Enter Loan Details")
name = st.text_input("Name of Loan", value="Loan 1")
balance = st.number_input("Loan Balance ($)", min_value=0, value=20000)
interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.54)
loan_term_months = st.number_input("Loan Term (Months)", min_value=1, max_value=360, value=120)  # Default to 120 months (10 years)
extra_payment = st.number_input("Extra Payment ($)", min_value=0, value=0)  # Extra payment input

# Function to calculate minimum payment
def calculate_min_payment(balance, rate, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    n = term_months  # Loan term in months
    min_payment = balance * (r * (1 + r)**n) / ((1 + r)**n - 1)  # Standard loan formula
    return min_payment

# Function to calculate loan amortization
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
st.markdown(f"### Total Payment: **${total_payment:,.2f}** per month")
st.markdown(f"### Final Balance after {len(loan_data)} months: **${final_balance:,.2f}**")

# Impact of Extra Payment: Enhanced UX
if extra_payment > 0:
    st.subheader(f"Impact of Extra Payments of **${extra_payment}** per Month")
    extra_data, _, _ = calculate_amortization(balance, interest_rate, loan_term_months, extra_payment)
    st.write(extra_data)
    
    # Plot the balance with extra payments
    st.subheader("Loan Balance with Extra Payments")
    plt.figure(figsize=(10, 6))
    plt.plot(extra_data['Month'], extra_data['Balance'], label="Loan Balance with Extra Payments", color="green")
    plt.title(f"{name} Loan Payoff Over Time (With Extra Payments)", fontsize=16)
    plt.xlabel("Months", fontsize=12)
    plt.ylabel("Loan Balance ($)", fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

# Loan balance graph
st.subheader("Loan Balance Over Time")
plt.figure(figsize=(10, 6))
plt.plot(loan_data['Month'], loan_data['Balance'], label="Loan Balance", color="blue")
plt.title(f"{name} Loan Payoff Over Time", fontsize=16)
plt.xlabel("Months", fontsize=12)
plt.ylabel("Loan Balance ($)", fontsize=12)
plt.grid(True)
plt.tight_layout()
st.pyplot(plt)

# Conclusion and guidance
if extra_payment > 0:
    months_saved = len(loan_data) - len(extra_data)
    st.markdown(f"### By making extra payments of **${extra_payment}** per month, you would save **{months_saved} months** and reduce the total interest paid!")
else:
    st.markdown("""
    ### Consider adding extra payments to pay off your loan faster and reduce the total interest you pay over time.
    Even small monthly contributions can make a significant difference in the long run.
    """)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by [Your Name](https://yourwebsite.com)")
