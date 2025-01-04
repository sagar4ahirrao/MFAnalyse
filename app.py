import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO
import matplotlib.pyplot as plt

# Function to extract data from the uploaded PDF
def extract_data_from_pdf(pdf_file):
    extracted_data = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            extracted_data.append(text)
    return extracted_data

# Function to process and consolidate data
def process_data(extracted_data):
    data = []
    for page in extracted_data:
        lines = page.split("\n")
        for line in lines:
            if re.search(r'\d{2}-[A-Za-z]{3}-\d{4}', line):
                parts = re.split(r'\s{2,}', line)
                if len(parts) >= 5:
                    data.append({
                        "Date": parts[0],
                        "Amount": float(parts[1].replace(",", "")),
                        "NAV": float(parts[2].replace(",", "")),
                        "Units": float(parts[3].replace(",", "")),
                        "Transaction": parts[4],
                        "Balance": float(parts[5].replace(",", "")) if len(parts) > 5 else None
                    })
    return pd.DataFrame(data)

# Visualization
def visualize_data(df):
    st.header("Investment Overview")
    st.subheader("Consolidated Portfolio")

    # Group by scheme and calculate totals
    consolidated = df.groupby("Transaction")["Amount"].sum().reset_index()
    st.write("Consolidated Data", consolidated)

    # Plot pie chart of investments by transaction type
    fig1, ax1 = plt.subplots()
    ax1.pie(consolidated["Amount"], labels=consolidated["Transaction"], autopct='%1.1f%%')
    ax1.set_title("Investment Distribution")
    st.pyplot(fig1)

    # Plot profit/loss chart
    st.subheader("Profit/Loss Trend")
    profit_loss_df = df.groupby("Date").sum()["Amount"].reset_index()
    fig2, ax2 = plt.subplots()
    ax2.plot(profit_loss_df["Date"], profit_loss_df["Amount"], marker='o', linestyle='-')
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Profit/Loss")
    ax2.set_title("Profit/Loss Over Time")
    st.pyplot(fig2)

# Streamlit App
st.title("Mutual Fund Analyzer")
st.write("Upload your Consolidated Account Statements to analyze investments.")

uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        st.write(f"Processing file: {file.name}")
        raw_data = extract_data_from_pdf(file)
        processed_data = process_data(raw_data)
        all_data.append(processed_data)

    # Combine all data
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        visualize_data(final_df)
else:
    st.write("Please upload your mutual fund statements.")
