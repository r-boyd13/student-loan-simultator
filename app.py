import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You can add up to 5 loans and simulate your payments based on the standard repayment plan (minimum payment over the term of the loan).
""")

# Limit to 5 loans
num_loans = 5

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
    interest_history = []  # Track interest at each month
    for month in range(months):
        interest = balance * r
        principal = min_payment - interest
        balance = max(0, balance - principal)
        balance_history.append(balance)
        total_interest += interest
        interest_history.append(total_interest)  # Track cumulative interest

    return balance_history, total_interest, interest_history

# Run simulation when button is clicked
if st.button("Run Simulation"):
    # Store results for all loans
    loan_results = []

    # Simulate each loan payoff and display results
    for i in range(num_loans):
        balance = loan_balances[i]
        interest_rate = interest_rates[i]
        loan_term_months = loan_terms_months[i]

        # Calculate the standard payment and simulate payoff
        min_payment = calculate_min_payment(balance, interest_rate, loan_term_months)
        balance_history, total_interest, interest_history = simulate_payoff(balance, interest_rate, min_payment, loan_term_months)

        # Store results
        loan_results.append({
            "name": loan_names[i],
            "balance": loan_balances[i],
            "interest_rate": interest_rate,
            "total_interest": total_interest,
            "interest_history": interest_history
        })

    # Sort loans by total interest (highest to lowest)
    loan_results.sort(key=lambda x: x["total_interest"], reverse=True)

    # Plot loan balances
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot each loan balance over time
    for result in loan_results:
        ax.plot(result["interest_history"], label=f"{result['name']} (${result['balance']:.2f} @ {result['interest_rate']}%)")
    
    # Plot combined balance (if necessary)
    ax.set_title("Loan Balances with Proper 10-Year Amortization")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # Show sorted loan interest
    for result in loan_results:
        st.write(f"**{result['name']}** (Interest Rate: {result['interest_rate']}%)")
        st.write(f"Total Interest: ${result['total_interest']:,.2f}")

        # Breakdown of interest accumulated every 18 months
        st.write("Interest Breakdown Every 18 Months:")
        for i in range(0, len(result['interest_history']), 18):
            month = i + 18
            st.write(f"Month {month}: ${result['interest_history'][i]:,.2f}")
