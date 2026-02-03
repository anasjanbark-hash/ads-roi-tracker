import streamlit as st
import pandas as pd

st.set_page_config(page_title="Ads & AdMob Tracker", layout="wide")
st.title("📊 Ads Cost vs AdMob Revenue Tracker")

def find_column(df, possible_names):
    """Matches messy excel headers to our needs"""
    for col in df.columns:
        if any(name.lower() in str(col).lower() for name in possible_names):
            return col
    return None

def process_files(uploaded_files, col_types):
    all_data = []
    for f in uploaded_files:
        try:
            # Read all sheets
            sheets = pd.read_excel(f, sheet_name=None, engine='openpyxl')
            for name, df in sheets.items():
                # Clean header names (remove spaces)
                df.columns = [str(c).strip() for c in df.columns]
                
                # Find the right columns
                country_col = find_column(df, ['Country', 'Territory', 'Location', 'Geo'])
                val_col = find_column(df, col_types)
                
                if country_col and val_col:
                    clean_df = df[[country_col, val_col]].copy()
                    clean_df.columns = ['Country', 'Value']
                    # Convert Value to numbers (removes $ or ,)
                    clean_df['Value'] = pd.to_numeric(clean_df['Value'], errors='coerce')
                    # Remove 'Total' rows
                    clean_df = clean_df[clean_df['Country'].astype(str).lower() != 'total']
                    all_data.append(clean_df)
        except Exception as e:
            st.error(f"Could not read {f.name}: {e}")
    
    if not all_data:
        return pd.DataFrame(columns=['Country', 'Value'])
    
    combined = pd.concat(all_data, ignore_index=True)
    return combined.groupby('Country')['Value'].sum().reset_index()

# UI Layout
col1, col2 = st.columns(2)
with col1:
    cost_files = st.file_uploader("Upload Google Ads Files (Cost)", accept_multiple_files=True)
with col2:
    rev_files = st.file_uploader("Upload AdMob Files (Revenue)", accept_multiple_files=True)

if cost_files and rev_files:
    # Process the data
    df_cost = process_files(cost_files, ['Cost', 'Spent', 'Amount'])
    df_rev = process_files(rev_files, ['Revenue', 'Earnings', 'Estimated'])

    if not df_cost.empty and not df_rev.empty:
        # Merge the two datasets on 'Country'
        final = pd.merge(df_cost, df_rev, on='Country', how='outer', suffixes=('_Cost', '_Rev')).fillna(0)
        final['Profit'] = final['Value_Rev'] - final['Value_Cost']
        
        # Rename columns for the final display
        final.columns = ['Country', 'Total Cost', 'Total Revenue', 'Profit/Loss']
        
        st.success("Analysis Complete!")
        # Add a total row at the top
        st.metric("Total Profit/Loss", f"${final['Profit/Loss'].sum():,.2f}")
        st.dataframe(final.sort_values('Profit/Loss', ascending=False), use_container_width=True)
    else:
        st
