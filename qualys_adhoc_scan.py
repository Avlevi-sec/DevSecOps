#Adhoc scan which lets the user pick a specific CVE and test assets against it. good for PT validation and zero days.

import requests
import json
import os
import xml.etree.ElementTree as ET
import urllib3
import xmltodict
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import traceback

def qualys_auth():
    # First authenticate the user to get the token needed for subsequent API calls
    password = os.environ.get('qualys_pass')
    url = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/session/"
    headers = {'X-Requested-With': 'Curl'}
    payload = {
        "action": "login",
        "username": "user",
        "password": f"{password}"
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    cookies = response.cookies.get_dict()
    print(f"The Login suceeded!")
    return cookies

def qualys_logout(session):
    print(f"Session number: {session} logout")
    # First authenticate the user to get the token needed for subsequent API calls
    url = "https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/session/"
    headers = {'X-Requested-With': 'Curl'}
    payload = {
        "action": "logout"
    }
    cookies = {"QualysSession": session}

    response = requests.post(url, headers=headers, data=payload, verify=False,cookies=cookies)
    if response.status_code == 200:
        print("logout successfull")


def qualys_cve_list(session):
    product = input("please enter product/CVE title\n")
    CVE_ID = input("please enter the CVE ID\n")
    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/qid/search_list/dynamic/?action=create&title={product}-{CVE_ID}&cve_ids_filter=1&cve_ids={CVE_ID}"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}

    #transfers the CSV format HTTP response into memory and saves it into dataframe
    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
    root = ET.fromstring(response.text)
    dynamic_list_id = root.find(".//VALUE").text
    print("cve list created")
    return dynamic_list_id, CVE_ID

def qualys_adhoc_option_profile(dynamic_list_id,session):
    adhoc_option_profile_id = "1703922"
    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/subscription/option_profile/vm/?action=update&id={adhoc_option_profile_id}&vulnerability_detection=custom&custom_search_list_ids={dynamic_list_id}"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}

    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
    print("adhoc option profile created")

def qualys_adhoc_scan(dc,attributes,CVE_ID,session):
    adhoc_option_profile_id = "1703922"
    title = f"{dc} - {CVE_ID}"
    appliance = attributes[0]
    asset_grp = attributes[1]

    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/scan/?action=launch&target_from=assets&scan_title={title}&asset_groups={asset_grp}&iscanner_name={appliance}&option_id={adhoc_option_profile_id}"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}

    #transfers the CSV format HTTP response into memory and saves it into dataframe
    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
    if response.status_code == 200:
         print(f"scan launched for {dc}")
    else:
         print(f"error launching scan for {dc}")


if __name__ == "__main__":
    cookies = qualys_auth()
    session = cookies["QualysSession"]
    scan_dict = {"generic_assets_title":["actual","asset group names"]}
    try:
        dynamic_list_id,CVE_ID = qualys_cve_list(session)
        qualys_adhoc_option_profile(dynamic_list_id,session)
        print("starting to launch scans...")
        for key,value in scan_dict.items():
             qualys_adhoc_scan(key,value,CVE_ID,session)
             #qualys_adhoc_scan(key,value,"cve-2023-20198",session)
        
        
    except Exception as e:
                    traceback.print_exc()
    qualys_logout(session)
