import requests
from requests.auth import HTTPBasicAuth
import sys

if len(sys.argv) != 5:
    print("Usage: python3 clean-up.py <ID> <baseURL> <username> <password>")
    sys.exit(1)

# Extract arguments from command-line
ID = sys.argv[1]
baseURL = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]

# URL to send the GET request to
url = f"{baseURL}/rest/tests/1.0/testresultstatus?projectId={ID}"

# Set up authentication
auth = HTTPBasicAuth(username, password)

# Send the GET request
response = requests.get(url, auth=auth)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the JSON response content
    response_content = response.json()

    # Initialize a variable to store the ID
    not_delivered_yet_id = None

    # Search for the entry with the name "Not Delivered Yet"
    for item in response_content:
        if item["name"] == "Not Delivered Yet":
            not_delivered_yet_id = item["id"]
            break

    # Check if the ID was found and print it
    if not_delivered_yet_id is not None:
        print(f"The ID for 'Not Delivered Yet' is: {not_delivered_yet_id}")
        
        update_url = f"{baseURL}/rest/tests/1.0/testresultstatus/{not_delivered_yet_id}"

        # Payload to send with the PUT request
        payload = {
            "id": not_delivered_yet_id,
            "projectId": int(ID),
            "name": "Retested"
        }

        # Set up headers
        headers = {
            "Content-Type": "application/json"
        }

        # Send the PUT request
        update_response = requests.put(update_url, json=payload, headers=headers, auth=auth)

        # Check if the request was successful (status code 200)
        if update_response.status_code == 200:
            print("Status updated successfully.")
        else:
            # Print the error details if the request was unsuccessful
            print(f"Error: {update_response.status_code} - {update_response.text}")

    else:
        print("The status 'Not Delivered Yet' was not found in the response.")

else:
    # Print the error details if the request was unsuccessful
    print(f"Error: {response.status_code} - {response.text}")
