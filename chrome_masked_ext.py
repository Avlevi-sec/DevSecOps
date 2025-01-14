# Enter comma seperated chrome extension IDs in order to find if they exist and eliminate the fact that an installed flagged extension is actually masked malware

import requests

# Replace with your Chrome Web Store extension ID
extension_ids = 'insert suspicious extension ID'
url_list = []
for id in extension_ids.split(','):
    # Construct the URL to fetch the extension info
    url = f'https://chrome.google.com/webstore/detail/{id}'
    url_list.append(url)

    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract the extension name from the HTML response
        html = response.text
        start_index = html.find('<title>') + len('<title>')
        end_index = html.find('</title>', start_index)
        extension_name = html[start_index:end_index]
        extension_name = extension_name.split('-',1)[0]
        print(f"{extension_name}")
    else:
        print(f"Failed to fetch extension info. Status code: {response.status_code}")
for full_url in url_list:
    print(full_url)
