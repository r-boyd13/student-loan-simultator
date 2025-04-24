import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Set page configuration
st.set_page_config(page_title="Student Loan Payoff Simulator", layout="centered")

# Title and Description
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
This tool helps you estimate your student loan repayment schedule based on your loan details. Enter your loan information below, and you will receive:
- Estimated Monthly Payment
- Total Interest Paid
- Total Payments
- Impact of Extra Payments
- Amortization Schedule
- Loan Balance Over Time Graph
""")

# Input Fields
st.subheader("Enter Loan Details")
loan_balance = st.number_input("Loan Balance ($)", min_value=0, value=30000)
interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.8)
loan_term_years = st.number_input("Loan Term (Years)", min_value=1, max_value=30, value=10)
extra_monthly_payment = st.number_input("Extra Monthly Payment ($)", min_value=0, value=0)

# Calculate Monthly Payment
def calculate_monthly_payment(principal, rate, term_years):
    r = rate / 100 / 12
    n = term_years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)

# Calculate Amortization Schedule
def calculate_amortization_schedule(principal, rate, term_years, extra_payment):
    r = rate / 100 / 12
    n = term_years * 12
    monthly_payment = calculate_monthly_payment(principal, rate, term_years)
    total_payment = monthly_payment + extra_payment
    balance_remaining = principal
    months = []
    balances = []
    principal_paid = []
    interest_paid = []
    
    for month in range(1, n + 1):
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
    })

# Calculate Payoff Date
def calculate_payoff_date(months_taken):
    start_date = datetime.today()
    payoff_date = start_date + relativedelta(months=months_taken)
    return payoff_date.strftime('%m-%d-%Y')

# Calculate and Display Results
with st.spinner("Calculating your loan details..."):
    amortization_schedule = calculate_amortization_schedule(loan_balance, interest_rate, loan_term_years, extra_monthly_payment)
    total_interest_paid = amortization_schedule['Interest Paid'].sum()
    total_paid = amortization_schedule['Principal Paid'].sum() + total_interest_paid
    months_taken = len(amortization_schedule)
    payoff_date = calculate_payoff_date(months_taken)
    
    # Display Results
    st.markdown(f"### Your loan will be fully paid off on **{payoff_date}**.")
    st.markdown(f"### Estimated Monthly Payment: **${total_paid / months_taken:,.2f}**")
    st.markdown(f"### Total Interest Paid: **${total_interest_paid:,.2f}**")
    st.markdown(f"### Total Payments: **${total_paid:,.2f}**")
    
    # Display Amortization Schedule
    st.subheader("Amortization Schedule")
    st.write(amortization_schedule)

    # Plot Loan Balance Over Time
    st.subheader("Loan Balance Over Time")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=amortization_schedule['Month'], y=amortization_schedule['Balance'], mode='lines', name='Loan Balance'))
    fig.update_layout(title='Loan Balance Over Time', xaxis_title='Months', yaxis_title='Loan Balance ($)', template='plotly_dark')
    st.plotly_chart(fig)

    # Impact of Extra Payments
    if extra_monthly_payment > 0:
        st.markdown(f"### By making extra payments of **${extra_monthly_payment}** per month:")
        st.markdown(f"- You would save **{loan_term_years * 12 - months_taken} months**")
        st.markdown(f"- Reduce the total interest paid by **${total_interest_paid:,.2f}**")
