import streamlit as st
st.set_page_config(page_title="Student Loan Simulator", layout="wide")  # MUST be first

import pandas as pd
import matplotlib.pyplot as plt
from streamlit_js_eval import streamlit_js_eval
from utils.amortization import calculate_minimum_payment, generate_amortization_schedule
from utils.strategies import simulate_baseline, simulate_full_strategy
import io
from fpdf import FPDF

# --- Handle rerun flag immediately ---
if st.session_state.get("simulate_now") and st.session_state.get("triggered_rerun") is None:
    st.session_state.triggered_rerun = True
    st.rerun()

# Detect browser width and set layout mode
screen_width = streamlit_js_eval(js_expressions="screen.width", key="screen_width")
layout_mode = "mobile" if screen_width and screen_width < 700 else "desktop"

# Track strategy and simulation trigger
if "strategy" not in st.session_state:
    st.session_state.strategy = "Avalanche"
if "simulate_now" not in st.session_state:
    st.session_state.simulate_now = False

st.title("🎓 Student Loan Payoff Simulator")
st.markdown("Simulate your loan repayment plan, see how extra payments make a difference, and visualize your path to debt freedom.")

st.header("Step 1: Enter Your Loan Details")

# Expand/Collapse all loan fields
if "loan_expanded" not in st.session_state:
    st.session_state.loan_expanded = True

col_expand, col_collapse = st.columns([1, 1])
with col_expand:
    if st.button("🔼 Expand All Loan Fields"):
        st.session_state.loan_expanded = True
with col_collapse:
    if st.button("🔽 Collapse All Loan Fields"):
        st.session_state.loan_expanded = False

num_loans = st.number_input("How many loans do you want to enter?", min_value=1, max_value=10, value=3)
loan_inputs = []

for i in range(num_loans):
    with st.expander(f"Loan {i + 1}", expanded=st.session_state.loan_expanded):
        cols = [st.container() for _ in range(4)] if layout_mode == "mobile" else st.columns(4)
        with cols[0]:
            loan_name = st.text_input(f"Loan Name {i}", value=f"Loan {chr(65+i)}", key=f"name_{i}")
        with cols[1]:
            balance = st.number_input(f"Balance {i}", value=10000, min_value=0, key=f"balance_{i}")
        with cols[2]:
            rate = st.number_input(f"Interest Rate {i}", value=5.0, min_value=0.0, key=f"rate_{i}")
        with cols[3]:
            term = st.number_input(f"Term {i}", value=120, min_value=1, max_value=360, key=f"term_{i}")
        loan_inputs.append({
            "loan_name": loan_name,
            "balance": balance,
            "interest_rate": rate,
            "term_months": term
        })

# --- Show Loan Summary Table ---
if loan_inputs:
    st.subheader("📋 Loan Summary")
    summary = []
    for loan in loan_inputs:
        min_payment = calculate_minimum_payment(loan["balance"], loan["interest_rate"], loan["term_months"])
        summary.append({
            "Loan Name": loan["loan_name"],
            "Balance ($)": f"${loan['balance']:,.2f}",
            "Interest Rate (%)": f"{loan['interest_rate']}%",
            "Term (months)": loan["term_months"],
            "Minimum Payment ($)": f"${min_payment:,.2f}"
        })
    st.dataframe(pd.DataFrame(summary), use_container_width=True)
    st.markdown(f"**💵 Combined Minimum Monthly Payment: ${sum(calculate_minimum_payment(l['balance'], l['interest_rate'], l['term_months']) for l in loan_inputs):,.2f}**")
    st.markdown("### Do you have any extra money in your budget to apply toward your loans?")

# --- Step 2: Strategy Selection ---
st.header("Step 2: Strategy Selection")

new_strategy = st.selectbox("Repayment Strategy", ["Avalanche", "Snowball"], index=0 if st.session_state.strategy == "Avalanche" else 1)
if new_strategy != st.session_state.strategy:
    st.session_state.strategy = new_strategy
    st.session_state.simulate_now = True
    st.rerun()

