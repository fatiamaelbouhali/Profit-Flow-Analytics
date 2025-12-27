import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Fatima Intelligence CRM", layout="wide")

# 1. Gatekeeper
valid_keys = st.secrets.get("valid_keys", [])
user_key = st.sidebar.text_input("License Key", type="password")

if user_key not in valid_keys:
    st.title("🛡️ FATIMA INTELLIGENCE SYSTEMS")
    st.warning("Locked. Provide key.")
    st.stop()

# 2. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl=0)

df = load_data()

# 3. App Logic
st.title("📱 Fatima CRM Pro")
t1, t2 = st.tabs(["📋 View Clients", "➕ Add New"])

with t1:
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Database is empty.")

with t2:
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name")
        srv = st.selectbox("Service", ["Netflix", "ChatGPT", "IPTV", "Autres"])
        phone = st.text_input("Phone")
        exp = st.date_input("Expiry")
        prc = st.number_input("Price", value=50)
        
        if st.form_submit_button("🚀 SYNC TO CLOUD"):
            new_row = pd.DataFrame([{"Name": name, "Service": srv, "Phone": str(phone), "Expiry": str(exp), "Status": "Actif", "Price": prc}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.balloons()
            st.cache_data.clear()
            st.rerun()
