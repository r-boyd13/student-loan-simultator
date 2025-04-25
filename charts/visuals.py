def plot_strategy_comparison(original_loans, strategy_df, extra_payment):
    from utils.amortization import generate_amortization_schedule

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot baseline
    for loan in original_loans:
        df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        ax.plot(df["Month"], df["Remaining Balance"], linestyle='--', label=f"{loan['loan_name']} (Min Payment)")

    # Plot aggressive strategy results
    for loan_name in strategy_df["Loan Name"].unique():
        sub = strategy_df[strategy_df["Loan Name"] == loan_name]
        ax.plot(sub["Month"], sub["Remaining Balance"], label=f"{loan_name} (Aggressive)")

    ax.set_title("Aggressive vs. Minimum Payment")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
