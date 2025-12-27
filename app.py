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

# --- CLOUD ENGINE (THE FINAL FIX) ---
# OMEGA: We use the ID from secrets directly
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Standard reading - it will use the spreadsheet from secrets automatically
        return conn.read(ttl=0) 
    except Exception as e:
        return pd.DataFrame(columns=['Name', 'Service', 'Phone', 'Expiry', 'Status', 'Price'])

df = load_data()

st.title("📱 Sub-Master Pro")
t1, t2 = st.tabs(["📋 Database", "➕ Add Client"])

with t2:
    with st.form("sub_form", clear_on_submit=True):
        st.subheader("New Subscription")
        c1, c2 = st.columns(2)
        name = c1.text_input("Client Name")
        phone = c2.text_input("WhatsApp")
        srv = st.selectbox("Service", ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "IPTV", "Autres"])
        exp = st.date_input("Expiry Date")
        prc = st.number_input("Price (DH)", value=50)
        
        if st.form_submit_button("🚀 SYNC TO CLOUD"):
            if name and phone:
                new_row = pd.DataFrame([{"Name": name, "Service": srv, "Phone": str(phone), "Expiry": str(exp), "Status": "Actif", "Price": prc}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                # OMEGA FORCE: Update the first worksheet
                conn.update(data=updated_df)
                st.balloons()
                st.cache_data.clear()
                st.rerun()

with t1:
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Cloud is currently empty. Add your first client.")
