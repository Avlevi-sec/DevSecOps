import requests
from atlassian import Jira
import urllib3
import pandas as pd
from io import StringIO
import xmltodict
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import PySimpleGUI as sg
from tempfile import NamedTemporaryFile
import os
import urllib.parse
import json



def tag_cleaner(html_string):
     soup = BeautifulSoup(html_string, 'html.parser')
     # Find all <a> tags
     a_tags = soup.find_all('a')

     # Iterate over each <a> tag
     for tag in a_tags:
         # Extract the URL from the href attribute
         url = tag['href']
         # Replace the <a> tag with the URL text
         tag.string = url

     # Get the cleaned string
     cleaned_string = soup.get_text()
     return cleaned_string

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

def Create_Issue_Jira(issue,csv_filename):
    #Auth with Jira
    jira = Jira(
        url='https://outseer.atlassian.net/',
        username='user@corp.com',
        password=os.environ.get("jira_pass"),
        cloud=True,
        verify_ssl=False) ##fix verify ssl with Amir 
    #create issue in relevant Jira Porjects
    print("creating the issue called: "+ f"{issue['summary']}")
    created_issue = jira.create_issue(issue)
    created_issue_key = created_issue["key"]
    csv_filepath = os.path.abspath(csv_filename)
    jira.add_attachment(created_issue_key, csv_filepath)
    os.remove(csv_filename)

def qualys_issues(session,qids,project):
    #Retrive hosts affected by a specific qid in qids nad tag is set to only On-Prem All assets
    print(f"Trying to retrive hosts affected by {qids}")
    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/asset/host/vm/detection/?action=list&qids={qids}&use_tags=1&tag_set_by=name&tag_set_include=On-Prem All&output_format=CSV_NO_METADATA&"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}

    #transfers the CSV format HTTP response into memory and saves it into dataframe
    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies )
    response_content = response.content.decode("utf-8")
    response_file = StringIO(response_content)
    df = pd.read_csv(response_file)

    #retrive the qid vulnerability information and description
    api_url = f"https://qualysapi.qg2.apps.qualys.com/api/2.0/fo/knowledge_base/vuln/?action=list&ids={qids}"
    headers = {'X-Requested-With': 'Curl'}
    cookies = {"QualysSession": session}
    
    response = requests.post(api_url,headers=headers, verify=False,cookies=cookies )
    dict_data = xmltodict.parse(response.content)
    vulnerability_data = dict_data['KNOWLEDGE_BASE_VULN_LIST_OUTPUT']['RESPONSE']['VULN_LIST']['VULN']
    vul_title = vulnerability_data['TITLE']
    vul_severity = vulnerability_data['SEVERITY_LEVEL']
    vul_description = vulnerability_data['DIAGNOSIS']
    vul_solution = vulnerability_data['SOLUTION']

    #strip html tags for all jira description values
    vul_description = tag_cleaner(vul_description)
    vul_solution = tag_cleaner(vul_solution)


    #setup a ticket using the data above
    hosts = []
    ips = []
    results = []
    for _,row in df.iterrows():
        #pull row data
        hosts.append(row['DNS Name'])
        ips.append(row['IP Address'])
        results.append((row['Results']).replace("\n"," "))
    df_hosts = pd.DataFrame({'host':hosts,'IP':ips,'Result':results})
    temp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    csv_filename = temp_file.name
    df_hosts.to_csv(csv_filename, index=False)
    temp_file.close()
    if project == 'TOP':
            task_issue = {
            'project':{'key':project},
            'summary':f"QID {qids} - {vul_title}",
            'description': '*Threat*\n' + f"{vul_description}" + \
            '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
            '\n*Affected Assets added as CSV*\n',
            'issuetype': {'name': 'TechOps Task'},
            'customfield_11519':{'value':'Qualys','id':'26130'}, #Security Tool
            'customfield_11086':{'value':'Critical','id':'23014'}, #Security Severity, High ID is 23013 etc -1 for each value
            }
            Create_Issue_Jira(task_issue,csv_filename)
    if project == 'VMPX': # for testing,13191 qid
            task_issue = {
            'project':{'key':project},
            'summary':f"QID {qids} - {vul_title}",
            'description': '*Threat*\n' + f"{vul_description}" + \
            '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
            '\n*Affected Assets added as CSV*\n',
            'issuetype': {'name': 'Task'},
            'customfield_10370':{'value':'High','id':'28291'},
            'customfield_11519':{'value':'Orca','id':'26129'},
            'customfield_11321':{'value':'FM','id':'28297'},
            }
            Create_Issue_Jira(task_issue,csv_filename)
            print("Created VMPX ticket")
    if project == 'NGAC':
            task_issue = {
            'project':{'key':project},
            'summary':f"QID {qids} - {vul_title}",
            'description': '*Threat*\n' + f"{vul_description}" + \
            '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
            '\n*Affected Assets added as CSV*\n',
            'issuetype': {'name': 'Story'},
            'customfield_10678':{'value':'Approved vulnerability with FM team'}, #Criteria Acceptance text box field
            'customfield_10166':{'value':'No','id':'11534'}, #New Documentation field
            #need to add security fields once available
            }
            Create_Issue_Jira(task_issue,csv_filename)
            print("Created NGAC ticket")
    

