import streamlit as st

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

# Placeholder for showing results (will update after next steps)
st.write("Loan Details: ", loan_names, loan_balances, interest_rates, min_payments, loan_terms)
