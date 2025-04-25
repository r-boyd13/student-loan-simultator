import numpy as np
import pandas as pd

def calculate_minimum_payment(balance, annual_rate, term_months):
    r = annual_rate / 100 / 12
    if r == 0:
        return balance / term_months
    return balance * (r * (1 + r)**term_months) / ((1 + r)**term_months - 1)

def generate_amortization_schedule(loan_name, balance, annual_rate, term_months):
    monthly_payment = calculate_minimum_payment(balance, annual_rate, term_months)
    schedule = []
    remaining_balance = balance
    r = annual_rate / 100 / 12
    month = 1

    while remaining_balance > 0.01 and month <= term_months:
        interest = remaining_balance * r
        principal = monthly_payment - interest
        principal = min(principal, remaining_balance)
        interest = monthly_payment - principal
        remaining_balance -= principal

        schedule.append({
            "Loan Name": loan_name,
            "Month": month,
            "Payment": round(monthly_payment, 2),
            "Principal Paid": round(principal, 2),
            "Interest Paid": round(interest, 2),
            "Remaining Balance": round(remaining_balance, 2)
        })
        month += 1

    return pd.DataFrame(schedule)
