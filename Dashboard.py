# STEP 1: Imports
import streamlit as st
import pandas as pd
import os
import calendar

# STEP 2: Page Config
st.set_page_config(layout="wide")

# STEP 3: Background + Styles
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f6f7;
    }
    .block-container {
        background-color: #fdfefe;
        border-radius: 8px;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# STEP 4: Title + Refresh Button
st.markdown(
    """
    <div style="text-align:center; margin-top:30px; margin-bottom:20px;">
        <h2 style="font-size:28px; color:#2E86C1; margin:0;">
            AK Family Bank Dashboard
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="text-align:right; margin-bottom:20px;">
        <form action="" method="get">
            <button style="font-size:16px; padding:4px 10px;">🔄 Refresh</button>
        </form>
    </div>
    """,
    unsafe_allow_html=True
)

# STEP 5: File Upload
def load_data(uploaded_file):
    """Load and preprocess Excel data."""
    if uploaded_file is None:
        st.warning("Please upload an Excel file to continue.")
        return None

    df = pd.read_excel(uploaded_file, sheet_name="Consolidated", header=1)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Ensure 'date' column exists
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        st.error("No 'date' column found. Columns are: " + str(df.columns.tolist()))
        st.stop()
    return df

# 🔹 Main App
uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx"])
df = load_data(uploaded_file)

if df is not None:
    # Data is loaded successfully, but no preview shown
    st.sidebar.success("✅ Data loaded from uploaded Excel file.")

    # STEP 8: Sidebar Filters
    current_year = pd.Timestamp.now().year
    current_month = pd.Timestamp.now().month
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1

    years = sorted(df["date"].dt.year.dropna().unique())
    months = sorted(df["date"].dt.month.dropna().unique())

    month_map = {i: calendar.month_abbr[i] for i in range(1, 13)}
    month_labels = [month_map[m] for m in months]

    year = st.sidebar.selectbox(
        "📅 Select Year",
        years,
        index=years.index(previous_year) if previous_year in years else 0
    )

    month_label = st.sidebar.selectbox(
        "📆 Select Month",
        month_labels,
        index=month_labels.index(month_map[previous_month]) if previous_month in months else 0
    )

    month = list(month_map.keys())[list(month_map.values()).index(month_label)]
    data_type = st.sidebar.radio("📊 Data Type", ["Raw", "Summary"])
    bank_choice = st.sidebar.selectbox("🏦 Select Bank", ["All"] + df["bank"].dropna().unique().tolist(), index=0)

    # STEP 9: Apply Filters
    filtered = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]
    if bank_choice != "All":
        filtered = filtered[filtered["bank"] == bank_choice]

    month_year_str = pd.Timestamp(year=year, month=month, day=1).strftime("%b-%y")

    # STEP 11: Bank Overview
    st.markdown("<h3 style='font-size:20px; color:#117A65;'>Bank Overview</h3>", unsafe_allow_html=True)
    bank_colors = {"DBS": "#e6f2ff", "Trust": "#e6ffe6", "OCBC": "#fff0e6", "SC": "#f9e6ff"}
    banks = ["DBS", "Trust", "OCBC", "SC"]
    cols = st.columns(4)

    for i, b in enumerate(banks):
        bank_df = filtered[filtered["bank"] == b]
        debit_total = bank_df["debit"].sum()
        credit_total = bank_df["credit"].sum()
        balance = credit_total - debit_total
        txn_count = len(bank_df)

        with cols[i]:
            st.markdown(
                f"""
                <div style="background-color:{bank_colors[b]};
                            border:1px solid #ccc;
                            padding:8px;
                            border-radius:6px;
                            text-align:center;">
                    <b>{b}</b> ({txn_count} txns)<br>
                    <span style="font-size:12px;">Debit: {debit_total:,.2f}</span><br>
                    <span style="font-size:12px;">Credit: {credit_total:,.2f}</span><br>
                    <span style="font-size:12px;">Balance: {balance:,.2f}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # STEP 12: Raw vs Summary
    if data_type == "Raw":
        st.markdown(
            f"<h3 style='font-size:20px; color:#C0392B;'>Raw Transactions ({bank_choice} – {month_year_str})</h3>",
            unsafe_allow_html=True
        )
        st.dataframe(filtered, use_container_width=True)

    else:
        view_choice = st.sidebar.radio("📊 Choose Summary View:", ["Excel Pivot", "Dynamic Summary"], index=0)

        if view_choice == "Excel Pivot":
            if uploaded_file is not None:
                summary_pivot_df = pd.read_excel(uploaded_file, sheet_name="Summary_Pivot")
                st.markdown(
                    f"<h3 style='font-size:20px; color:#E67E22;'>Summary Page (Excel Pivot – {bank_choice} – {month_year_str})</h3>",
                    unsafe_allow_html=True
                )
                st.dataframe(summary_pivot_df, use_container_width=True)
            else:
                st.warning("No file uploaded for Excel Pivot view.")

        elif view_choice == "Dynamic Summary":
            if "main category" in df.columns:
                summary_dynamic = filtered.groupby("main category").agg({
                    "debit": "sum",
                    "credit": "sum"
                }).reset_index()

                st.markdown(
                    f"<h3 style='font-size:20px; color:#E67E22;'>Summary Page (Dynamic – {bank_choice} – {month_year_str})</h3>",
                    unsafe_allow_html=True
                )
                st.dataframe(summary_dynamic, use_container_width=True)
            else:
                st.warning("No 'Main Category' column found in your Excel file.")

    # STEP 13: Totals & Reports
    st.markdown(
        f"<h3 style='font-size:20px; color:#8E44AD;'>Totals & Reports ({bank_choice} – {month_year_str})</h3>",
        unsafe_allow_html=True
    )
    overall_debit = filtered["debit"].sum()
    overall_credit = filtered["credit"].sum()
    overall_balance = overall_credit - overall_debit

    st.write(f"**Overall Debit:** {overall_debit:,.2f}")
    st.write(f"**Overall Credit:** {overall_credit:,.2f}")
    st.write(f"**Overall Balance:** {overall_balance:,.2f}")
