import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

# 1. Global Config
st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide")

# --- 2. THE GATEKEEPER (SECURITY) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.sidebar.header("🔐 Secure Access")
user_key = st.sidebar.text_input("License Key", type="password")

if user_key not in st.secrets.get("valid_keys", []):
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ FATIMA INTELLIGENCE SYSTEMS</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.error("🔒 **RESTRICTED ACCESS AREA**")
    st.info("Please enter your License Key to access the suite.")
    st.stop()

# --- 3. NAVIGATION ---
st.sidebar.markdown("---")
st.sidebar.header("🚀 Select Tool")
tool = st.sidebar.selectbox("Choose Service", ["Profit-Flow (Excel Analytics)", "Sub-Master (Digital CRM)"])

# --- 4. TOOL 1: PROFIT-FLOW (The Analytics Legend) ---
if tool == "Profit-Flow (Excel Analytics)":
    st.title("📊 Profit-Flow: Business Analytics")
    uploaded_file = st.file_uploader("Upload Excel/CSV", type=['csv', 'xlsx'])
    
    if uploaded_file:
        header_row = st.sidebar.number_input("Header Row Index", value=3)
        try:
            df = pd.read_excel(uploaded_file, header=header_row, engine='openpyxl') if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
            
            # Universal cleaning
            df = df.loc[:, [col for col in df.columns if not str(col).startswith('Unnamed')]].dropna(how='all')
            
            st.sidebar.header("🛠️ Mapping")
            all_cols = df.columns.tolist()
            status_col = st.sidebar.selectbox("Status Column", all_cols)
            price_col = st.sidebar.selectbox("Price Column", all_cols)
            client_col = st.sidebar.selectbox("Client Column", all_cols)
            
            # Fix: Force numeric conversion
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            
            # --- THE OMEGA FIX: Handle non-string values safely ---
            success_mask = df[status_col].astype(str).str.contains('Actif|Payé|✅|Livre|Success', na=False, case=False)
            delivered_count = len(df[success_mask])
            total_count = len(df)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Volume", f"{df[price_col].sum():,.2f} DH")
            success_rate = (delivered_count / total_count * 100) if total_count > 0 else 0
            c2.metric("Success Rate", f"{success_rate:.1f}%")
            c3.metric("Records", total_count)
            
            st.plotly_chart(px.pie(df, names=status_col, hole=0.4), use_container_width=True)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error processing file: {e}")

# --- 5. TOOL 2: SUB-MASTER (The Subscription Manager) ---
else:
    st.title("📱 Sub-Master: Subscription Manager")
    if 'clients_db' not in st.session_state:
        st.session_state['clients_db'] = pd.DataFrame(columns=['Name', 'Service', 'End Date', 'Status', 'Price'])

    tab1, tab2 = st.tabs(["📋 View Clients", "➕ Add Subscription"])
    
    with tab2:
        with st.form("sub_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Client Name")
            srv = c2.selectbox("Service", ["Netflix", "IPTV", "Canva", "Disney+", "Spotify"])
            e_date = c1.date_input("Expiry Date", value=date.today())
            prc = c2.number_input("Price (DH)", value=50)
            sts = st.selectbox("Status", ["Actif", "En attente", "Payé"])
            if st.form_submit_button("Save Client"):
                new_row = pd.DataFrame([[name, srv, e_date, sts, prc]], columns=st.session_state['clients_db'].columns)
                st.session_state['clients_db'] = pd.concat([st.session_state['clients_db'], new_row], ignore_index=True)
                st.success(f"Client {name} Added!")

    with tab1:
        db = st.session_state['clients_db']
        if not db.empty:
            # Fix: Proper date conversion for calculation
            db['Days Left'] = (pd.to_datetime(db['End Date']) - pd.Timestamp(date.today())).dt.days
            
            def style_days(val):
                color = 'red' if val <= 2 else 'orange' if val <= 5 else 'green'
                return f'background-color: {color}; color: white; font-weight: bold'
            
            st.dataframe(db.style.applymap(style_days, subset=['Days Left']))
            st.markdown(f"**Total Projected Revenue:** {db['Price'].sum()} DH")
        else:
            st.info("No subscriptions found yet.")
