import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ads & AdMob Tracker", layout="wide")
st.title("📊 Ads Cost vs AdMob Revenue Tracker")

# 1. FILE UPLOADERS
col1, col2 = st.columns(2)
with col1:
    cost_files = st.file_uploader("Upload Google Ads Cost Excels", accept_multiple_files=True, type=['xlsx'])
with col2:
    rev_files = st.file_uploader("Upload AdMob Revenue Excels", accept_multiple_files=True, type=['xlsx'])

if cost_files and rev_files:
    # 2. PROCESS ADS COST
    all_costs = []
    for f in cost_files:
        # Load all sheets from the file
        sheets_dict = pd.read_excel(f, sheet_name=None)
        for sheet_name, df in sheets_dict.items():
            # Standardize column names (assuming they have 'Country' and 'Cost')
            df.columns = [str(c).strip().title() for c in df.columns]
            if 'Country' in df.columns and 'Cost' in df.columns:
                all_costs.append(df[['Country', 'Cost']])
    
    cost_df = pd.concat(all_costs).groupby('Country').sum().reset_index()

    # 3. PROCESS ADMOB REVENUE
    all_revs = []
    for f in rev_files:
        df = pd.read_excel(f)
        df.columns = [str(c).strip().title() for c in df.columns]
        # AdMob usually calls it 'Estimated Revenue' or 'Revenue'
        # We rename it to 'Revenue' for consistency
        rev_col = [c for c in df.columns if 'Revenue' in c][0]
        all_revs.append(df[['Country', rev_col]].rename(columns={rev_col: 'Revenue'}))
    
    rev_df = pd.concat(all_revs).groupby('Country').sum().reset_index()

    # 4. MERGE & CALCULATE
    final_df = pd.merge(cost_df, rev_df, on='Country', how='outer').fillna(0)
    final_df['Profit/Loss'] = final_df['Revenue'] - final_df['Cost']
    final_df['ROI %'] = (final_df['Profit/Loss'] / final_df['Cost'] * 100).round(2)

    # 5. DISPLAY RESULTS
    st.divider()
    st.subheader("Final Combined Country List")
    st.dataframe(final_df.style.background_gradient(subset=['Profit/Loss'], cmap='RdYlGn'))
else:
    st.info("Please upload both Google Ads and AdMob files to begin.")
