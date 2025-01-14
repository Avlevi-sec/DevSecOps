#automation for audits to pull quarterly scans as required per PCI

import os
import requests
from datetime import datetime
import urllib3
import xml.etree.ElementTree as ET
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



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
        "action": "logout",
    }
    cookies = {"QualysSession": session}

    response = requests.post(url, headers=headers, data=payload, verify=False,cookies=cookies)
    if response.status_code == 200:
        print("logout successfull")

def qualys_get_scans(session,date):
    titles = ['BOS-3DS','AMS-3DS','SLG-3DS','ASH-3DS']
    title_matched = False
    ref_dict = {}
    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/scan/?action=list&launched_after_datetime={date}&state=Finished"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}
    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
    root = ET.fromstring(response.content)
    for title in titles:
        title_matched = False
        for scan in root.findall('.//SCAN'):
            scan_title = scan.find('TITLE').text
            if scan_title == title:
                ref_dict [scan_title] = scan.find('REF').text
    return ref_dict

def qualys_download_csv_report(session,ref_dict):
    print("Downloading CSVs per DC")
    for title,ref in ref_dict.items():
        api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/scan/?action=fetch&scan_ref={ref}&output_format=csv_extended"
        headers = {'X-Requested-With': 'Curl'}
        cookies = {"QualysSession": session}
        response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
        with open(f"C:\\Users\\AvihayLevi\\Downloads\\{title}.csv", 'wb') as csv_file:
            csv_file.write(response.content)

def qualys_launch_pdf_report(session,ref_dict):
    template_id = 2514413
    report_ref_dict = {}
    for title,ref in ref_dict.items():
        api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/report/?action=launch&template_id={template_id}&output_format=pdf&report_refs={ref}&report_title={title}"
        headers = {'X-Requested-With': 'Curl'}
        cookies = {"QualysSession": session}
        response = requests.post(api_url,headers=headers, verify=False,cookies=cookies)
        root = ET.fromstring(response.content)
        report_ID = root.find(".//VALUE").text
        report_ref_dict[title] = report_ID
    return report_ref_dict

def qualys_download_pdf_report(session,report_ref_dict):
    print("Downloading PDF reports per DC")
    for title,ref in report_ref_dict.items():
        api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/report/?action=fetch&id={ref}"
        headers = {'X-Requested-With': 'Curl'}
        cookies = {"QualysSession": session}
        response = requests.post(api_url,headers=headers, verify=False,cookies=cookies,stream=True)
        pdf_path = f"C:\\Users\\AvihayLevi\\Downloads\\{title}.pdf"
        with open(pdf_path, 'wb') as pdf_file:
            for chunk in response.iter_content(chunk_size=128):
                pdf_file.write(chunk)
        print(f"Report PDF for {title} downloaded successfully.")



if __name__ == "__main__":
        date = input("enter date in the format Year-Month-Day\n")
        cookies = qualys_auth()
        ref_dict = qualys_get_scans(cookies["QualysSession"],date)
        qualys_download_csv_report(cookies["QualysSession"],ref_dict)
        report_ref_dict = qualys_launch_pdf_report(cookies["QualysSession"],ref_dict)
        print(report_ref_dict)
        time.sleep(120)
        qualys_download_pdf_report(cookies["QualysSession"],report_ref_dict)
        qualys_logout(cookies["QualysSession"])
