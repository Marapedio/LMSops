import streamlit as st
import pandas as pd
import xlrd
import numpy as np

# 读取本地 funder 数据
funder_format = pd.read_excel("Tadata/funder_data.xlsx")

# 页面布局
col1, col2 = st.columns([3, 2])

with col2:
    dbs_file = st.file_uploader("Upload DBS Excel", type=["xls"])
    lms_file = st.file_uploader("Upload LMS Excel", type=["xlsx"])

# 处理 DBS 文件
if dbs_file is not None:
    dbs_df = pd.read_excel(dbs_file, skiprows=2, engine="xlrd")
    selected_cols = ["Account Number", "Currency", "Available Balance"]

    funder_format['Account no.'] = pd.to_numeric(funder_format['Account no.'], errors='coerce')
    dbs_df['Account Number'] = pd.to_numeric(dbs_df['Account Number'], errors='coerce')
    dbs_df = dbs_df[selected_cols]

    merged_df = funder_format.merge(
        dbs_df,
        left_on=["Account no.", "Currency"],
        right_on=["Account Number", "Currency"],
        how="left"
    )
    merged_df["Bank record"] = merged_df["Available Balance"]
    funder_format = merged_df.drop(columns=["Account Number", "Available Balance"])

# 处理 LMS 文件
if lms_file is not None:
    lms_df = pd.read_excel(lms_file)
    selected_cols = ["Funder ID", "Currency", "Available Balance"]
    lms_df = lms_df[selected_cols]
    lms_df['Currency'] = lms_df['Currency'].replace('CNH', 'CNY')

    merged_df = funder_format.merge(
        lms_df,
        left_on=["Funder list", "Currency"],
        right_on=["Funder ID", "Currency"],
        how="left"
    )
    merged_df["LMS Amt"] = merged_df["Available Balance"]
    funder_format = merged_df.drop(columns=["Funder ID", "Available Balance"])

# 显示原始数据
with col1:
    st.subheader("Original Data")
    st.dataframe(funder_format)

    # 如果两个文件都上传了，进行差异分析
    if lms_file is not None and dbs_file is not None:
        df = funder_format.copy()
        df.columns = df.columns.str.strip()

        required_cols = ['LMS Amt', 'Bank record']
        if all(col in df.columns for col in required_cols):
            df['Difference'] = df['LMS Amt'] - df['Bank record']
            df['Warning'] = np.where(df['Difference'] != 0, '⚠️ Difference Warning', '')
            df = df[df['Difference'] != 0]

            st.subheader("Difference Details")

            def highlight_diff(row):
                return ['background-color: yellow' if row['Difference'] != 0 else '' for _ in row]

            st.dataframe(df.style.apply(highlight_diff, axis=1))
       else:
            st.error(f"Missing required columns: {required_cols}")





