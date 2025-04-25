import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.amortization import generate_amortization_schedule
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend safe for Streamlit
import matplotlib.pyplot as plt

def plot_loan_timeline_plotly(df, loans, layout_mode="desktop"):
    fig = go.Figure()

    for loan in loans:
        loan_name = loan["loan_name"]
        balance = loan["balance"]
        rate = loan["interest_rate"]

        sub_df = df[df["Loan Name"] == loan_name]
        label = f"{loan_name} (${balance:,.0f} @ {rate}%)"

        fig.add_trace(go.Scatter(
            x=sub_df["Month"],
            y=sub_df["Remaining Balance"],
            mode='lines',
            name=label
        ))

    font_size = 12 if layout_mode == "mobile" else 16
    legend_size = 10 if layout_mode == "mobile" else 14
    margins = dict(l=20, r=20, t=40, b=40) if layout_mode == "mobile" else dict(l=40, r=40, t=60, b=40)

    fig.update_layout(
        title="Loan Payoff Timeline",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template="plotly_dark",
        font=dict(size=font_size),
        legend=dict(font=dict(size=legend_size)),
        margin=margins
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_strategy_comparison_plotly(original_loans, strategy_df, extra_payment, layout_mode="desktop"):
    fig = go.Figure()

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

    font_size = 12 if layout_mode == "mobile" else 16
    legend_size = 10 if layout_mode == "mobile" else 14
    margins = dict(l=20, r=20, t=40, b=40) if layout_mode == "mobile" else dict(l=40, r=40, t=60, b=40)

    fig.update_layout(
        title="Aggressive vs. Minimum Payment",
        xaxis_title="Month",
        yaxis_title="Remaining Balance ($)",
        template="plotly_dark",
        font=dict(size=font_size),
        legend=dict(font=dict(size=legend_size)),
        margin=margins
    )
    st.plotly_chart(fig, use_container_width=True)
