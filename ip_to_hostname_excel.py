import pandas as pd
import glob
import os
import re

# Define the filenames
main_excel_file = './Inventory/Asset_list.xlsx'
lookup_files = ['Amsterdam IPs.xlsx', 'Billerica IPs.xlsx', 'Phoenix IPs.xlsx', 'Slough IPs.xlsx']
folder_path = "/Users/alevi/Code/Inventory"

# Function to extract IPs from strings using regular expression
def extract_ips(s):
    # Regular expression pattern to find IPs in the format xxx.xxx.xxx.xxx
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = re.findall(ip_pattern, s)
    return ips

# Function to perform VLOOKUP and retrieve value from other sheets
def vlookup_ip(ip, lookup_df):
    print(df_lookup.head())
    # Perform lookup in the provided DataFrame based on 'IP Address' column
    try:
        result = lookup_df.loc[lookup_df['IP Address'] == ip, 'Hostname'].values
    except:
        None
    try:
        if len(result) > 0:
            return result[0]
        return None
    except:
        None

# Load main Excel file and extract IPs
df_main = pd.read_excel(main_excel_file, sheet_name='asset_list')  # Adjust sheet name as necessary
df_main['IPs'] = df_main['Asset'].apply(extract_ips)

# Prepare to collect results
results = []

# Iterate through each lookup file
for lookup_file in lookup_files:
    # Load all sheets from the lookup Excel file
    xls = pd.ExcelFile(f"{folder_path}/{lookup_file}")
    for sheet_name in xls.sheet_names:
        df_lookup = pd.read_excel(f"{folder_path}/{lookup_file}", sheet_name=sheet_name)
        
        # Flatten list of IPs (since each cell can contain multiple IPs)
        ips_list = [ip for ips in df_main['IPs'] for ip in ips]
        
        # Perform VLOOKUP for each IP in main file
        for ip in ips_list:
            lookup_result = vlookup_ip(ip, df_lookup)
            if lookup_result is not None:
                results.append({'IP': ip, 'Hostname': lookup_result, 'Source': f'{os.path.basename(lookup_file)} - {sheet_name}'})

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Print or process df_results as needed
print(df_results)

# Optionally, write df_results to a new Excel file
output_file = './Inventory/lookup_results.xlsx'
df_results.to_excel(output_file, index=False)

print(f"Lookup results have been saved to {output_file}")
