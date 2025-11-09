import streamlit as st
import os
from PIL import Image


#---logo setting
image_path = "00images/"
logo_img = image_path+"FPops.png"
icon_img = image_path+"penguin.png"
st.logo(logo_img, icon_image=icon_img)

data_processor = st.Page(
    "Data box/DataBox.py", title="Data Processor", icon=":material/hourglass:")

lianlian_preview = st.Page(
    "Data box/Lianlian.py", title="Lian Lian", icon=":material/upload:")

settings = st.Page(
    "Data box/DataSettings.py", title="SOFR Update", icon=":material/settings:")

funder_balance = st.Page(
    "Funder Balance/FunderBalance.py",title="Funder Balance",icon=":material/bug_report:")


data_pages = [data_processor,lianlian_preview,settings]
upload_pages = [funder_balance]
#---------------------------------------------------

page_dict = {
    "Data Processor": data_pages,
    "Others": upload_pages
}

st.markdown("""
    <style>
        .block-container {
            max-width: 90% !important;
            margin: 0 auto !important;
            padding-top: 4rem !important;
            padding-right: 5rem;
            padding-left: 0rem
        }
    </style>
    """, unsafe_allow_html=True)

pg = st.navigation(page_dict)

pg.run()
