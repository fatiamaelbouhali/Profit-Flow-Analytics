import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

# 1. Config dial Fatima
st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide", page_icon="🛡️")

# --- 2. GATEKEEPER ---
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
    st.warning("Please provide a valid License Key.")
    st.stop()

# --- 3. CLOUD ENGINE (The Stable Fix) ---
# Hna ghadi n-stakhdmou l-url nichan men l-secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # OMEGA FIX: Using the worksheet name explicitly
        return conn.read(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], 
                         worksheet="SubMaster_DB", 
                         ttl=0)
    except Exception as e:
        st.error(f"⚠️ Connection Error: {e}")
        return pd.DataFrame(columns=['Name', 'Service', 'Phone', 'Expiry', 'Status', 'Price'])

df = load_data()

# --- 4. INTERFACE ---
st.title("📱 Sub-Master Pro")

t1, t2 = st.tabs(["📋 Live Alerts", "➕ Add Client"])

with t2:
    with st.form("sub_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name")
        phone = c2.text_input("Phone")
        srv = st.selectbox("Service", ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "IPTV", "Autres"])
        other_srv = st.text_input("Specifiy if Autres") if srv == "Autres" else ""
        final_srv = other_srv if srv == "Autres" else srv
        exp = st.date_input("Expiry")
        prc = st.number_input("Price", value=50)
        
        if st.form_submit_button("🚀 SYNC TO CLOUD"):
            if name and phone:
                new_row = pd.DataFrame([{"Name": name, "Service": final_srv, "Phone": str(phone), "Expiry": str(exp), "Status": "Actif", "Price": prc}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # OMEGA FORCE WRITE
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"],
                            worksheet="SubMaster_DB", 
                            data=updated_df)
                
                st.balloons()
                st.success("Synced!")
                st.cache_data.clear()
                st.rerun()

with t1:
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Cloud is empty. Add a client.")
