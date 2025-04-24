import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Set page configuration to use wide layout with no sidebar
st.set_page_config(page_title="Student Loan Payoff Simulator", layout="wide")

# Title and Description
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
This tool helps you estimate your student loan repayment schedule based on your loan details. Enter your loan information below, and you will receive:
- Minimum monthly payment
- Total interest paid over the course of the loan
- A detailed amortization schedule
- A graph illustrating the impact of making extra payments
""")

# Loan input fields directly in the main content area
st.subheader("Enter Loan Details")
name = st.text_input("Name of Loan", value="Loan 1", help="Provide a name for your loan (e.g., 'Student Loan 1')")
balance = st.number_input("Loan Balance ($)", min_value=0, value=20000, help="Total amount owed on the loan.")
interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=6.54, help="Annual interest rate of your loan.")
loan_term_months = st.number_input("Loan Term (Months)", min_value=1, max_value=360, value=120, help="Loan term in months.")
extra_payment = st.number_input("Extra Payment ($)", min_value=0, value=0, help="Monthly extra payment towards your loan.")

# Function to calculate minimum payment
def calculate_min_payment(balance, rate, term_months):
    r = rate / 100 / 12  # Monthly interest rate
    n = term_months  # Loan term in months
    min_payment = balance * (r * (1 + r)**n) / ((1 + r)**n - 1)  # Standard loan formula
    return min_payment

# Function to calculate loan amortization and track months taken
def calculate_amortization(balance, rate, term_months, extra_payment=0):
    r = rate / 100 / 12  # Monthly interest rate
    min_payment = calculate_min_payment(balance, rate, term_months)
    total_payment = min_payment + extra_payment
    balance_remaining = balance
    months = []
    balances = []
    principal_paid = []
    interest_paid = []
    
    # Track the number of months to pay off the loan
    month_count = 0
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
            month_count = month
            break
    
    return pd.DataFrame({
        'Month': months,
        'Balance': balances,
        'Principal Paid': principal_paid,
        'Interest Paid': interest_paid
    }), total_payment, balance_remaining, month_count

# Function to calculate loan amortization without extra payments
def calculate_amortization_no_extra(balance, rate, term_months):
    return calculate_amortization(balance, rate, term_months, extra_payment=0)

# Progress Bar and Spinner for loading data
with st.spinner("Calculating your loan details..."):
    loan_data, total_payment, final_balance, months_taken = calculate_amortization(balance, interest_rate, loan_term_months, extra_payment)

    # Display the table for the loan with extra payments
    st.subheader(f"Loan Amortization Schedule for {name}")
    st.write(loan_data)

    # Display total payment and final balance
    st.markdown(f"### Total Payment: **${total_payment:,.2f}** per month")
    st.markdown(f"### Final Balance after {len(loan_data)} months: **${final_balance:,.2f}**")

    # Calculate amortization without extra payments for comparison
    loan_data_no_extra, _, _, months_taken_no_extra = calculate_amortization_no_extra(balance, interest_rate, loan_term_months)

    # Combine the two graphs into one plot using Plotly
    st.subheader("Loan Balance Over Time (With and Without Extra Payments)")
    
    # Create the Plotly figure
    fig = go.Figure()

    # Plot loan balance with extra payments (green line)
    fig.add_trace(go.Scatter(x=loan_data['Month'], y=loan_data['Balance'], mode='lines', name='Loan Balance with Extra Payments', line=dict(color='green', width=2)))
    
    # Plot loan balance without extra payments (blue line)
    fig.add_trace(go.Scatter(x=loan_data_no_extra['Month'], y=loan_data_no_extra['Balance'], mode='lines', name='Loan Balance without Extra Payments', line=dict(color='blue', dash='dash', width=2)))

    # Update layout
    fig.update_layout(
        title=f"{name} Loan Payoff Over Time",
        xaxis_title="Months",
        yaxis_title="Loan Balance ($)",
        template="plotly_dark",
        width=900,
        height=500,
        legend_title="Loan Comparison",
    )

    # Show the Plotly graph
    st.plotly_chart(fig)

    # Conclusion and guidance
    if extra_payment > 0:
        months_saved = months_taken_no_extra - months_taken
        total_interest_saved = loan_data_no_extra['Interest Paid'].sum() - loan_data['Interest Paid'].sum()

        # Format the numbers with commas and two decimal places for better readability
        months_saved_str = f"{months_saved} months" if months_saved > 0 else "no months"
        total_interest_saved_str = f"${total_interest_saved:,.2f}"

        st.markdown(f"""
        ### By making extra payments of **${extra_payment}** per month:
        - You would save **{months_saved_str}** and
        - Reduce the total interest paid by **{total_interest_saved_str}**!
        """)
    else:
        st.markdown("""
        ### Consider adding extra payments to pay off your loan faster and reduce the total interest you pay over time.
        Even small monthly contributions can make a significant difference in the long run.
        """)

# Footer with Link
st.markdown("---")
st.markdown("Created with ❤️ by [Your Name](https://yourwebsite.com)")
