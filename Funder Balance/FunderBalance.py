import streamlit as st
import pandas as pd
import xlrd
import numpy as np
funder_format = pd.read_excel("Tadata/funder_data.xlsx")


col1, col2 = st.columns([3,2])

with col2:
    dbs_file = st.file_uploader("Upload DBS Excel", type=["xls"])
    lms_file = st.file_uploader("Upload LMS Excel", type=["xlsx"])



if dbs_file is not None:
    dbs_df = pd.read_excel(dbs_file, skiprows=2, engine="xlrd")  # 跳过第一行，从第二行开始读取
    selected_cols = ["Account Number", "Currency", "Available Balance"]
    funder_format['Account no.'] = pd.to_numeric(funder_format['Account no.'], errors='coerce')
    dbs_df['Account Number'] = pd.to_numeric(dbs_df['Account Number'], errors='coerce')
    dbs_df= dbs_df[selected_cols]
    merged_df = funder_format.merge(
            dbs_df,
            left_on=["Account no.", "Currency"],
            right_on=["Account Number", "Currency"],
            how="left"
        )
    merged_df["Bank record"] = merged_df["Available Balance"]
    funder_format = merged_df.drop(columns=["Account Number", "Available Balance"])

if lms_file is not None:
    lms_df = pd.read_excel(lms_file)  # 跳过第一行，从第二行开始读取
    selected_cols = ["Funder ID", "Currency", "Available Balance"]
    lms_df = lms_df[selected_cols]
    merged_df = funder_format.merge(
            lms_df ,
            left_on=["Funder list", "Currency"],
            right_on=["Funder ID", "Currency"],
            how="left"
        )
    merged_df["LMS Amt"] = merged_df["Available Balance"]
    funder_format = merged_df.drop(columns=["Funder ID", "Available Balance"])
with col1:
    st.subheader("Original Data")
    st.dataframe(funder_format)

    if lms_file is not None and dbs_file is not None:
        df = funder_format.copy()

        # Clean column names
        df.columns = df.columns.str.strip()

        # Check required columns
        required_cols = ['LMS Amt', 'Bank record']
        if all(col in df.columns for col in required_cols):
            # Calculate difference
            df['Difference'] = df['LMS Amt'] - df['Bank record']

            # Mark rows with non-zero difference
            df['Warning'] = np.where(df['Difference'] != 0, '⚠️ Difference Warning', '')

            # Display processed data with highlighted rows
            st.subheader("Difference Details")
            def highlight_diff(row):
                return ['background-color: yellow' if row['Difference'] != 0 else '' for _ in row]

            st.dataframe(df.style.apply(highlight_diff, axis=1))

            # Display warning list
            warning_col = 'Funder ID' if 'Funder ID' in df.columns else 'Funder list'
            if warning_col in df.columns:
                warnings = df[df['Difference'] != 0][[warning_col, 'Difference']]
                if not warnings.empty:
                    st.subheader("⚠️ Warning List")
                    st.table(warnings)
                else:
                    st.success("Funder balance is OK. Thank you 😊")
            else:
                st.warning(f"Column '{warning_col}' not found. Cannot display warning list.")
        else:
            st.error(f"Missing required columns: {required_cols}")