def orca_issues(headers,vul_title,project,severity):
    # do calls to Orca Security API with an API token
    # Using sonar query we get all the hosts affected and using another specific alert query we get the vulnerability details
    severity_jira_ids_vmpx = {'informational':'28292','low':'28290','medium':'28289','high':'28291','critical':'28288'}
    severity_jira_ids_prod= {'informational':'23015','low':'23011','medium':'23012','high':'23013','critical':'23014'}

    ###########
    query = 'Alert with AlertType = "%s" and RiskLevel = "%s" and (CloudAccount.Name like "FRI" or CloudAccount.Name like "Shared_Services" or CloudAccount.Name like "Data_Warehouse")' % (vul_title,severity)
    response = requests.get("https://api.orcasecurity.io/api/sonar/query", headers=headers,params={"query":query}).json()
    print(response)
    hosts = []
    orca_ids = []
    for alert in response['data']:
        asset_name = alert['data']['Source']
        if asset_name.startswith("vm"):
              asset_name = alert['data']['Hostname']
        alert_id = alert['name']
        alert_link = f"https://app.orcasecurity.io/alerts/{alert_id}"
        hosts.append(asset_name)
        orca_ids.append(alert_link)
    df_hosts=pd.DataFrame({'asset':hosts,'alert id':orca_ids})
    temp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    csv_filename = temp_file.name
    df_hosts.to_csv(csv_filename, index=False)
    temp_file.close()
    orca_id = (orca_ids[0]).split("/")[-1]
    response = requests.get(f"https://api.orcasecurity.io/api/alerts/{orca_id}", headers=headers).json()
    vul_description = response['details']
    vul_solution = response['recommendation']
    ###########

    if project == 'TOP':
                severity_jira_id = severity_jira_ids_prod[severity]
                task_issue = {
                'project':{'key':project},
                'summary':f"{vul_title}",
                'description': '*Threat*\n' + f"{vul_description}" + \
                '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
                '\n*Affected Assets added as CSV*\n',
                'issuetype': {'name': 'TechOps Task'},
                'customfield_11519':{'value':'Orca','id':'26129'}, #Security Tool
                'customfield_11086':{'value':severity,'id':severity_jira_id}, #Security Severity, defined at the top
                }
                Create_Issue_Jira(task_issue,csv_filename)
                print("Created TOP ticket")
    if project == 'VMPX': # for testing,Service Vulnerability
                severity_jira_id = severity_jira_ids_vmpx[severity]
                task_issue = {
                'project':{'key':project},
                'summary':f"{vul_title}",
                'description': '*Threat*\n' + f"{vul_description}" + \
                '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
                '\n*Affected Assets added as CSV*\n',
                'issuetype': {'name': 'Task'},
                'customfield_10370':{'value':severity,'id':severity_jira_id},
                'customfield_11519':{'value':'Orca','id':'26129'},
                'customfield_11321':{'value':'FM','id':'28297'},
                }
                Create_Issue_Jira(task_issue,csv_filename)
                print("Created VMPX ticket")
    if project == 'PROD':
                task_issue = {
                'project':{'key':project},
                'summary':f"Orca - {vul_title}",
                'description': '*Threat*\n' + f"{vul_description}" + \
                '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
                '\n*Affected Assets added as CSV*\n',
                'issuetype': {'name': 'Change Request'},
                'customfield_10296':{'value':'Tech debt','id':'28238'}, #Change Request Type
                'customfield_11483':{'value':'Fraud Manager on Cloud(FMoC)','id':'25801'}, #FRI Product - Customers
                'customfield_10294':{'value':'Security','id':'28232'}, #Change Initiation Group
                'customfield_10158':{'value':'Improtant Vulnerability'}, #Business Justification
                'customfield_10299':{'value':'N/A'}, #Revenue Opportunity
                'customfield_10301':{'value':'N/A'}, #Salesforce Ticket ID
                'customfield_11849':{'value':'Security Vulnerability'}, #Use case
                'customfield_11851':{'value':'N/A'}, #Value Propositions
                'customfield_11852':{'value':'Urgent'}, #Time (Urgency)
                }
    if project == 'NGAC':
                 severity_jira_id = severity_jira_ids_prod[severity]
                 task_issue = {
                'project':{'key':project},
                'summary':f"Orca - {vul_title}",
                'description': '*Threat*\n' + f"{vul_description}" + \
                '\n*Issue Recommendation*\n' + f"{vul_solution}" + \
                '\n*Affected Assets added as CSV*\n',
                'issuetype': {'name': 'Bug'},
                'customfield_10262':{'value': 'Internal issue','id':'11774'}, #Issue source type
                'customfield_10079':[{'value':'Yes','id':'11087'}], #Security issue
                'customfield_11321':{'value':'Fraud Manager on Cloud(FMoC)','id':'25020'}, #Outseer Product
                'versions':[{'name':'Not Applicable'}], #version is ingested into existing version parameter
                'components':[{'name':'Other'}], #component is ingested into existing component parameter
                'customfield_11519':{'value':'Orca','id':'26129'}, #Security Tool
                'customfield_11086':{'value':severity,'id':severity_jira_id}, #Security Severity, defined at the top
                 }
                 Create_Issue_Jira(task_issue,csv_filename)
                 print("Created NGAC ticket")
                  
            


