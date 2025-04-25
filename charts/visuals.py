import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.amortization import generate_amortization_schedule

def plot_loan_timeline_plotly(df):
    fig = go.Figure()

    # Group the dataframe by loan name and get first known balance + interest if available
    grouped = df.groupby("Loan Name")

    for loan_name, sub_df in grouped:
        initial_balance = sub_df["Remaining Balance"].iloc[0]
        
        # Try to extract interest rate from loan_name if embedded
        # If not, label with just name + balance
        if "@" in loan_name:
            label = f"{loan_name} (${initial_balance:,.0f})"
        else:
            # Default format if rate isn't embedded
            label = f"{loan_name} (${initial_balance:,.0f})"

        fig.add_trace(go.Scatter(
            x=sub_df["Month"],
            y=sub_df["Remaining Balance"],
            mode='lines',
            name=label
        ))

    fig.update_layout(
        title="Loan Payoff Timeline",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template="plotly_dark",
        font=dict(size=16),
        legend=dict(font=dict(size=14)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_strategy_comparison_plotly(original_loans, strategy_df, extra_payment):
    fig = go.Figure()

    # Baseline (Dashed)
    for loan in original_loans:
        df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        label = f"{loan['loan_name']} (${loan['balance']:,.0f} @ {loan['interest_rate']}%) (Min Payment)"
        fig.add_trace(go.Scatter(
            x=df["Month"],
            y=df["Remaining Balance"],
            mode='lines',
            name=label,
            line=dict(dash='dash')
        ))

    # Strategy (Solid)
    for loan_name in strategy_df["Loan Name"].unique():
        sub = strategy_df[strategy_df["Loan Name"] == loan_name]
        first_row = sub.iloc[0]
        label = f"{loan_name} (${first_row['Remaining Balance']:,.0f}) (Aggressive)"
        fig.add_trace(go.Scatter(
            x=sub["Month"],
            y=sub["Remaining Balance"],
            mode='lines',
            name=label
        ))

    fig.update_layout(
        title="Aggressive vs. Minimum Payment",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template="plotly_dark",
        font=dict(size=16),
        legend=dict(font=dict(size=14)),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
