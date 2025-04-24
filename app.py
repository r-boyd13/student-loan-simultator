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

    # Display the minimum monthly payment and total interest
    st.write(f"**Your minimum monthly payment**: ${min_payment:.2f}")
    st.write(f"**The amount of interest paid over the course of the loan**: ${total_interest:,.2f}")
    st.write(f"**Total Principal Paid**: ${total_principal:,.2f}")
    st.write(f"**Total Payments**: ${min_payment * loan_term_months:,.2f}")

    # Display amortization schedule as a table
    amortization_df = pd.DataFrame(amortization_schedule)
    st.subheader("📊 Amortization Schedule")
    st.write(amortization_df)

    # Create interactive graph using Plotly
    fig = go.Figure()

    # Plot loan balance decrease over time
    fig.add_trace(go.Scatter(
        x=list(range(loan_term_months + 1)),  # X-axis for months
        y=balance_history,  # Y-axis for the loan balance over time
        mode='lines',
        name=f"Loan Payoff: {name} (${balance:,.2f} @ {interest_rate}%)",
        line=dict(color='royalblue', width=3)
    ))

    # Customize the layout for a sleek appearance
    fig.update_layout(
        title="Simulated Loan Downpayment Over Time",
        xaxis_title="Months",
        yaxis_title="Remaining Balance ($)",
        template="plotly_dark",
        hovermode="closest",
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    # Add balance tooltips at 6-month intervals
    for month in range(0, loan_term_months + 1, 6):  # Every 6 months
        fig.add_annotation(
            x=month,
            y=balance_history[month],
            text=f"${balance_history[month]:,.2f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor="white",
            ax=0,
            ay=-40,
            font=dict(size=12, color="white")
        )

    # Display graph
    st.plotly_chart(fig)
