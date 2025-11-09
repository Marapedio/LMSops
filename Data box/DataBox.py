import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import re
from utils.atext2df import parse_lms_to_df
from utils.atext2df import process_email_data
from utils.atext2df  import generate_approval_dataframe
from utils.bslidebar import get_funder_type, get_rate_type, get_prdtype
import utils.cintercal as trunc
from utils.cintercal import calculate_interest_components
from utils.dchecker import extract_and_validate
import streamlit.components.v1 as components
# ------------------ Cache & Constants ------------------
today = date.today().strftime('%Y-%m-%d')
# ------------------ Session State Initialization ------------------
if "sofr_df" in st.session_state:
    sofr_df = st.session_state["sofr_df"]
else:
    st.warning("Please Import Interest Rate Info First")
if "raw_input" not in st.session_state:
    st.session_state.raw_input = ""
if "fundertype_slider" not in st.session_state:
    st.session_state.fundertype_slider = "Main"
if "ratetype_slider" not in st.session_state:
    st.session_state.ratetype_slider = "SOFR+"
if "prdtype_slider" not in st.session_state:
    st.session_state.prdtype_slider = "Regular"
# ------------------ Refresh Logic ------------------
# ------------------ Utility ------------------
def clear_text():
    st.session_state.raw_input = ""
    for key in ["fundertype_slider", "ratetype_slider", "prdtype_slider"]:
        if key in st.session_state:
            del st.session_state[key]
# ------------------ Sidebar ------------------
opstype = st.sidebar.selectbox("OpsType", ["Repayment", "Rollover"], index=0)
# ------------------ Layout ------------------
col1, col2 = st.columns([3, 1])
# ------------------ Column 1: Input & Processing ------------------
with col1:
    st.header("Data Processer")
    subcol1, subcol2, subcol3 = st.columns([3, 1, 1])
    with subcol1:
        data_source = st.radio("", ["LMS", "Email"], index=0, horizontal=True, label_visibility="collapsed")
    with subcol2:
        output_button = st.button("Output")
    with subcol3:
        clean_button = st.button("Clean", on_click=clear_text)
with col2:
    default_nature = (
        "FP2.0" if data_source == "Email"
        else "Rollover" if opstype == "Rollover"
        else "Repayment"
    )
    nature_options = ["Repayment", "Rollover", "FP2.0", "Lianlian", "Other"]
    default_index = nature_options.index(default_nature)
    selected_nature = st.selectbox("Nature", nature_options, index=default_index)
    nature_input = st.text_input("Custom nature name") if selected_nature == "Other" else selected_nature
    transfer_acc = st.text_input("Other Info")
    maker_name = st.text_input("Maker Name")
    xdj_switch = st.toggle("小店金", value=False)
with col1:
    raw_input = st.text_area("Paste Your Data Here", height=120, key="raw_input")
if output_button and raw_input.strip():
    if data_source == "LMS":
        with col1:
            df = parse_lms_to_df(raw_input)
            syspreview_df = generate_approval_dataframe(df, today, nature_input,transfer_acc, maker_name)
            st.session_state.fundertype_slider = get_funder_type(df)
            st.session_state.ratetype_slider = get_rate_type(df)
            st.session_state.prdtype_slider = get_prdtype(df)
        with col2:
            fundertype = st.select_slider("Funder Type", options=["Main", "Zero", "Fixed"], value=st.session_state.fundertype_slider,label_visibility="collapsed", key="fundertype_slider")
            ratetype = st.select_slider("Rate Type", options=["SOFR+", "HIBOR+", "Fixed"],value=st.session_state.ratetype_slider,label_visibility="collapsed", key="ratetype_slider")
            prdtype = st.select_slider("Product Type", options=["Regular", "PL-novd", "RFPO"],value=st.session_state.prdtype_slider,label_visibility="collapsed", key="prdtype_slider")
            sme_interest, overdue_interest, funder_interest, spreading,note = calculate_interest_components(df, sofr_df,opstype, prdtype, ratetype, fundertype, xdj_switch)
        with col1:
            warnings, checker = extract_and_validate(df, fundertype, ratetype, sme_interest, overdue_interest, funder_interest, spreading)
            st.session_state.warnings = warnings
            if warnings:
                with st.expander("⚠️ Warnings"):
                    for w in warnings:
                        st.warning(w)
            syspreview_df['Checker'] = checker
    if data_source == "Email":
        with col1:
            syspreview_df = process_email_data(raw_input,today,nature_input,transfer_acc,maker_name)
    with col1:
        st.dataframe(syspreview_df)
        second_row = syspreview_df.iloc[0]
        row_str = '\t'.join([str(v) for v in second_row.values])
            #For Copy Botton
        styled_button = f"""
            <style>
                .copy-btn {{
                    background-color: #ffffffff;
                    color: #5063b8ff;
                    border: 2px solid #e6f1fbff";
                    padding: 1em 1em;
                    border-radius: 0.5em;
                    font-size: 1em;
                    font-family: sans-serif; 
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }}
                .copy-btn:hover {{
                    background-color: #e6f1fbff;
                }}
                .copy-msg {{
                    margin-top: 0.5em;
                    color: #00BCD4;
                    font-weight: bold;
                }}
            </style>
            <button class="copy-btn" onclick="navigator.clipboard.writeText(`{row_str}`); document.getElementById('copied').innerText='Copied';">
                Copy the trade info
            </button>
            <div id="copied" class="copy-msg"></div>
            """

        components.html(styled_button, height=120)
        if sme_interest is not None:
            cal_data = {
                "Repay":[note],
                "Product":[prdtype],
                "SME Interest": [sme_interest],
                "Overdue Interest": [overdue_interest],
                "Funder Interest": [funder_interest],
                "Spreading": [spreading],
            }
            cal_df = pd.DataFrame(cal_data )
            st.dataframe (cal_df )


if output_button and not raw_input.strip():
    with col1:
        st.warning("please paste the data first")







            