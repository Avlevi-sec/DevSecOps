import pandas as pd
import glob
import os
import re
import unicodedata # Added for advanced string cleaning

# --- Configuration ---
# IMPORTANT: Adjust these paths and names to match your setup.
# Using relative paths is generally recommended for portability.
# If your script is in /Users/alevi/Code/Inventory, then './' refers to that folder.

# Path to the folder containing your main Excel file and lookup files
# If the script is in the same directory as 'Inventory', you can use './Inventory'
# Otherwise, provide the absolute path like '/Users/alevi/Code/Inventory'
BASE_FOLDER_PATH = './Inventory'

# Main Excel file details
MAIN_EXCEL_FILE = 'asset_list.xlsx'
MAIN_SHEET_NAME = 'asset_list' # Adjust sheet name as necessary
MAIN_IP_COLUMN_NAME = 'Asset' # Column in main_excel_file containing IP entries

# Lookup Excel files (ensure these are .xlsx as per your original code)
LOOKUP_FILES = [
    'Amsterdam IPs.xlsx',
    'Billerica IPs.xlsx',
    'Phoenix IPs.xlsx',
    'Slough IPs.xlsx'
]
# Columns in the lookup files that contain the IP and Hostname
LOOKUP_IP_COLUMN_NAME = 'IP Address'
LOOKUP_HOSTNAME_COLUMN_NAME = 'Hostname'

# Output file path
OUTPUT_EXCEL_FILE = 'processed_asset_list_with_hostnames.xlsx'

# --- Debugging Configuration ---
# List of specific IPs to enable detailed debugging for.
# To see ALL debug messages, you can set DEBUG_ALL_IPS = True
DEBUG_ALL_IPS = False
DEBUG_IPS = [
    "172.16.133.50", "172.16.133.57", "172.16.133.20",
    "172.16.197.101", "172.16.197.102", "172.16.197.103",
    "172.16.197.104", "172.16.197.105", "172.16.197.106",
    "172.16.197.11", "172.16.197.12", "172.16.197.13",
    "172.16.197.14", "172.16.197.144", "172.16.197.145",
    "172.16.197.146", "172.16.197.16", "172.16.197.52"
]


# --- Helper Function for Robust String Cleaning ---
def clean_string(s):
    """
    Cleans a string by removing non-printable ASCII characters,
    normalizing horizontal whitespace, and stripping leading/trailing spaces.
    Preserves newline characters (\n, \r).
    Also removes a trailing colon if present, common in IP contexts.
    NEW: Replaces '_x000D_' with actual newline characters.
    """
    if pd.isna(s):
        return ""
    s = str(s)
    # Replace '_x000D_' with actual newline characters first
    s = s.replace('_x000D_', '\n')
    # Normalize Unicode characters (e.g., full-width spaces to normal spaces)
    s = unicodedata.normalize('NFKC', s)
    # Remove all non-printable ASCII characters (except common whitespace like space, tab, newline, carriage return)
    s = ''.join(char for char in s if char.isprintable() or char in ('\n', '\t', '\r'))
    # Replace multiple horizontal spaces/tabs with a single space
    s = re.sub(r'[ \t]+', ' ', s) 
    # Strip leading/trailing whitespace from the entire string (including newlines if they are at ends)
    s = s.strip()
    # Remove trailing colon if present (specific to IP addresses)
    if s.endswith(':'):
        s = s[:-1]
    return s


# --- Helper Function to Extract IPs ---
def extract_ips_from_string(s):
    """
    Extracts all IP addresses (IPv4) from a given string.
    Handles cases where the string might contain other text or multiple IPs.
    The input string is cleaned before IP extraction.
    """
    cleaned_s = clean_string(s) # Apply cleaning
    if not cleaned_s:
        return []
    # Regular expression pattern to find IPs in the format xxx.xxx.xxx.xxx
    # This pattern is robust for standard IPv4 addresses.
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ips = re.findall(ip_pattern, cleaned_s)
    return ips

