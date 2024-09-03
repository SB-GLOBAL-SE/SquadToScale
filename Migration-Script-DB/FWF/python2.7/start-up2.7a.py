import sys
import requests
from requests.auth import HTTPBasicAuth
import json
import os

# Clear error.txt if it exists from a previous run
if os.path.exists("error.txt"):
    os.remove("error.txt")

# python2 start-up2.7a.py matthew.bonner password MIGB 10024 https://next-jira-8-postgres.qa.tm4j-server.smartbear.io 
if len(sys.argv) != 6:
    print("Usage: python combined_script.py <username> <password> <project_key> <projectID> <instance_url>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]
project_Id = sys.argv[4]
base_url = sys.argv[5]
mc_auth = HTTPBasicAuth(username, password)

# Start of SCRIPT 1 logic
try:
    with open('app.properties', 'r') as file:
        for line in file:
            if line.startswith('host'):
                instance_url = line.split('=', 1)[1].strip()
                break

    query_url = "{}/rest/api/2/search?jql=project = {} AND issuetype = Test &maxResults=1".format(base_url, project_key)
    default_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    issues_response = requests.get(query_url, headers=default_headers, auth=mc_auth)

    if issues_response.status_code == 200:
        response_data = issues_response.json()

        # Check if there are issues in the response
        if "issues" in response_data and response_data["issues"]:
            first_issue = response_data["issues"][0]

            project_id = first_issue["fields"]["project"]["id"]

            print("ID={}".format(project_id))
            print("baseURL={}".format(base_url))

        else:
            print("No issues found in the response.")
            sys.exit(1)
    else:
        with open("error.txt", "w") as error_file:
            error_file.write("Error: {} - {}\n".format(issues_response.status_code, issues_response.text))
        print("Error: {} - {}\nError details saved to error.txt".format(issues_response.status_code, issues_response.text))
        sys.exit(1)

    PostStatusURL = "{}/rest/tests/1.0/testresultstatus".format(base_url)

    status_list = [
        {
            "name": "Descoped",
            "description": "Description for Descoped",
            "color": "#9900ff"
        },
        {
            "name": "Not Delivered Yet",
            "description": "Description for Retested",
            "color": "#ff9966"
        },
        {
            "name": "WIP",
            "description": "Description for WIP",
            "color": "#ff9965"
        }
    ]

    # Set the environment variables before the loop
    os.environ['MIGRATION_ID'] = str(project_id)
    os.environ['MIGRATION_BASE_URL'] = base_url

    # Iterate through the status_list and send request to create new status.
    for index, status_details in enumerate(status_list):
        payload = {
            "projectId": int(project_id),
            "name": status_details["name"],
            "description": status_details["description"],
            "color": status_details["color"],
            "index": index,
            "items": []
        }

        response = requests.post(PostStatusURL, data=json.dumps(payload), headers=default_headers, auth=mc_auth)

        if response.status_code == 200:
            print("Status {} posted successfully.".format(index))
        else:
            with open("error.txt", "a") as error_file:
                error_file.write("Error posting status {}: {} - {}\n".format(index, response.status_code, response.text))
            print("Error posting status {}. Error details saved to error.txt".format(index))
            sys.exit(1)

except Exception as e:
    print("An unexpected error occurred during SCRIPT 1 execution: {}".format(str(e)))
    sys.exit(1)

# End of SCRIPT 1 logic

# Start of SCRIPT 2 logic
try:
    query_url = "{}/rest/api/2/priority".format(base_url)
    issues_response = requests.get(query_url, headers=default_headers, auth=mc_auth)

    if issues_response.status_code == 200:
        with open("priority_data.txt", "w") as file:
            file.write(issues_response.text)

        with open("priority_data.txt", "r") as file:
            json_data = json.load(file)

        names = []
        ids = []
        descriptions = []
        colors = []

        for item in json_data:
            names.append(item["name"])
            ids.append(item["id"])
            descriptions.append(item.get("description", ""))
            colors.append(item.get("statusColor", ""))

        PostStatusURL = "{}/rest/tests/1.0/testcasepriority".format(base_url)
        n = 0

        for i in range(len(names)):
            # Check if the priority name should be ignored
            if names[i].lower() in ["highest", "high", "medium", "low", "lowest"]:
                print("Skipping priority '{}' as it is on the ignore list.".format(names[i]))
                continue

            payload = {
                "projectId": int(project_Id),
                "name": names[i],
                "description": descriptions[i],
                "color": colors[i],
                "index": int(ids[i]),
                "items": []
            }

            response = requests.post(PostStatusURL, data=json.dumps(payload), headers=default_headers, auth=mc_auth)

            if response.status_code == 200:
                print("Status {} posted successfully.".format(names[i]))
                n = n + 1
            else:
                with open("error.txt", "a") as error_file:
                    error_file.write("Error: {} - {}\n".format(response.status_code, response.text))
                print("Error details saved to error.txt")

    else:
        with open("error.txt", "w") as error_file:
            error_file.write("Error: {} - {}".format(issues_response.status_code, issues_response.text))
        print("Error: {} - {}\nError details saved to error.txt".format(issues_response.status_code, issues_response.text))

except Exception as e:
    print("An unexpected error occurred during SCRIPT 2 execution: {}".format(str(e)))
    sys.exit(1)

# End of SCRIPT 2 logic
