import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide")

# --- 2. THE GATEKEEPER (SECURITY) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.sidebar.header("🔐 Secure Access")
user_key = st.sidebar.text_input("License Key", type="password")

valid_keys = st.secrets.get("valid_keys", [])

if user_key in valid_keys:
    st.session_state['authenticated'] = True
    st.sidebar.success("✅ System Unlocked")
else:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ FATIMA INTELLIGENCE SYSTEMS</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.error("🔒 **RESTRICTED ACCESS AREA**")
    st.write("Please provide a valid License Key to proceed.")
    st.stop()

# --- 3. THE ANALYTICS ENGINE (VISIBLE ONLY AFTER UNLOCK) ---
st.title("🚀 Profit-Flow: Smart Business Intelligence")

uploaded_file = st.file_uploader("Upload Business Data", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # SIDEBAR CONTROLS
        st.sidebar.header("📂 File Structure")
        # Hada howa l-bouton li mcha lik!
        header_row = st.sidebar.number_input("Which row contains the Headers?", value=3, min_value=0)

        # Loading Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, header=header_row, engine='openpyxl')

        # Clean "Unnamed" columns
        df = df.loc[:, [col for col in df.columns if not str(col).startswith('Unnamed')]]
        df = df.dropna(how='all')

        if not df.empty:
            st.sidebar.header("🛠️ Column Mapping")
            all_cols = df.columns.tolist()
            
            # Select boxes for the user
            status_col = st.sidebar.selectbox("Select Status Column", all_cols)
            price_col = st.sidebar.selectbox("Select Payment Column", all_cols)
            client_col = st.sidebar.selectbox("Select Client Column", all_cols)

            # Calculations
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            total_rev = df[price_col].sum()
            
            # Identify 'Actif' or 'Payé'
            positive_mask = df[status_col].astype(str).str.contains('Actif|Payé|✅|Livre|Success', case=False, na=False)
            collected_rev = df[positive_mask][price_col].sum()

            # Dashboard Display
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Volume (CA)", f"{total_rev:,.2f} DH")
            c2.metric("Collected Revenue", f"{collected_rev:,.2f} DH")
            c3.metric("Total Records", len(df))

            st.markdown("---")
            v1, v2 = st.columns(2)
            with v1:
                st.subheader("Status Analysis")
                st.plotly_chart(px.pie(df, names=status_col, hole=0.4), use_container_width=True)
            with v2:
                st.subheader("Revenue by Client")
                st.plotly_chart(px.bar(df.head(15), x=client_col, y=price_col, color=status_col), use_container_width=True)

            st.subheader("📋 Raw Data Preview")
            st.dataframe(df.head(50))

    except Exception as e:
        st.error(f"❌ OMEGA Error: {e}")
