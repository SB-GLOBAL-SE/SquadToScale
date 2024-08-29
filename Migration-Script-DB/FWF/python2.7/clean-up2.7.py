import requests
from requests.auth import HTTPBasicAuth
import sys

if len(sys.argv) != 5:
    print("Usage: python clean-up.py <ID> <baseURL> <username> <password>")
    sys.exit(1)

ID = sys.argv[1]
baseURL = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]

url = "{}/rest/tests/1.0/testresultstatus?projectId={}".format(baseURL, ID)

auth = HTTPBasicAuth(username, password)

response = requests.get(url, auth=auth)

if response.status_code == 200:
    response_content = response.json()

    not_delivered_yet_id = None

    # Search for the entry with the name "Not Delivered Yet"
    for item in response_content:
        if item["name"] == "Not Delivered Yet":
            not_delivered_yet_id = item["id"]
            break

    # Check if the ID was found and print it
    if not_delivered_yet_id is not None:
        print("The ID for 'Not Delivered Yet' is: {}".format(not_delivered_yet_id))
        
        update_url = "{}/rest/tests/1.0/testresultstatus/{}".format(baseURL, not_delivered_yet_id)

        payload = {
            "id": not_delivered_yet_id,
            "projectId": int(ID),
            "name": "Retested"
        }

        headers = {
            "Content-Type": "application/json"
        }

        update_response = requests.put(update_url, json=payload, headers=headers, auth=auth)

        if update_response.status_code == 200:
            print("Status updated successfully.")
        else:
            print("Error: {} - {}".format(update_response.status_code, update_response.text))

    else:
        print("The status 'Not Delivered Yet' was not found in the response.")

else:
    print("Error: {} - {}".format(response.status_code, response.text))
