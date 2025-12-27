import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Universal Analytics", layout="wide")
# --- OMEGA GATEKEEPER: THE ARMOR ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

st.sidebar.header("🔐 Access Control")
user_key = st.sidebar.text_input("Enter License Key", type="password")

# We look for the keys in Streamlit's Secret Vault
valid_keys = st.secrets.get("valid_keys", [])

if user_key in valid_keys:
    st.session_state['authenticated'] = True
    st.sidebar.success("✅ Access Granted")
else:
    if user_key != "":
        st.sidebar.error("❌ Invalid Key")
    
    st.warning("🛡️ This system is protected by OMEGA. Enter a valid license key.")
    st.info("No license? Contact fatima@example.com")
    st.stop()

st.title("🛡️: Universal Business Intelligence")
st.write("If the data looks wrong, adjust the **Header Row** in the sidebar.")

uploaded_file = st.file_uploader("Upload Data", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # --- 1. SMART HEADER DETECTION ---
        if uploaded_file.name.endswith('.xlsx'):
            # Load first 10 rows to guess header
            df_temp = pd.read_excel(uploaded_file, header=None, nrows=10, engine='openpyxl')
            guessed_header = 0
            for i, row in df_temp.iterrows():
                if row.notnull().sum() > 3: # Ster fih aktar men 3 columns
                    guessed_header = i
                    break
            
            # SIDEBAR CONTROL FOR HEADERS
            st.sidebar.header("📂 File Structure")
            header_row = st.sidebar.number_input("Which row contains the Headers?", value=int(guessed_header), min_value=0)
            df = pd.read_excel(uploaded_file, header=header_row, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file)

        # Clean "Unnamed" columns
        df = df.loc[:, [col for col in df.columns if not str(col).startswith('Unnamed')]]
        df = df.dropna(how='all')

        if not df.empty:
            st.sidebar.header("🛠️ Smart Mapping")
            all_cols = df.columns.tolist()

            # --- 2. FUZZY DETECTION (OMEGA'S BRAIN) ---
            def guess_col(keywords, columns):
                for col in columns:
                    if any(k.lower() in str(col).lower() for k in keywords):
                        return columns.index(col)
                return 0

            status_keys = ['statut', 'status', 'etat', 'state', '✅', 'الحالة']
            price_keys = ['montant', 'price', 'taman', 'payment', 'revenue', 'dh', 'chiffre']
            client_keys = ['client', 'nom', 'name', 'user', 'ville', 'city']

            idx_status = guess_col(status_keys, all_cols)
            idx_price = guess_col(price_keys, all_cols)
            idx_client = guess_col(client_keys, all_cols)

            # UI Mapping
            status_col = st.sidebar.selectbox("Status Column", all_cols, index=idx_status)
            price_col = st.sidebar.selectbox("Payment Column", all_cols, index=idx_price)
            client_col = st.sidebar.selectbox("Client/Info Column", all_cols, index=idx_client)

            # --- 3. PROCESSING ---
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            
            total_rev = df[price_col].sum()
            positive_mask = df[status_col].astype(str).str.contains('Actif|Payé|Livre|Success|✅|Done', case=False, na=False)
            collected_rev = df[positive_mask][price_col].sum()
            
            # --- 4. DASHBOARD ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Business Volume", f"{total_rev:,.2f} DH")
            c2.metric("Collected Revenue", f"{collected_rev:,.2f} DH")
            c3.metric("Data Rows", len(df))

            st.markdown("---")
            v1, v2 = st.columns(2)
            with v1:
                st.subheader("Visual Status Analysis")
                fig_pie = px.pie(df, names=status_col, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
            with v2:
                st.subheader("Revenue Breakdown")
                fig_bar = px.bar(df.head(20), x=client_col, y=price_col, color=status_col)
                st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("📋 Data Preview")
            st.dataframe(df.head(50))
        else:
            st.warning("The selected row doesn't look like a header. Try another row number.")

    except Exception as e:

        st.error(f"❌ Error: {e}")

