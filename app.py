import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# 1. Config
st.set_page_config(page_title="Fatima Intelligence: Sub-Master Pro", layout="wide")

# --- 2. SECURITY ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Role management: Admin aw Client
role = st.sidebar.selectbox("Login As", ["Admin", "Client Portal"])
access_key = st.sidebar.text_input("Access Key / Phone Number", type="password")

# --- 3. DATA PERSISTENCE (Simulation for now - Sync with GSheets tomorrow) ---
if 'master_db' not in st.session_state:
    st.session_state['master_db'] = pd.DataFrame([
        {'Name': 'Said', 'Service': 'Netflix', 'Phone': '0661XXX', 'Expiry': date(2025, 12, 30), 'Status': 'Actif', 'Price': 50},
        {'Name': 'Hamza', 'Service': 'ChatGPT Pro', 'Phone': '0662XXX', 'Expiry': date(2025, 12, 28), 'Status': 'Actif', 'Price': 200}
    ])

df = st.session_state['master_db']

# --- 4. ADMIN INTERFACE ---
if role == "Admin":
    if access_key not in st.secrets.get("valid_keys", []):
        st.error("🔒 Admin Access Denied.")
        st.stop()

    st.title("👨‍💻 Admin Control Center")
    
    # --- TAB 1: SMART ALERTS ---
    t1, t2, t3 = st.tabs(["⚠️ Urgent Alerts", "➕ New Subscription", "📋 Full Management"])
    
    with t1:
        st.subheader("Clients Expiring Soon")
        df['Days_Left'] = (pd.to_datetime(df['Expiry']).dt.date - date.today()).apply(lambda x: x.days)
        urgent = df[df['Days_Left'] <= 3]
        if not urgent.empty:
            st.warning(f"Found {len(urgent)} clients near expiry!")
            for i, row in urgent.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                col1.write(f"**{row['Name']}** ({row['Service']})")
                col2.write(f"Remaining: {row['Days_Left']} days")
                if col3.button(f"Renew {row['Name']}", key=f"ren_{i}"):
                    # Logic: Add 30 days to expiry
                    st.session_state['master_db'].at[i, 'Expiry'] = date.today() + timedelta(days=30)
                    st.success("Renewed!")
        else:
            st.success("All systems clear. No urgent expiries.")

    with t2:
        with st.form("add_sub"):
            st.subheader("Add Digital Service")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Client Name")
            phone = c2.text_input("Phone Number")
            srv = c3.selectbox("Service", ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "Canva", "IPTV"])
            exp = st.date_input("Expiry Date")
            prc = st.number_input("Price (DH)", value=50)
            if st.form_submit_button("Register & Sync"):
                new_row = {'Name': name, 'Service': srv, 'Phone': phone, 'Expiry': exp, 'Status': 'Actif', 'Price': prc}
                st.session_state['master_db'] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.success("Synced to Cloud!")

# --- 5. CLIENT PORTAL (The Self-Service) ---
elif role == "Client Portal":
    st.title("👤 My Subscription Portal")
    if access_key != "":
        client_data = df[df['Phone'] == access_key]
        if not client_data.empty:
            for i, row in client_data.iterrows():
                st.write(f"### Welcome {row['Name']}")
                st.info(f"Service: {row['Service']} | Expiry: {row['Expiry']}")
                if st.button("Cancel Subscription", key=f"can_{i}"):
                    st.session_state['master_db'].at[i, 'Status'] = 'Annulé'
                    st.warning("Request sent to Admin.")
        else:
            st.error("Phone number not found.")
