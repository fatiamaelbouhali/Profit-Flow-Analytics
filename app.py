import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import date

st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide", page_icon="🛡️")

# 1. GATEKEEPER (The Security)
valid_keys = st.secrets.get("valid_keys", ["FATIMA-2026"])
user_key = st.sidebar.text_input("License Key", type="password")

if user_key not in valid_keys:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ FATIMA INTELLIGENCE</h1>", unsafe_allow_html=True)
    st.warning("Locked. Please enter your Master Key to proceed.")
    st.stop()

# 2. CLOUD ENGINE
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl=0) # Get real-time data

df = load_data()

# 3. INTERFACE
st.title("📱 Sub-Master Pro: Digital CRM")
st.write(f"Founder Dashboard | {date.today()}")

t1, t2 = st.tabs(["📋 View Database", "➕ Register New Client"])

with t1:
    if not df.empty:
        # Alert Urgency
        df['Expiry'] = pd.to_datetime(df['Expiry']).dt.date
        df['Days Left'] = (df['Expiry'] - date.today()).apply(lambda x: x.days)
        st.dataframe(df.style.apply(lambda x: ['background-color: #ffcccc' if x['Days Left'] <= 3 else '' for _ in x], axis=1), use_container_width=True)
    else:
        st.info("The database is waiting for its first record.")

with t2:
    with st.form("add_form", clear_on_submit=True):
        st.subheader("Add New Subscription")
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name")
        phone = c2.text_input("WhatsApp (e.g. 06XX)")
        
        services = ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "IPTV", "Autres"]
        srv = st.selectbox("Select Service", services)
        other_srv = st.text_input("If Autres, specify name:") if srv == "Autres" else ""
        final_srv = other_srv if srv == "Autres" else srv
        
        exp = st.date_input("Expiry Date")
        prc = st.number_input("Price (DH)", value=50)
        
        if st.form_submit_button("🚀 SYNC TO CLOUD"):
            if name and phone:
                new_row = pd.DataFrame([{"Name": name, "Service": final_srv, "Phone": str(phone), "Expiry": str(exp), "Price": prc, "Status": "Actif"}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.balloons()
                st.success(f"{name} is now Cloud-Secured.")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Missing critical info.")
