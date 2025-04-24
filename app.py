import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details below. You can add up to 10 loans and simulate your payments based on the standard 10-year repayment plan.
""")

# Number of loans the user wants to input
num_loans = st.number_input("How many loans do you have?", min_value=1, max_value=10, value=1)

# Initialize lists to store loan details
loan_names = []
loan_balances = []
interest_rates = []
min_payments = []
loan_terms = []

# Loop to create input fields for each loan
for i in range(num_loans):
    st.subheader(f"Loan {i + 1}")
    name = st.text_input(f"Name of Loan {i + 1}", key=f"name_{i}")
    balance = st.number_input(f"Balance for Loan {i + 1} ($)", min_value=0, value=10000, key=f"balance_{i}")
    interest_rate = st.number_input(f"Interest Rate for Loan {i + 1} (%)", min_value=0.0, value=5.0, key=f"rate_{i}")
    min_payment = st.number_input(f"Minimum Payment for Loan {i + 1} ($)", min_value=0, value=200, key=f"payment_{i}")
    loan_term = st.number_input(f"Loan Term for Loan {i + 1} (Years)", min_value=1, max_value=30, value=10, key=f"term_{i}")

    # Store loan details in lists
    loan_names.append(name)
    loan_balances.append(balance)
    interest_rates.append(interest_rate)
    min_payments.append(min_payment)
    loan_terms.append(loan_term)

# Calculate minimum payment (standard 10-year plan)
def calculate_min_payment(balance, rate, term_years=10):
    r = rate / 100 / 12
    n = term_years * 12
    if r == 0:
        return balance / n
    return balance * r * (1 + r)**n / ((1 + r)**n - 1)

# Simulate loan payoff over time
def simulate_payoff(balance, rate, min_payment, term_years=10):
    r = rate / 100 / 12
    months = term_years * 12
    balance_history = [balance]
    for month in range(months):
        interest = balance * r
        principal = min_payment - interest
        balance = max(0, balance - principal)
        balance_history.append(balance)
    return balance_history

# Run simulation when button is clicked
if st.button("Run Simulation"):
    # Simulate each loan payoff and display results
    for i in range(num_loans):
        balance = loan_balances[i]
        interest_rate = interest_rates[i]
        min_payment = min_payments[i]
        loan_term = loan_terms[i]

        # Calculate standard payment and simulate payoff
        min_payment_calc = calculate_min_payment(balance, interest_rate, loan_term)
        balance_history = simulate_payoff(balance, interest_rate, min_payment_calc, loan_term)
        
        # Plot loan balance over time
        fig, ax = plt.subplots()
        ax.plot(balance_history, label=f"Loan {i + 1}: {loan_names[i]}")
        ax.set_title(f"Payoff Timeline for {loan_names[i]}")
        ax.set_xlabel("Months")
        ax.set_ylabel("Remaining Balance ($)")
        ax.grid(True)
        ax.legend()

        st.pyplot(fig)
        st.write(f"Minimum monthly payment for {loan_names[i]}: ${min_payment_calc:.2f}")
