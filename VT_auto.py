#query all domains/data you want in VT quickly. you can also add parameter search to cmd and do a singular search.

import vt
from pprint import pprint
import sys
import os
import requests
from termcolor import colored

url = "https://www.virustotal.com/api/v3/ip_addresses/"
key = os.environ.get("vt_api_key")
headers = {
    "accept": "application/json",
    "x-apikey": key
}
infile = "domains.txt"
malicious_dict = {}
not_found_dict = []

#response = requests.get(url, headers=headers).json()
#print(response['data']['attributes']['last_analysis_stats']['malicious'])

try:
    if sys.argv[1] == "search" and len(sys.argv) < 4:
        ip =sys.argv[2]
        response = requests.get(url+ip, headers=headers).json()
        malicious_num = response['data']['attributes']['last_analysis_stats']['malicious']
        if malicious_num > 0:
            print (colored(f"{ip} is malicious with {malicious_num} hits",'red'))
        else:
            print (colored(f"{ip} is not malicious with {malicious_num} hits",'green'))
        exit()
except:
    None

# get domains from file
with open(infile, 'r') as f:
    domains = [line.rstrip() for line in f if line.rstrip()]
    
for domain in domains:
    try:
        response = requests.get(url+domain, headers=headers).json()
        malicious_num = response['data']['attributes']['last_analysis_stats']['malicious']
        if malicious_num > 0:
            print (colored(f"{domain} is malicious with {malicious_num} hits",'red'))
            malicious_dict.update({domain:f"{malicious_num} hits"})
        else:
            print (colored(f"{domain} is not malicious with {malicious_num} hits",'green'))
    except:
        print(f"{domain} not found")
        not_found_dict.append(domain)
print(colored(malicious_dict,'red'))
print(not_found_dict)
