import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import date

# ---------------------------------------------------------
# Smart Expense Tracker - Streamlit App
# ---------------------------------------------------------

# File where all transactions will be stored
DATA_FILE = "transactions.csv"

# Categories for Income and Expense
INCOME_CATEGORIES = ["Salary", "Business", "Investment", "Gift", "Other Income"]
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other Expense"]


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def load_data():
    """Load transaction data from CSV file. Create file if it doesn't exist."""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
    else:
        df = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
        df.to_csv(DATA_FILE, index=False)
    return df


def save_data(df):
    """Save the dataframe back to CSV file."""
    df.to_csv(DATA_FILE, index=False)


def add_transaction(t_date, t_type, t_category, t_amount, t_desc):
    """Add a new transaction row and save it to CSV."""
    df = load_data()
    new_row = {
        "Date": pd.to_datetime(t_date),
        "Type": t_type,
        "Category": t_category,
        "Amount": t_amount,
        "Description": t_desc
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)


# ---------------------------------------------------------
# Streamlit App Configuration
# ---------------------------------------------------------

st.set_page_config(page_title="Smart Expense Tracker", page_icon="💰", layout="wide")

st.title("💰 Smart Expense Tracker")

# Sidebar Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Add Transaction", "View Summary", "Analytics Chart"])

# Load existing data once
data = load_data()


# ---------------------------------------------------------
# PAGE 1: Add Transaction
# ---------------------------------------------------------
if page == "Add Transaction":
    st.subheader("➕ Add a New Transaction")

    # Choose transaction type first so category list updates accordingly
    t_type = st.radio("Transaction Type", ["Income", "Expense"], horizontal=True)

    # Pick category list based on type
    if t_type == "Income":
        category_list = INCOME_CATEGORIES
    else:
        category_list = EXPENSE_CATEGORIES

    # Input form
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            t_date = st.date_input("Date", value=date.today())
            t_category = st.selectbox("Category", category_list)

        with col2:
            t_amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
            t_desc = st.text_input("Description (optional)")

        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            if t_amount <= 0:
                st.error("⚠️ Please enter an amount greater than 0.")
            else:
                add_transaction(t_date, t_type, t_category, t_amount, t_desc)
                st.success(f"✅ {t_type} of ₹{t_amount:.2f} added successfully!")


# ---------------------------------------------------------
# PAGE 2: View Summary
# ---------------------------------------------------------
elif page == "View Summary":
    st.subheader("📊 Financial Summary")

    if data.empty:
        st.info("No transactions yet. Go to 'Add Transaction' to get started.")
    else:
        # Calculate totals
        total_income = data[data["Type"] == "Income"]["Amount"].sum()
        total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
        balance = total_income - total_expense

        # Display totals in 3 columns
        col1, col2, col3 = st.columns(3)
        col1.metric("💵 Total Income", f"₹{total_income:,.2f}")
        col2.metric("💸 Total Expense", f"₹{total_expense:,.2f}")
        col3.metric("🏦 Balance", f"₹{balance:,.2f}")

        st.markdown("---")
        st.subheader("📜 Transaction History")

        # Sort by most recent first
        display_df = data.sort_values(by="Date", ascending=False).reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True)

        # Option to download data
        csv_data = display_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Transactions as CSV", csv_data, "transactions.csv", "text/csv")

        # Option to clear all data
        st.markdown("---")
        if st.button("🗑️ Clear All Data"):
            empty_df = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
            save_data(empty_df)
            st.warning("All transaction data has been cleared. Please refresh the page.")


# ---------------------------------------------------------
# PAGE 3: Analytics Chart
# ---------------------------------------------------------
elif page == "Analytics Chart":
    st.subheader("📈 Expense Breakdown")

    if data.empty:
        st.info("No transactions yet. Go to 'Add Transaction' to get started.")
    else:
        expense_data = data[data["Type"] == "Expense"]

        if expense_data.empty:
            st.info("No expense data available to plot.")
        else:
            # Group expenses by category
            category_summary = expense_data.groupby("Category")["Amount"].sum().reset_index()

            # Pie chart using Plotly
            fig = px.pie(
                category_summary,
                names="Category",
                values="Amount",
                title="Expense Distribution by Category",
                hole=0.3  # makes it a donut chart, looks nicer
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("📅 Monthly Income vs Expense")

            # Create a Month column for grouping
            data["Month"] = pd.to_datetime(data["Date"]).dt.to_period("M").astype(str)

            monthly_summary = data.groupby(["Month", "Type"])["Amount"].sum().reset_index()

            # Bar chart comparing income vs expense per month
            bar_fig = px.bar(
                monthly_summary,
                x="Month",
                y="Amount",
                color="Type",
                barmode="group",
                title="Monthly Income vs Expense"
            )
            st.plotly_chart(bar_fig, use_container_width=True)


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ using Streamlit")