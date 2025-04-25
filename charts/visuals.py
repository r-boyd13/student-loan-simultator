import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.amortization import generate_amortization_schedule

def plot_loan_timeline_plotly(df):
    fig = go.Figure()
    for loan_name in df["Loan Name"].unique():
        sub_df = df[df["Loan Name"] == loan_name]
        fig.add_trace(go.Scatter(
            x=sub_df["Month"],
            y=sub_df["Remaining Balance"],
            mode='lines',
            name=loan_name
        ))
    fig.update_layout(
        title="Loan Payoff Timeline",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_strategy_comparison_plotly(original_loans, strategy_df, extra_payment):
    fig = go.Figure()

    # Baseline: Dashed lines
    for loan in original_loans:
        df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        fig.add_trace(go.Scatter(
            x=df["Month"],
            y=df["Remaining Balance"],
            mode='lines',
            name=f"{loan['loan_name']} (Min Payment)",
            line=dict(dash='dash')
        ))

    # Strategy: Solid lines
    for loan_name in strategy_df["Loan Name"].unique():
        sub = strategy_df[strategy_df["Loan Name"] == loan_name]
        fig.add_trace(go.Scatter(
            x=sub["Month"],
            y=sub["Remaining Balance"],
            mode='lines',
            name=f"{loan_name} (Aggressive)"
        ))

fig.update_layout(
    title="Your Title",
    xaxis_title="Month",
    yaxis_title="Remaining Balance ($)",
    template="plotly_dark",  # optional
    font=dict(size=16),
    legend=dict(font=dict(size=14)),
    margin=dict(l=40, r=40, t=60, b=40)
)

    st.plotly_chart(fig, use_container_width=True)
