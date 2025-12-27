import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Config dial l-page (Hadi dima hiya l-lowla)
st.set_page_config(page_title="Fatima Intelligence Systems", layout="wide")

# --- 2. FATIMA'S ELITE GATEKEEPER (L-7IMAYA) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.sidebar.header("🔐 Secure Access")
user_key = st.sidebar.text_input("License Key", type="password", help="Contact Fatima for authorization.")

# The Vault (Hada kiy-9ra les keys men l-Secrets dial Streamlit)
valid_keys = st.secrets.get("valid_keys", [])

if user_key in valid_keys:
    st.session_state['authenticated'] = True
    st.sidebar.success("✅ System Unlocked")
else:
    if user_key != "":
        st.sidebar.error("❌ Access Revoked: Invalid Credentials")
    
    # L-wjah dial l-mhayba (What everyone else sees)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ FATIMA INTELLIGENCE SYSTEMS</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.error("🔒 **RESTRICTED ACCESS AREA**")
    st.write("""
        This terminal is protected by high-level encryption. 
        Unauthorised access is strictly prohibited. 
        **Please provide a valid License Key to proceed.**
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📬 **For Partnerships:** \n contact@fatima-analytics.com")
    with col2:
        # Hna nti ghadi t-bddli had l-raqm b raqm dialk s-7i7
        st.info("🔑 **Request License:** \n +212 6-XX-XX-XX-XX")
        
    st.stop() # Hna kayssali l-code, l-app kat-7bess ila ma-3ndouch l-key

# --- 3. UNIVERSAL BUSINESS ENGINE (L-APP DIYALK) ---
st.title("🚀 Profit-Flow: Smart Business Intelligence")
st.write("Welcome back, Founder. Let's analyze the growth.")

uploaded_file = st.file_uploader("Upload Business Data", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # Load logic (Same as before)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, header=3, engine='openpyxl')

        df = df.loc[:, [col for col in df.columns if not str(col).startswith('Unnamed')]]
        df = df.dropna(how='all')

        st.sidebar.header("🛠️ Column Mapping")
        all_cols = df.columns.tolist()
        
        status_col = st.sidebar.selectbox("Status", all_cols)
        price_col = st.sidebar.selectbox("Payment", all_cols)
        client_col = st.sidebar.selectbox("Client", all_cols)

        # Processing
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        total_rev = df[price_col].sum()
        positive_mask = df[status_col].astype(str).str.contains('Actif|Payé|✅|Livre|Success', case=False, na=False)
        collected_rev = df[positive_mask][price_col].sum()

        # Dashboard
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Volume", f"{total_rev:,.2f} DH")
        c2.metric("Collected", f"{collected_rev:,.2f} DH")
        c3.metric("Records", len(df))

        st.markdown("---")
        v1, v2 = st.columns(2)
        with v1:
            st.plotly_chart(px.pie(df, names=status_col, hole=0.4), use_container_width=True)
        with v2:
            st.plotly_chart(px.bar(df.head(15), x=client_col, y=price_col, color=status_col), use_container_width=True)

        st.dataframe(df.head(50))

    except Exception as e:
        st.error(f"❌ Error: {e}")
