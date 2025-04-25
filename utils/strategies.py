def simulate_full_strategy(loans, extra_payment, strategy="avalanche"):
    if strategy == "avalanche":
        loans = sorted(loans, key=lambda x: -x["interest_rate"])
    elif strategy == "snowball":
        loans = sorted(loans, key=lambda x: x["balance"])

    history = []
    balances = [loan["balance"] for loan in loans]
    rates = [loan["interest_rate"] / 100 / 12 for loan in loans]
    terms = [loan["term_months"] for loan in loans]
    min_payments = [calculate_minimum_payment(b, r * 12 * 100, t)
                    for b, r, t in zip(balances, rates, terms)]
    month = 1

    while any(b > 0.01 for b in balances):
        # Choose the correct loan to target based on strategy
        target_idx = None
        if strategy == "avalanche":
            target_idx = max(
                [i for i, b in enumerate(balances) if b > 0.01],
                key=lambda i: rates[i]
            )
        elif strategy == "snowball":
            target_idx = min(
                [i for i, b in enumerate(balances) if b > 0.01],
                key=lambda i: balances[i]
            )

        for i in range(len(loans)):
            if balances[i] <= 0.01:
                continue

            interest = balances[i] * rates[i]
            payment = min_payments[i] + (extra_payment if i == target_idx else 0)
            principal = min(payment - interest, balances[i])
            balances[i] -= principal
            history.append({
                "Loan Name": loans[i]["loan_name"],
                "Month": month,
                "Payment": round(payment, 2),
                "Principal Paid": round(principal, 2),
                "Interest Paid": round(interest, 2),
                "Remaining Balance": round(balances[i], 2)
            })
        month += 1

    return pd.DataFrame(history)
