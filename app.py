import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from streamlit_gsheets import GSheetsConnection

# 1. Page Config
st.set_page_config(page_title="Fatima Intelligence: Sub-Master Pro", layout="wide")

# --- 2. SECURITY ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

role = st.sidebar.selectbox("Login As", ["Admin", "Client Portal"])
access_key = st.sidebar.text_input("Access Key / Phone Number", type="password")

# --- 3. GOOGLE SHEETS CONNECTION (THE REAL EXCEL LINK) ---
# Nti ghadi t-7etti l-URL f Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    try:
        return conn.read(ttl="1m") # Kiy-9ra l-data kol dqiqa
    except:
        # Fallback simulation if sheets not connected yet
        return pd.DataFrame(columns=['Name', 'Service', 'Phone', 'Expiry', 'Status', 'Price'])

df = get_data()

# --- 4. ADMIN INTERFACE ---
if role == "Admin":
    if access_key not in st.secrets.get("valid_keys", []):
        st.error("🔒 Admin Access Denied.")
        st.stop()

    st.title("👨‍💻 Admin Control Center (Cloud Synced)")
    
    t1, t2, t3 = st.tabs(["⚠️ Urgent Alerts", "➕ New Subscription", "📋 Full Management"])
    
    with t1:
        st.subheader("Clients Expiring Soon")
        if not df.empty:
            df['Expiry'] = pd.to_datetime(df['Expiry']).dt.date
            df['Days_Left'] = (df['Expiry'] - date.today()).apply(lambda x: x.days)
            urgent = df[df['Days_Left'] <= 3]
            if not urgent.empty:
                for i, row in urgent.iterrows():
                    st.warning(f"🚨 {row['Name']} - {row['Service']} expires in {row['Days_Left']} days!")
            else:
                st.success("All subscriptions are healthy.")

    with t2:
        with st.form("add_sub"):
            st.subheader("Add Digital Service")
            c1, c2, c3 = st.columns(3)
            name = c1.text_input("Client Name")
            phone = c2.text_input("Phone Number")
            # Choices Updated with "Autres"
            services = ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "Canva", "IPTV", "Autres"]
            srv = c3.selectbox("Service", services)
            
            # Dynamic input for "Autres"
            other_srv = ""
            if srv == "Autres":
                other_srv = st.text_input("Specify Service Name")
            
            final_srv = other_srv if srv == "Autres" else srv
            
            exp = st.date_input("Expiry Date")
            prc = st.number_input("Price (DH)", value=50)
            
            if st.form_submit_button("Register & Sync to Google Sheets"):
                # Logic to append to Google Sheets will go in Secrets
                st.success(f"Synced {final_srv} for {name} to Cloud Excel!")

# --- 5. CLIENT PORTAL ---
elif role == "Client Portal":
    st.title("👤 My Subscription Portal")
    # ... Same logic to search by phone
