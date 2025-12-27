import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

# 1. Page Config - Al-Hayba al-Ula
st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide", page_icon="🛡️")

# --- 2. THE GATEKEEPER (Protection dial Fatima) ---
valid_keys = st.secrets.get("valid_keys", [])

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

with st.sidebar:
    st.header("🔐 Secure Access")
    user_key = st.text_input("Enter License Key", type="password")
    if user_key in valid_keys:
        st.session_state['authenticated'] = True
        st.success("✅ System Unlocked")
    else:
        if user_key != "":
            st.error("❌ Access Revoked")

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ FATIMA INTELLIGENCE SYSTEMS</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.warning("🔒 **RESTRICTED AREA**: Please provide a valid License Key to proceed.")
    st.stop()

# --- 3. CLOUD ENGINE (Google Sheets Connection) ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Read live data from the specific worksheet
def load_data():
    try:
        # worksheet="SubMaster_DB" khass t-koun hiya smiya l-ta7t f l-Excel
        return conn.read(worksheet="SubMaster_DB", ttl=0)
    except Exception as e:
        return pd.DataFrame(columns=['Name', 'Service', 'Phone', 'Expiry', 'Status', 'Price'])

df = load_data()

# --- 4. MAIN INTERFACE ---
st.title("📱 Sub-Master Pro: Subscription Manager")
st.write(f"Welcome, Founder. Today is {date.today()}")

t1, t2 = st.tabs(["📋 Live Alerts & Database", "➕ Add New Client"])

with t2:
    st.subheader("Register New Digital Service")
    with st.form("registration_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Client Full Name")
        phone = c2.text_input("WhatsApp Number (e.g. 06XXXXXXXX)")
        
        services = ["Netflix", "ChatGPT Pro", "Perplexity Pro", "Gemini Pro", "Canva", "IPTV", "Autres"]
        srv = st.selectbox("Select Service", services)
        
        other_srv = ""
        if srv == "Autres":
            other_srv = st.text_input("Please specify the service name")
        
        final_srv = other_srv if srv == "Autres" else srv
        
        c3, c4 = st.columns(2)
        exp_date = c3.date_input("Expiry Date", value=date.today())
        price = c4.number_input("Price (DH)", min_value=0, value=50)
        
        submit = st.form_submit_button("🚀 SYNC TO CLOUD")
        
        if submit:
            if name and phone:
                # Prepare the record
                new_entry = pd.DataFrame([{
                    "Name": name,
                    "Service": final_srv,
                    "Phone": str(phone),
                    "Expiry": str(exp_date),
                    "Status": "Actif",
                    "Price": price
                }])
                
                # OMEGA Force Update Logic
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                
                # Push back to Google Sheets
                conn.update(worksheet="SubMaster_DB", data=updated_df)
                
                st.balloons()
                st.success(f"✅ {name} added to cloud successfully!")
                st.cache_data.clear() # Reset memory to see new data immediately
                st.rerun()
            else:
                st.error("Name and Phone are mandatory!")

with t1:
    st.subheader("Subscription Status")
    if not df.empty:
        # Alert Logic
        df_view = df.copy()
        df_view['Expiry'] = pd.to_datetime(df_view['Expiry']).dt.date
        df_view['Days Left'] = (df_view['Expiry'] - date.today()).apply(lambda x: x.days)
        
        # Color coding rows based on urgency
        def highlight_expiry(row):
            if row['Days Left'] <= 0:
                return ['background-color: #ffcccc'] * len(row)
            elif row['Days Left'] <= 3:
                return ['background-color: #fff3cd'] * len(row)
            return [''] * len(row)

        st.dataframe(df_view.style.apply(highlight_expiry, axis=1), use_container_width=True)
        
        # Summary Metrics
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Clients", len(df))
        m2.metric("Active Volume", f"{df['Price'].sum()} DH")
        urgent_count = len(df_view[df_view['Days Left'] <= 3])
        m3.metric("Urgent Renewals", urgent_count, delta=f"{urgent_count} needs action", delta_color="inverse")
    else:
        st.info("The Cloud Excel is currently empty. Add your first client to start.")
