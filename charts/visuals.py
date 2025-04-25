import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def plot_loan_timeline(df):
    grouped = df.groupby(["Loan Name", "Month"])["Remaining Balance"].max().reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    for loan_name in grouped["Loan Name"].unique():
        sub_df = grouped[grouped["Loan Name"] == loan_name]
        ax.plot(sub_df["Month"], sub_df["Remaining Balance"], label=loan_name)
    ax.set_title("Loan Payoff Timeline (All Loans)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

def plot_strategy_comparison(original_loans, strategy_loans, extra_payment):
    from utils.amortization import generate_amortization_schedule

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot baseline
    for loan in original_loans:
        df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        ax.plot(df["Month"], df["Remaining Balance"], linestyle='--', label=f"{loan['loan_name']} (Min Payment)")

    # Plot strategy
    df = pd.concat(strategy_loans)
    for loan_name in df["Loan Name"].unique():
        sub = df[df["Loan Name"] == loan_name]
        ax.plot(sub["Month"], sub["Remaining Balance"], label=f"{loan_name} (Aggressive)")

    ax.set_title("Aggressive vs. Minimum Payment")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
