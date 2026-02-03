import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ads & AdMob Tracker", layout="wide")
st.title("📊 Ads Cost vs AdMob Revenue Tracker")

# 1. FILE UPLOADERS
col1, col2 = st.columns(2)
with col1:
    cost_files = st.file_uploader("Upload Google Ads Cost Files", accept_multiple_files=True, type=['xlsx', 'csv'])
with col2:
    rev_files = st.file_uploader("Upload AdMob Revenue Files", accept_multiple_files=True, type=['xlsx', 'csv'])

def load_data(uploaded_files, is_admob=False):
    all_data = []
    for f in uploaded_files:
        try:
            # Check if file is CSV or Excel
            if f.name.endswith('.csv'):
                df = pd.read_csv(f)
            else:
                # sheet_name=None reads ALL sheets
                sheets_dict = pd.read_excel(f, sheet_name=None, engine='openpyxl')
                df = pd.concat(sheets_dict.values(), ignore_index=True)
            
            # Clean column names
            df.columns = [str(c).strip().title() for c in df.columns]
            
            if is_admob:
                # Find column that looks like 'Revenue'
                rev_col = [c for c in df.columns if 'Revenue' in c or 'Earnings' in c]
                if rev_col and 'Country' in df.columns:
                    all_data.append(df[['Country', rev_col[0]]].rename(columns={rev_col[0]: 'Revenue'}))
            else:
                # Find column that looks like 'Cost'
                cost_col = [c for c in df.columns if 'Cost' in c or 'Spent' in c]
                if cost_col and 'Country' in df.columns:
                    all_data.append(df[['Country', cost_col[0]]].rename(columns={cost_col[0]: 'Cost'}))
                    
        except Exception as e:
            st.error(f"Error reading file '{f.name}': {e}")
            
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

if cost_files and rev_files:
    # Process
    cost_df_raw = load_data(cost_files, is_admob=False)
    rev_df_raw = load_data(rev_files, is_admob=True)

    if not cost_df_raw.empty and not rev_df_raw.empty:
        # Group and Merge
        cost_df = cost_df_raw.groupby('Country').sum().reset_index()
        rev_df = rev_df_raw.groupby('Country').sum().reset_index()
        
        final_df = pd.merge(cost_df, rev_df, on='Country', how='outer').fillna(0)
        final_df['Profit/Loss'] = final_df['Revenue'] - final_df['Cost']
        
        # Display
        st.subheader("Results by Country")
        st.dataframe(final_df.sort_values(by='Profit/Loss', ascending=False), use_container_width=True)
    else:
        st.warning("Make sure your files have 'Country' and 'Cost' or 'Revenue' columns.")
