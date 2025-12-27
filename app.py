import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide", page_icon="🛡️")

# --- SECURITY ---
valid_keys = st.secrets.get("valid_keys", [])
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

with st.sidebar:
    st.header("🔐 Secure Access")
    user_key = st.text_input("License Key", type="password")
    if user_key in valid_keys:
        st.session_state['authenticated'] = True

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center;'>🛡️ FATIMA INTELLIGENCE SYSTEMS</h1>", unsafe_allow_html=True)
    st.stop()

# --- CLOUD CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # worksheet="SubMaster_DB" khass t-koun smiya dial l-tab l-ta7t f Google Sheets
        return conn.read(worksheet="SubMaster_DB", ttl=0)
    except Exception as e:
        st.error(f"❌ Connection Error [404]: Check your Spreadsheet ID and Permissions. {e}")
        return pd.DataFrame(columns=['Name', 'Service', 'Phone', 'Expiry', 'Status', 'Price'])

df = load_data()

st.title("📱 Sub-Master Pro")
t1, t2 = st.tabs(["📋 Database", "➕ Add Client"])

with t2:
    with st.form("sub_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        srv = st.selectbox("Service", ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "IPTV", "Autres"])
        exp = st.date_input("Expiry")
        prc = st.number_input("Price", value=50)
        
        if st.form_submit_button("🚀 SYNC TO CLOUD"):
            if name and phone:
                new_row = pd.DataFrame([{"Name": name, "Service": srv, "Phone": str(phone), "Expiry": str(exp), "Status": "Actif", "Price": prc}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="SubMaster_DB", data=updated_df)
                st.balloons()
                st.cache_data.clear()
                st.rerun()

with t1:
    st.dataframe(df, use_container_width=True)