if st.session_state.strategy == "Avalanche":
    st.markdown("""
    **Avalanche Method:**  
    This method focuses on paying off the **loan with the highest interest rate first**, while making minimum payments on the rest.
    """)
else:
    st.markdown("""
    **Snowball Method:**  
    This method pays off the **smallest loan balance first** to build momentum.
    """)

extra_payment = st.number_input("Extra Monthly Payment ($)", min_value=0, value=150)

if st.button("Simulate Repayment"):
    st.session_state.simulate_now = True
    st.rerun()

# --- Simulation ---
if st.session_state.simulate_now:
    st.success("Calculating your optimized repayment plan...")
    baseline_interest, baseline_months, _ = simulate_baseline(loan_inputs)
    strategy_loans = [loan.copy() for loan in loan_inputs]
    schedule_df = simulate_full_strategy(strategy_loans, extra_payment, strategy=st.session_state.strategy.lower())
    total_interest = schedule_df["Interest Paid"].sum()
    final_month = schedule_df["Month"].max()

    # Results
    st.subheader("📊 Summary Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Interest Saved", f"${baseline_interest - total_interest:,.2f}")
        st.metric("Time Saved", f"{baseline_months - final_month} months")
    with col2:
        st.metric("Total Interest (Standard)", f"${baseline_interest:,.2f}")
        st.metric("Total Interest (Strategy)", f"${total_interest:,.2f}")

    # Charts
    st.subheader("📈 Loan Payoff Timeline")
    fig, ax = plt.subplots(figsize=(10, 5))
    for loan in loan_inputs:
        sub_df = schedule_df[schedule_df["Loan Name"] == loan["loan_name"]]
        ax.plot(sub_df["Month"], sub_df["Remaining Balance"],
                label=f"{loan['loan_name']} (${loan['balance']:,.0f} @ {loan['interest_rate']}%)")
    ax.set_title("Loan Payoff Timeline")
    ax.set_xlabel("Month")
    ax.set_ylabel("Remaining Balance ($)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("📉 Aggressive vs. Minimum Payment")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    for loan in loan_inputs:
        base_df = generate_amortization_schedule(
            loan["loan_name"], loan["balance"], loan["interest_rate"], loan["term_months"]
        )
        ax2.plot(base_df["Month"], base_df["Remaining Balance"], linestyle="--",
                 label=f"{loan['loan_name']} - Min Payment")
    for loan_name in schedule_df["Loan Name"].unique():
        sub = schedule_df[schedule_df["Loan Name"] == loan_name]
        ax2.plot(sub["Month"], sub["Remaining Balance"], label=f"{loan_name} (Strategy)")
    ax2.set_title("Aggressive vs. Minimum Payment")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Remaining Balance ($)")
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)

    # --- Step 3: Repayment Checklist & PDF Export ---
    grouped = schedule_df.groupby("Month")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Loan Repayment Checklist", ln=True, align='C')
    pdf.ln(10)

    for month, payments in grouped:
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Month {month}", ln=True)
        pdf.set_font("Arial", size=11)
        for _, row in payments.iterrows():
            name = row["Loan Name"]
            pay = f"${row['Payment']:,.2f}"
            principal = f"${row['Principal Paid']:,.2f}"
            interest = f"${row['Interest Paid']:,.2f}"
            remaining = f"${row['Remaining Balance']:,.2f}"
            line = f"• {name} → Payment: {pay} | Principal: {principal} | Interest: {interest} | Balance Left: {remaining}"
            pdf.multi_cell(0, 8, txt=line)
        pdf.ln(4)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.subheader("📄 Repayment Checklist")
    st.download_button(
        label="📥 Download Monthly Payment Checklist (PDF)",
        data=pdf_buffer,
        file_name="Loan_Repayment_Checklist.pdf",
        mime="application/pdf"
    )

    # Reset trigger
    st.session_state.simulate_now = False
    st.session_state.triggered_rerun = None
