import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You can add up to 5 loans and simulate your payments based on the standard repayment plan (minimum payment over the term of the loan).
""")

# Default to 1 loan and allow adding more (up to 5)
num_loans = st.number_input("How many loans do you have?", min_value=1, max_value=5, value=1)

# Initialize lists to store loan details
loan_names = []
loan_balances = []
interest_rates = []
loan_terms_months = []  # Loan term in months

# Loop to create input fields for each loan
for i in range(num_loans):
    st.subheader(f"Loan {i + 1}")
    name = st.text_input(f"Name of Loan {i + 1}", key=f"name_{i}")
    balance = st.number_input(f"Balance for Loan {i + 1} ($)", min_value=0, value=10000, key=f"balance_{i}")
    interest_rate = st.number_input(f"Interest Rate for Loan {i + 1} (%)", min_value=0.0, value=6.54, key=f"rate_{i}")  # Default to 6.54%
    loan_term_months = st.number_input(f"Loan Term for Loan {i + 1} (Months)", min_value=1, max_value=360, value=120, key=f"term_{i}")  # Default 120 months (10 years)

    # Store loan details in lists
    loan_names.append(name)
    loan_balances.append(balance)
    interest_rates.append(interest_rate)
    loan_terms_months.append(loan_term_months)

# Calculate minimum payment (standard plan)
def calculate_min_payment(balance, rate, term_months):
    r = rate / 100 / 12
    n = term_months
    if r == 0:
        return balance / n
    return balance * r * (1 + r)**n / ((1 + r)**n - 1)

# Simulate loan payoff over time
def simulate_payoff(balance, rate, min_payment, term_months):
    r = rate / 100 / 12
    months = term_months
    balance_history = [balance]
    total_interest = 0
    for month in range(months):
        interest = balance * r
        principal = min_payment - interest
        balance = max(0, balance - principal)
        balance_history.append(balance)
        total_interest += interest
    return balance_history, total_interest

# Run simulation when button is clicked
if st.button("Run Simulation"):
    # Initialize lists for all balance histories
    all_balance_histories = []
    combined_balance_history = [0]  # Start with a 0 balance for combined

    # Simulate each loan payoff and calculate total combined balance
    for i in range(num_loans):
        balance = loan_balances[i]
        interest_rate = interest_rates[i]
        loan_term_months = loan_terms_months[i]

        # Calculate the standard payment and simulate payoff
        min_payment = calculate_min_payment(balance, interest_rate, loan_term_months)
        balance_history, _ = simulate_payoff(balance, interest_rate, min_payment, loan_term_months)
        
        # Append individual loan's balance history to combined balance
        all_balance_histories.append(balance_history)

        # Add to combined balance history
        combined_balance_history = [x + y for x, y in zip(combined_balance_history, balance_history)]

    # Plot all loan balances on the same graph
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each loan balance over time
    for i in range(num_loans):
        ax.plot(all_balance_histories[i], label=f"{loan_names[i]} (${loan_balances[i]:,.2f} @ {interest_rates[i]}%)")

    # Plot combined balance
    ax.plot(combined_balance_history, label="Combined Balance", color="black", linestyle="--", linewidth=2)

    ax.set_title("Loan Balances with Proper 10-Year Amortization")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()

    # Add data labels with loan name and interest rate
    for i in range(num_loans):
        ax.text(0, all_balance_histories[i][0], f"{loan_names[i]} ({interest_rates[i]}%)", fontsize=9, ha="center")

    ax.grid(True)
    st.pyplot(fig)

    # Show total combined balance at the final point
    st.write(f"Total combined balance of all loans at the end of the loan term: ${combined_balance_history[-1]:,.2f}")
