import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Set page configuration to use wide layout with no sidebar
st.set_page_config(page_title="Student Loan Payoff Simulator", layout="centered")

# Title and Description
st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
This tool helps you estimate your student loan repayment schedule based on your loan details. Enter your loan information below, and you will receive:
- Minimum monthly payment
- Total interest paid over the course of the loan
- A detailed amortization schedule
- A graph illustrating the impact of making extra payments
""")

# Add an expandable section for explaining the logic behind the calculations
with st.expander("Click to Learn the Calculation Logic"):
    st.markdown("""
    The loan calculations are based on standard amortization formulas, which break down the repayment of your loan into fixed monthly payments of principal and interest.

    ### Key Components of the Calculation:
    
    1. **Minimum Monthly Payment Calculation**:
       The minimum monthly payment is calculated using the formula for an amortizing loan:
       
       \[
       M = P \times \frac{r(1 + r)^n}{(1 + r)^n - 1}
       \]
       - Where:
         - \( M \) is the monthly payment.
         - \( P \) is the loan principal (balance).
         - \( r \) is the monthly interest rate (annual interest rate divided by 12).
         - \( n \) is the number of payments (loan term in months).

    2. **Amortization Schedule**:
       Each month, a portion of your payment goes towards interest, and the remaining amount reduces the principal balance. The loan balance decreases over time as more of the payment is applied towards the principal.

    3. **Impact of Extra Payments**:
       When extra payments are made:
       - The **extra payment** is added to the principal reduction each month.
       - This reduces the balance faster, which means less interest is paid over time.
       - The **loan term** is shortened, and the payoff date is earlier than originally projected.

    4. **Estimated Payoff Date**:
       The payoff date is calculated by estimating when the balance will reach zero, considering the monthly payment and extra payments.

    5. **Calculating Total Interest Paid**:
       Total interest paid is calculated by summing up the interest portion of each monthly payment over the life of the loan.

    ### What This Tool Does:
    - **Loan Schedule**: It shows the breakdown of each month's principal and interest payments.
    - **Payoff Date**: It estimates when the loan will be fully paid off, considering the regular and extra payments.
    - **Visual Impact**: It plots how the loan balance decreases over time, showing the effect of extra payments on the loan term and total interest.
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

# Function to calculate estimated payoff date
def calculate_payoff_date(months_taken):
    start_date = datetime.today()
    payoff_date = start_date + relativedelta(months=months_taken)
    return payoff_date.strftime('%m-%d-%Y')

# Progress Bar and Spinner for loading data
with st.spinner("Calculating your loan details..."):
    loan_data, total_payment, final_balance, months_taken = calculate_amortization(balance, interest_rate, loan_term_months, extra_payment)

    # Display the estimated payoff date above the amortization schedule
    payoff_date = calculate_payoff_date(months_taken)
    st.markdown(f"### Your loan will be fully paid off on **{payoff_date}**.")

    # Display the key loan statistics
    st.markdown(f"### Minimum Monthly Payment: **${total_payment:,.2f}**")
    total_interest_paid = loan_data['Interest Paid'].sum()
    total_principal_paid = loan_data['Principal Paid'].sum()
    total_paid = total_principal_paid + total_interest_paid
    st.markdown(f"### Total Interest Paid: **${total_interest_paid:,.2f}**")
    st.markdown(f"### Total Principal Paid: **${total_principal_paid:,.2f}**")
    st.markdown(f"### Total Payments: **${total_paid:,.2f}**")

    # Display the table for the loan with extra payments
    st.subheader(f"Loan Amortization Schedule for {name}")
    st.write(loan_data)

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
        width=800,  # Adjusted width
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
