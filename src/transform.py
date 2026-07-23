# src/transform.py
import pandas as pd
import io
import re

def transform_data(input_buffer, file_name):
    """
    Apply a series of data cleansing and enrichment steps using Pandas.
    Only CSV and Excel files are transformed – other file types are passed through unchanged.
    The output is a new in-memory buffer ready for upload.
    """
    
    # If it's not a CSV or Excel, we just return the raw buffer as-is
    if not (file_name.endswith('.csv') or file_name.endswith('.xlsx')):
        return input_buffer

    # 1. Load data with fallback encoding (UTF-8 first, then Latin-1 for older files)
    if file_name.endswith('.csv'):
        try:
            df = pd.read_csv(input_buffer, encoding='utf-8')
        except UnicodeDecodeError:
            input_buffer.seek(0)
            df = pd.read_csv(input_buffer, encoding='latin1', sep=None, engine='python')
    else:
        df = pd.read_excel(input_buffer)

    df = df.reset_index(drop=True)

    # 2. Fix a common problem: columns shifted left when Billing Amount is empty or misaligned.
    #    We check if the 'Billing Amount' cell is actually numeric; if not, we shift that row's
    #    values one column to the right (effectively sliding everything back into place).
    def fix_shift(row):
        try:
            float(str(row['Billing Amount']).replace(',', '.'))
            return row
        except ValueError:
            cols = list(df.columns)
            if 'Billing Amount' in cols:
                idx_billing = cols.index('Billing Amount')
                for i in range(idx_billing, len(cols) - 1):
                    row[cols[i]] = row[cols[i+1]]
                row[cols[-1]] = None
            return row

    if 'Billing Amount' in df.columns:
        df = df.apply(fix_shift, axis=1)

    # 3. Strip whitespace and remove special characters from all text columns.
    #    This helps with consistency when we later do comparisons or groupings.
    regex_clean = r'[^\w\s\-\+\,]'
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(regex_clean, '', regex=True)
            df[col] = df[col].replace(['nan', 'None', '0.0', '0'], '')

    # 4. Capitalize names properly (e.g., "john doe" -> "John Doe")
    if 'Name' in df.columns:
        df['Name'] = df['Name'].str.title()

    # 5. Remove titles (Dr., Mr., etc.) from the Doctor column, then capitalize
    if 'Doctor' in df.columns:
        titles_regex = r'\b(Dr|Dr\.|Miss|MD|Mrs|Mr|PhD|Dra|Dra\.)\b'
        df['Doctor'] = df['Doctor'].str.replace(titles_regex, '', regex=True, flags=re.IGNORECASE)
        df['Doctor'] = df['Doctor'].str.strip().str.title()

    # 6. Create a unique Record_ID by combining a row counter and the Year column
    if 'Year' in df.columns:
        df['Record_ID'] = [f"{i+1}_{year}" for i, year in enumerate(df['Year'])]
        # Move Record_ID to the front for easier reading
        cols = ['Record_ID'] + [c for c in df.columns if c != 'Record_ID']
        df = df[cols]

    # 7. Ensure numeric columns are actually numeric (clean commas/points, coerce errors)
    if 'Billing Amount' in df.columns:
        df['Billing Amount'] = df['Billing Amount'].astype(str).str.replace(',', '.', regex=False)
        df['Billing Amount'] = pd.to_numeric(df['Billing Amount'], errors='coerce').fillna(0.0)
    
    if 'Age' in df.columns:
        df['Age'] = pd.to_numeric(df['Age'], errors='coerce').fillna(0).astype(int)

    # 8. Age Clustering – create a categorical column for age ranges
    if 'Age' in df.columns:
        age_limits = [-1, 18, 35, 50, 65, 150]
        age_labels = [
            '1. 0 to 18 (Ongrowing)', 
            '2. 19 to 35 (Young Adult)', 
            '3. 36 to 50 (Full grown)', 
            '4. 51 to 65 (Mature)', 
            '5. 66+ (Elder)'
        ]
        df['Health_Cluster'] = pd.cut(df['Age'], bins=age_limits, labels=age_labels)

    # 9. Billing Clustering – tiered buckets for billing amounts
    if 'Billing Amount' in df.columns:
        billing_limits = [float('-inf'), -0.01, 10000, 20000, 30000, 40000, float('inf')]
        billing_labels = [
            '0. Cashback (< 0)',
            '1. Up to 10k',
            '2. 10k to 20k',
            '3. 20k to 30k',
            '4. 30k to 40k',
            '5. Above 40k'
        ]
        df['Billing_Tier'] = pd.cut(df['Billing Amount'], bins=billing_limits, labels=billing_labels)

    # 10. Date Processing – convert to datetime, extract weekday, compute length of stay
    date_columns = ['Date of Admission', 'Discharge Date'] 
    
    # 10.1: Convert to actual datetime objects (coerce errors to NaT)
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=False)

    # 10.2: Map day of week numbers to readable labels
    if 'Date of Admission' in df.columns:
        days_map = {
            0: '1. Monday', 1: '2. Tuesday', 2: '3. Wednesday',
            3: '4. Thursday', 4: '5. Friday', 5: '6. Saturday', 6: '7. Sunday'
        }
        df['Admission_Weekday'] = df['Date of Admission'].dt.dayofweek.map(days_map)

    # 10.3: Calculate length of stay in days (difference between discharge and admission)
    if 'Date of Admission' in df.columns and 'Discharge Date' in df.columns:
        diff = (df['Discharge Date'] - df['Date of Admission']).dt.days
        df['Length_of_Stay'] = pd.to_numeric(diff, errors='coerce').fillna(0).astype(int)

    # 10.4: Format the original date columns back to YYYY-MM-DD strings (for consistency)
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d')

    # 11. Export the transformed DataFrame to a new buffer (CSV or Excel)
    output_buffer = io.BytesIO()
    if file_name.endswith('.csv'):
        df.to_csv(output_buffer, index=False, encoding='utf-8', decimal='.')
    else:
        df.to_excel(output_buffer, index=False, engine='openpyxl')
    
    output_buffer.seek(0)
    return output_buffer