# --- Main Processing Function ---
def process_assets_with_local_lookup():
    """
    Processes the main asset list Excel file by looking up hostnames
    from specified local Excel files and appending them to IP entries.
    """
    print("--- Starting IP Hostname Lookup and Processing ---")
    print(f"Base Folder: {BASE_FOLDER_PATH}")
    print(f"Main File: {MAIN_EXCEL_FILE} (Sheet: {MAIN_SHEET_NAME}, IP Column: '{MAIN_IP_COLUMN_NAME}')")
    print(f"Lookup Files: {LOOKUP_FILES}")
    print(f"Output File: {OUTPUT_EXCEL_FILE}")

    # 1. Build a consolidated IP-to-Hostname map from all lookup files
    ip_to_hostname_map = {}
    print("\n1. Building consolidated IP-to-Hostname map...")
    for lookup_file_name in LOOKUP_FILES:
        full_lookup_path = os.path.join(BASE_FOLDER_PATH, lookup_file_name)
        if not os.path.exists(full_lookup_path):
            print(f"Warning: Lookup file not found: '{full_lookup_path}'. Skipping.")
            continue

        try:
            # Use ExcelFile to read all sheets
            xls = pd.ExcelFile(full_lookup_path)
            print(f"  Loading '{lookup_file_name}'...")
            for sheet_name in xls.sheet_names:
                df_lookup = pd.read_excel(full_lookup_path, sheet_name=sheet_name)

                # Check if required columns exist in the lookup sheet
                if LOOKUP_IP_COLUMN_NAME not in df_lookup.columns or \
                   LOOKUP_HOSTNAME_COLUMN_NAME not in df_lookup.columns:
                    print(f"    Warning: Sheet '{sheet_name}' in '{lookup_file_name}' "
                          f"is missing '{LOOKUP_IP_COLUMN_NAME}' or '{LOOKUP_HOSTNAME_COLUMN_NAME}' columns. Skipping sheet.")
                    continue

                # Populate the map
                for _, row in df_lookup.iterrows():
                    # Apply cleaning to IP and Hostname from lookup files
                    ip = clean_string(row[LOOKUP_IP_COLUMN_NAME])
                    hostname = clean_string(row[LOOKUP_HOSTNAME_COLUMN_NAME])
                    
                    if ip and hostname:
                        if ip in ip_to_hostname_map:
                            # If you want to see duplicate IPs being ignored, uncomment this:
                            # if DEBUG_ALL_IPS or ip in DEBUG_IPS:
                            #     print(f"    DEBUG (Map Build): Duplicate IP '{ip}' found. Keeping first hostname: '{ip_to_hostname_map[ip]}', ignoring '{hostname}'.")
                            pass
                        else:
                            ip_to_hostname_map[ip] = hostname
                            # --- DEBUG PRINT: What IPs are being added to the map ---
                            if DEBUG_ALL_IPS or ip in DEBUG_IPS: # Only print for IPs we are debugging
                                print(f"    DEBUG (Map Build): Added to map: IP='{ip}' (Len: {len(ip)}), Hostname='{hostname}' (Len: {len(hostname)})")
            print(f"  Finished processing '{lookup_file_name}'. Total mappings: {len(ip_to_hostname_map)}")
        except Exception as e:
            print(f"  Error processing lookup file '{lookup_file_name}': {e}")

    if not ip_to_hostname_map:
        print("\nError: No IP-to-hostname mappings were loaded from lookup files. Exiting.")
        return

    # 2. Load the main Excel file
    full_main_path = os.path.join(BASE_FOLDER_PATH, MAIN_EXCEL_FILE)
    if not os.path.exists(full_main_path):
        print(f"\nError: Main Excel file not found: '{full_main_path}'. Exiting.")
        return

    try:
        df_main = pd.read_excel(full_main_path, sheet_name=MAIN_SHEET_NAME)
        print(f"\n2. Successfully loaded main file: '{MAIN_EXCEL_FILE}'")
    except Exception as e:
        print(f"\nError loading main Excel file '{MAIN_EXCEL_FILE}': {e}. Exiting.")
        return

    # Check if the specified IP column exists in the main DataFrame
    if MAIN_IP_COLUMN_NAME not in df_main.columns:
        print(f"Error: Column '{MAIN_IP_COLUMN_NAME}' not found in the main Excel sheet.")
        print(f"Available columns in main sheet: {df_main.columns.tolist()}")
        return

    # 3. Process the main IP column
    print("\n3. Processing IP entries in the main file...")

    def process_cell_content(cell_content):
        """
        Processes a single cell's content, extracts IPs, looks them up,
        and reconstructs the string with appended hostnames.
        """
        # Apply cleaning to the entire cell content first
        # This will normalize horizontal whitespace but preserve newlines
        cleaned_cell_content = clean_string(cell_content)
        if not cleaned_cell_content:
            return ""

        # Use re.split to robustly split by various newline characters (\r, \n, \r\n)
        original_entries = re.split(r'[\r\n]+', cleaned_cell_content) 
        processed_entries = []

        print(f"\n--- Processing Cell Content: Original: '{cell_content}' ---")
        print(f"--- Cleaned Cell Content: '{cleaned_cell_content}' ---")
        print(f"--- Individual Lines (after splitting): {original_entries} ---")

        for entry in original_entries:
            entry = entry.strip() # Strip individual entry again to be safe
            if not entry:
                processed_entries.append("") # Keep empty lines empty
                continue

            # This variable will hold the modified entry for the current line
            current_line_modified = entry 
            
            # Extract all IPs from the current line (entry)
            extracted_ips = extract_ips_from_string(entry) # This already calls clean_string internally

            print(f"  Processing line: '{entry}'")
            print(f"    Extracted IPs from this line: {extracted_ips}")

            if extracted_ips:
                # Assuming the user wants to append to the full line, based on the example.
                # If there are multiple IPs on one line, we'll append the hostname of the first found IP.
                # If the requirement is to append hostnames for ALL IPs on a single line,
                # the logic would need to iterate through extracted_ips and apply replacements
                # to current_line_modified for each. For now, we append based on the first IP.
                
                ip_for_lookup = extracted_ips[0] # Take the first IP found on the line
                resolved_hostname = ip_to_hostname_map.get(ip_for_lookup, "N/A (Not Found)")

                # --- DEBUG PRINTS FOR RESOLVED HOSTNAME AND PROCESSED ENTRY ---
                if DEBUG_ALL_IPS or ip_for_lookup in DEBUG_IPS: 
                    print(f"      DEBUG (Cell Process): IP used for lookup: '{ip_for_lookup}' (Len: {len(ip_for_lookup)})")
                    print(f"      DEBUG (Cell Process): Resolved Hostname: '{resolved_hostname}' (Len: {len(resolved_hostname)})")
                    
                    if ip_for_lookup in ip_to_hostname_map:
                        print(f"      DEBUG (Cell Process): '{ip_for_lookup}' WAS FOUND in map.")
                    else:
                        print(f"      DEBUG (Cell Process): '{ip_for_lookup}' WAS NOT FOUND in map.")

                # Append the resolved_hostname to the end of the entire original line entry
                processed_entry_for_line = f"{entry}-{resolved_hostname}"
                
                if DEBUG_ALL_IPS or ip_for_lookup in DEBUG_IPS:
                    print(f"      DEBUG (Cell Process): Final processed entry for '{ip_for_lookup}': '{processed_entry_for_line}'")
                
                processed_entries.append(processed_entry_for_line)

            else:
                # If no IP found in the entry, keep original and note it
                processed_entries.append(f"{entry}-N/A (No IP detected)")
            
        # --- NEW DEBUG PRINT: Final processed entries for the cell ---
        # This checks if any IP from the original cell content is in DEBUG_IPS
        if DEBUG_ALL_IPS or any(ip in DEBUG_IPS for ip in extract_ips_from_string(cell_content)):
            print(f"    DEBUG (Cell Process): Final list for cell: {processed_entries}")
        
        return '\n'.join(processed_entries)

    # Apply the processing function to the specified column
    df_main[MAIN_IP_COLUMN_NAME] = df_main[MAIN_IP_COLUMN_NAME].apply(process_cell_content)

    # 4. Save the modified DataFrame to a new Excel file
    full_output_path = os.path.join(BASE_FOLDER_PATH, OUTPUT_EXCEL_FILE)
    try:
        df_main.to_excel(full_output_path, index=False)
        print(f"\n4. Processing complete. Modified data saved to '{full_output_path}'")
    except Exception as e:
        print(f"\nError saving output Excel file '{OUTPUT_EXCEL_FILE}': {e}")

    print("\n--- Script Finished ---")

# --- Execute the main processing function ---
if __name__ == "__main__":
    process_assets_with_local_lookup()