if __name__ == "__main__":
    #qualys_logout("ID")
    # Define the available options for the tool and Jira project dropdown menus
    tool_options = ['Qualys', 'Orca', 'PT']
    project_options = ['VMPX', 'TOP', 'PROD','NGAC']
    severity_options = ['informational','low','medium','high','critical']

    # Create the layout for the UI
    layout = [
        [sg.Text('Select the tool:')],
        [sg.Combo(tool_options, key='tool')],
        [sg.Text('Select the Severity:')],
        [sg.Combo(severity_options, key='severity')],
        [sg.Text('Select the Jira project:')],
        [sg.Combo(project_options, key='project')],
        [sg.Text('Enter issue IDs (comma-separated):')],
        [sg.InputText(key='issue_ids')],
        [sg.Button('Submit')]
    ]

    # Create the window
    window = sg.Window('My Application', layout)

    # Event loop to process UI events
    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break

        if event == 'Submit':
            # Extract the selected tool and Jira project values
            selected_tool = values['tool']
            selected_project = values['project']
            issue_ids = values['issue_ids']
            selected_severity = values['severity']

            if ',' in issue_ids:
                issue_ids = issue_ids.split(',')
            else:
                issue_ids = [issue_ids]
            # Call your existing functions with the selected values
            if selected_tool == 'Qualys':
                try:
                    cookies = qualys_auth()
                    for issueid in issue_ids:
                        qualys_issues(cookies["QualysSession"],issueid,selected_project)
                except Exception as e:
                    print("An error occured:",str(e))
                qualys_logout(cookies["QualysSession"])
            if selected_tool == 'Orca':
                try:
                    api_token_secret = os.environ.get("orca_api_token")
                    headers = {"Authorization": f"Token {api_token_secret}"}
                    for issueid in issue_ids:
                         orca_issues(headers,issueid,selected_project,selected_severity)
                except Exception as e:
                     print("An error occured:",str(e))

    
