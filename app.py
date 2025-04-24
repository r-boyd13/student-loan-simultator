%%writefile requirements.txt
streamlit
matplotlib
numpy

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("🎓 Student Loan Payoff Simulator")

st.markdown("""
Enter your loan details and payment strategy below. This app will show:
- A projected payoff timeline
- Interest paid with your strategy vs minimum payments
- How much interest you could save 💰
""")

# Loan inputs
balance = st.number_input("Loan Balance ($)", value=10000)
interest_rate = st.number_input("Interest Rate (%)", value=5.00)
monthly_payment = st.number_input("Monthly Payment ($)", value=400)

# Minimum payment calculation
def calculate_min_payment(balance, rate, term_years=10):
    r = rate / 100 / 12
    n = term_years * 12
    if r == 0:
        return balance / n
    return balance * r * (1 + r)**n / ((1 + r)**n - 1)

# Simulation
def simulate_payoff(balance, rate, monthly_pay):
    r = rate / 100 / 12
    months = 0
    total_interest = 0
    balances = [balance]
    
    while balance > 0 and months < 600:  # Limit to 50 years to prevent runaway
        interest = balance * r
        principal = monthly_pay - interest
        if principal <= 0:
            break  # Infinite loop protection
        balance = max(0, balance - principal)
        total_interest += interest
        balances.append(balance)
        months += 1
    
    return months, total_interest, balances

# Run when button is clicked
if st.button("Run Simulation"):
    min_payment = calculate_min_payment(balance, interest_rate)
    months_custom, interest_custom, bal_custom = simulate_payoff(balance, interest_rate, monthly_payment)
    months_min, interest_min, _ = simulate_payoff(balance, interest_rate, min_payment)

    st.subheader("📊 Results")
    st.write(f"With your payment of ${monthly_payment:.2f}, your loan will be paid off in **{months_custom} months**.")
    st.write(f"Total interest paid: **${interest_custom:,.2f}**")
    st.write(f"If you paid the minimum (${min_payment:.2f}), you'd pay **${interest_min:,.2f}** in interest.")
    st.success(f"You'd save **${interest_min - interest_custom:,.2f}** in interest by paying more!")

    # Plot chart
    fig, ax = plt.subplots()
    ax.plot(bal_custom, label="Loan Balance")
    ax.set_title("Payoff Timeline")
    ax.set_xlabel("Month")
    ax.set_ylabel("Balance ($)")
    ax.grid(True)
    st.pyplot(fig)
