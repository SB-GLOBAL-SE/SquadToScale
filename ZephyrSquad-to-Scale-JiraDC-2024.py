import requests
import sys
from requests.auth import HTTPBasicAuth
from requests.exceptions import Timeout
import json
import os
import time

# Record the start time
start_time = time.time()

# When triggering script pass values by: python3 script.py <username> <password> <project_key> <instance_url>
# For example in CLI: python ZephyrSquad-to-Scale-JiraDC-2024.py my_username my_password my_project_key https://example.com
if len(sys.argv) != 5:
    print("Usage: python3 script.py <username> <password> <project_key> <instance_url>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]
base_url = sys.argv[4]
mc_auth = HTTPBasicAuth(username, password)

project_key = project_key
base_url = base_url
query_url = f"{base_url}/rest/api/2/search?jql=project = {project_key} AND issuetype = Test"

default_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

issues_response = requests.request(
    "GET",
    query_url,
    headers=default_headers,
    auth=mc_auth
)


total = issues_response.json().get("total")
print(total)
startAt = 0

if total and total > 0:
    while startAt < total:
        inner_issue_response = requests.request(
            "GET",
            query_url,
            params={
              "maxResults": 100,
              "startAt": startAt
            },
            headers=default_headers,
            auth=mc_auth
        )
        
        counter = 0
        while inner_issue_response.status_code == 504 and counter < 600:
            inner_issue_response = requests.request(
                "GET",
                query_url,
                params={
                    "maxResults": 100,
                    "startAt": startAt
                },
                headers=default_headers,
                auth=mc_auth
            )
            counter = counter + 1
        
        if inner_issue_response.status_code == 200:
            output_file_path = "1.txt"
            response_content = inner_issue_response.text
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(response_content)
                
        else:
            print("Request failed with status code:", inner_issue_response.status_code)

        file_path = r"1.txt"
        output_file_path = r"2.txt"

        with open(file_path, 'r', encoding="utf-8") as file:
            json_data = json.load(file)

        parsed_data = []

        for issue in json_data["issues"]:
            projectKey = issue["fields"]["project"]["key"]
            ID = issue["id"]
            name = issue["fields"]["summary"]
            precondition = issue["key"]
            objective = issue["fields"]["description"]
            priority = issue["fields"]["priority"]["name"]
            priority = priority if priority else "No priority"
            WorkFlowStatus = issue["fields"]["status"]["name"]
            WorkFlowStatus = WorkFlowStatus if WorkFlowStatus else "No status"
            labels = issue["fields"]["labels"]
            owner = issue["fields"]["reporter"]["key"]
            issueLinks = issue["fields"]["issuelinks"]
            issueLinksList = [item['outwardIssue']['key'] if 'outwardIssue' in item else item['inwardIssue']['key'] for item in issueLinks if 'outwardIssue' in item or 'inwardIssue' in item]                                          
            priority_info = issue["fields"].get("priority")
            priority = priority_info["name"] if priority_info else "No priority"
            if "components" in issue["fields"]:
                components = issue["fields"]["components"]
                components_list = [component["name"].strip() for component in components]
                component_List_str = ", ".join(components_list)
                if components_list:
                    component_List_str = ", ".join(components_list)
                else:
                    component_List_str = "No Component"

            else:
                print("no components for issue")

           
            
            parsed_data.append({
                "projectKey": projectKey,
                "ID": ID,
                "name": name,
                "priority": priority,
                "objective": objective,
                "labels": labels,
                "owner" : owner,
                "precondition": precondition,
                "issueLinks" : issueLinksList, 
                "customFields": {
                    "components" : component_List_str,
                    "WorkFlowStatus" : WorkFlowStatus,
                    "SquadPriority" : priority

                    }
            })
            
           

        with open(output_file_path, 'w', encoding="utf-8") as output_file:
            json.dump(parsed_data, output_file, indent=4)

        print(f"Parsed data has been written to {output_file_path}")

        with open(output_file_path, 'r') as file:
            data = json.load(file)

        testcase_url = f"{base_url}/rest/atm/1.0/testcase"

        responses = []

        for item in data:
            project_key = item["projectKey"]
            name = item["name"]
            precondition = item["precondition"]
            objective = item["objective"]
            owner = item["owner"]
            issueLinks = item["issueLinks"]
            labels = item["labels"]
            priority = item["priority"]
            WorkFlowStatus = item["customFields"]["WorkFlowStatus"]                                   
            components = item["customFields"]["components"]
            
            payload = {
                "projectKey": project_key,
                "name": name,
                "objective": objective,
                "labels": labels,
                "owner": owner,
                "issueLinks": issueLinks,
                "precondition": precondition, 
                #"customFields": {
                #    "components" : components,
                #    "WorkFlowStatus" : WorkFlowStatus,
                #    "SquadPriority" : priority
                #    }    
                
            }
               

            testcase_response = requests.request(
                "POST",
                testcase_url,
                headers=default_headers,
                json=payload,
                auth=mc_auth
            )

            if testcase_response.status_code == 201:
                response_data = testcase_response.json()
                key = response_data.get("key")
                responses.append({"ID": item["ID"], "key": key})
                print(f"POST request for {item['ID']} successful!")
                print("Response content:", response_data)
            else:
                print(f"POST request for {item['ID']} failed with status code:", testcase_response.status_code)
                print("Response content:", testcase_response.text)
                print(payload)

        with open('2.5.txt', 'w', encoding="utf-8") as output_file:
            json.dump(responses, output_file, indent=2)
            print("Responses written to 2.5.txt")

        with open("2.5.txt", "r", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            key = item["key"]
            ID = item["ID"]
            teststep_url = f"{base_url}/rest/zapi/latest/teststep/{ID}"
            try:
                teststep_response = requests.request(
                    "GET",
                    teststep_url,
                    headers=default_headers,
                    auth=mc_auth
                )
                if teststep_response.status_code == 200:
                    response_content = teststep_response.text
                    output_file_path = "3.txt"
                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(response_content)
                    print("Response saved to", output_file_path)
                else:
                    print("Request failed with status code:", teststep_response.status_code)
                    print(teststep_url)
                    print(teststep_response)
            except requests.RequestException as e:
                print("An error occurred:", e)

            json_file_path = "3.txt"
            output_file_path = "4.txt"

            with open(json_file_path, "r", encoding="utf-8") as json_file:
                json_data = json_file.read()
            parsed_data = json.loads(json_data)

            step_data_pairs = []
            for step_entry in parsed_data["stepBeanCollection"]:
                step_data_pairs.append({
                    "step": step_entry["step"].strip(),
                    "data": step_entry["data"].strip(),
                    "result": step_entry["result"].strip()
                })
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                for pair in step_data_pairs:
                    output_file.write(json.dumps(pair) + "\n")
            print("Extracted data saved to", output_file_path)

            input_file_path = "4.txt"
            output_file_path = "5.txt"

            with open(input_file_path, "r", encoding="utf-8") as input_file:
                extracted_data = input_file.readlines()

                transformed_data = {
                    "testScript": {
                        "type": "STEP_BY_STEP",
                        "steps": []
                    }
                }

                for entry in extracted_data:
                    kvp = json.loads(entry)
                    step_description = kvp["step"]
                    data_description = kvp["data"]
                    result_description = kvp["result"]
                    step = {
                        "description": step_description.strip(".") + ".",
                        "testData": data_description.strip(".") + ".",
                        "expectedResult": result_description.strip(".") + "."
                    }
                    transformed_data["testScript"]["steps"].append(step)

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    json.dump(transformed_data, output_file, indent=2)
                print("Transformed data saved to", output_file_path)

            with open("2.5.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
                key = item["key"]
                ID = item["ID"]

                url = f"{base_url}/rest/atm/1.0/testcase/{key}"
                file_path = "5.txt"

                with open(file_path, "r", encoding="utf-8") as file:
                    payload_data = file.read()

                inner_testcase_response = requests.request(
                    "PUT",
                    url,
                    headers=default_headers,
                    data=payload_data,
                    auth=mc_auth
                )

                if inner_testcase_response.status_code == 200:
                    print("PUT request successful")
                else:
                    print("PUT request failed with status code:", inner_testcase_response.status_code)

        with open("2.5.txt", "r", encoding="utf-8") as file:
            data25 = json.load(file)

        for item in data25:
            key = item["key"]
            ID = item["ID"]

            url = f"{base_url}/rest/zapi/latest/execution?issueId={ID}"
            output_file_path = "6.txt"
            try:
                execution_respose = requests.request(
                    "GET",
                    url,
                    headers=default_headers,
                    auth=mc_auth
                )

                if execution_respose.status_code == 200:
                    response_content = execution_respose.text

                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(response_content)
                    print("Response saved to", output_file_path)
                else:
                    print("Request failed with status code:", execution_respose.status_code)
                    print(payload)
            except requests.RequestException as e:
                print("An error occurred:", e)

            with open("6.txt", "r", encoding="utf-8") as file:
                data6 = file.read()

            data_dict = json.loads(data6)
            key_value_pairs = []


#Status Mapping must match test case statuses that are in Squad. 
#The same test case statuses must be available in Scale. 
            status_mapping = {
                "1": "Pass",
                "2": "Fail",
                "3": "WIP",
                "4": "Blocked",
                "-1": "Unexecuted",
                "5": "Descoped",
                "6": "Not Delivered Yet",
                "7": "On Hold",
            }

            for execution in data_dict["executions"]:
                execution_status_id = execution["executionStatus"]
                execution_status = status_mapping.get(execution_status_id, "Unknown")
                executedBy = execution["createdBy"]
                versionName = execution["versionName"]
                ExecutionComment = execution["htmlComment"]
                cycleName = execution["cycleName"]
                if "executedOn" in execution: 
                    executedOn = execution["executedOn"]
                else:
                    executedOn = "None"
                if "assignedTo" in execution: 
                    AssignedTo_DisplayName = execution["assignedTo"]
                else:
                    AssignedTo_DisplayName = "None"
                    
                if "folderName" in execution:
                    folderName = execution["folderName"]
                else:
                    folderName = "None"                                 
                                                     

                key_value_pair = {
                    "status": execution_status,
                    "testCaseKey": key,
                    "executedBy" : executedBy,
                    "comment" : ExecutionComment,
                    "customFields": {
                    #"executedOn" : executedOn,
                    #"AssignedTo" : AssignedTo_DisplayName,   
                    #"Squadversion" :versionName,
                    #"SquadCycleName":cycleName,
                    #"folderName":folderName
                }                                                           
                }
                key_value_pairs.append(key_value_pair)

            with open("7.txt", "w", encoding="utf-8") as output_file:
                json.dump(key_value_pairs, output_file, indent=4)

            print("Data extracted and saved to '7.txt'.")

            payload = {
                "name": "Migrating Executions From Legacy Tool",
                "projectKey": f"{project_key}"
            }
            url = f"{base_url}/rest/atm/1.0/testrun"

            post_response = requests.request(
                "POST",
                url,
                headers=default_headers,
                json=payload,
                auth=mc_auth
            )

            if post_response.status_code == 201:
                data = post_response.json()
                cycleKey = data["key"]

                url = f"{base_url}/rest/atm/1.0/testrun/{cycleKey}/testresults"
                file_path = "7.txt"
                with open(file_path, "r", encoding="utf-8") as file:
                    payload_data = file.read()

                response = requests.request(
                    "POST",
                    url,
                    headers=default_headers,
                    data=payload_data,
                    auth=mc_auth
                )

                if response.status_code == 201:
                    print("Post request successful")
                elif response.status_code == 400 and b"Should be informed at least 1 test result" in response.content:
                    print("No Executions for Test Case")
                elif response.status_code == 400 and b"'The user was not found for field executedBy." in response.content:
                    print("ExecutedBy User Not Found in target system, reRun with ExecutedBy= Null")
                    # Rerun the request with ExecutedBy set to null
                    payload_data = payload_data.replace('"executedBy":', '"executedBy": null')
                    response_retry = requests.request(
                        "POST",
                        url,
                        headers=default_headers,
                        data=payload_data,
                        auth=mc_auth
                    )

                    if response_retry.status_code == 201:
                        print("Post request successful after retry with ExecutedBy = Null")
                    else:
                        print("POST request failed after retry with ExecutedBy = Null. Status code:", response_retry.status_code)
                        print(response_retry.content)
                else:
                    print("POST request failed with status code:", response.status_code)
                    print(response.content)

            else:
                print(f"Request failed with status code {post_response.status_code}")
        os.remove("1.txt")
        startAt = startAt + 100
        
"""
        with open("2.5.txt", "r", encoding="utf-8") as file:
            data = json.load(file)

        for item in data:
            key = item["key"]
            ID = item["ID"]
            url = f"{base_url}/rest/api/2/issue/{ID}"

            response = requests.get(url, auth=mc_auth)
            if response.status_code == 200:
                data_dict = json.loads(response.content)
                attachments = data_dict['fields'].get('attachment', [])

                if attachments:
                    for i in range(len(attachments)):
                        attachmentsURL = attachments[i-1]['content']
                        attachmentName = attachments[i-1]['filename']
                        current_directory = os.getcwd()

                        url = attachmentsURL

                        # Define the output file path in the current directory
                        output_file_path = os.path.join(current_directory, attachmentName)

                        mc_auth = HTTPBasicAuth(username, password)


                        response = requests.get(url, auth=mc_auth)

                        if response.status_code == 200:
                            with open(output_file_path, 'wb') as f:
                                f.write(response.content)
                        else:
                            print(key)
                            print(payload)

                        testCaseKey = key

                        url = f"{base_url}/rest/atm/1.0/testcase/{testCaseKey}/attachments"

                        # Get the absolute path to the file
                        file_path = os.path.abspath(attachmentName)

                        files = {'file': (attachmentName, open(file_path, 'rb'), 'application/octet-stream')}
                        mc_auth = HTTPBasicAuth("username", "password")

                        response = requests.post(url, auth=mc_auth, files=files)
                        print(f"Attachment posted successfully for {key}")

                else:
                    print(f"No attachments found for issue {key}")
            else:
                print(f"Failed to fetch data for issue {key}. Status code: {response.status_code}")
"""
        
# Record the end time
end_time = time.time()

# Calculate the elapsed time'[]
elapsed_time = end_time - start_time

# Print the start time, end time, and elapsed time
print(f"Start Time: {start_time}")
print(f"End Time: {end_time}")
print(f"Elapsed Time: {elapsed_time} seconds")
