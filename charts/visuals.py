import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Safe backend for Streamlit
import matplotlib.pyplot as plt
from utils.amortization import generate_amortization_schedule


def plot_loan_timeline_plotly(df, loans, layout_mode="desktop"):
    fig, ax = plt.subplots(figsize=(10, 6) if layout_mode == "desktop" else (6, 4))

    for loan in loans:
        loan_name = loan["loan_name"]
        balance = loan["balance"]
        rate = loan["interest_rate"]

        sub_df = df[df["Loan Name"] == loan_name]
        label = f"{loan_name} (${balance:,.0f} @ {rate}%)"
        ax.plot(sub_df["Month"], sub_df["Remaining Balance"], label=label)

    ax.set_title("Loan Payoff Timeline", fontsize=14 if layout_mode == "mobile" else 18)
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.grid(True)
    ax.legend(fontsize=8 if layout_mode == "mobile" else 12)
    plt.tight_layout()
    st.pyplot(fig)


def plot_strategy_comparison_plotly(original_loans, strategy_df, extra_payment, layout_mode="desktop"):
    fig, ax = plt.subplots(figsize=(10, 6) if layout_mode == "desktop" else (6, 4))

    for loan in original_loans:
        df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        label = f"{loan['loan_name']} (${loan['balance']:,.0f} @ {loan['interest_rate']}%) (Min Payment)"
        ax.plot(df["Month"], df["Remaining Balance"], linestyle="--", label=label)

    for loan_name in strategy_df["Loan Name"].unique():
        sub = strategy_df[strategy_df["Loan Name"] == loan_name]
        first_row = sub.iloc[0]
        label = f"{loan_name} (${first_row['Remaining Balance']:,.0f}) (Aggressive)"
        ax.plot(sub["Month"], sub["Remaining Balance"], label=label)

    ax.set_title("Aggressive vs. Minimum Payment", fontsize=14 if layout_mode == "mobile" else 18)
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.grid(True)
    ax.legend(fontsize=8 if layout_mode == "mobile" else 12)
    plt.tight_layout()
    st.pyplot(fig)
