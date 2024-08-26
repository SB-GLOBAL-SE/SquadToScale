import sys
import subprocess

# 2 parameters you must modify.
# Jar file name/version you are migrating with
jar_file_name = 'app-migration-zephyr-1.0.6-SNAPSHOT-jar-with-dependencies.jar'
# Jira DB name
db_name = 'jira'

#Name of start up script 
migrate_statuses = 'start-up.py'
#Name of clean up script
clean_up = 'clean-up.py'

if len(sys.argv) != 4:
    print("Usage: python3 main5.py <username> <password> <project_key>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]

def get_DB_user():
    DB_user = None
    with open('database.properties', 'r') as file:
        for line in file:
            if 'datasource.username' in line:
                DB_user = line.split('=', 1)[1].strip()
                break
    if DB_user is None:
        print("Error: datasource.username not found in database.properties")
        sys.exit(1)
    return DB_user

def execute_query(DB_user, db_name):
    command = [
        "psql", "-U", DB_user, "-d", db_name, "-c",
        r"\COPY public.\"AO_4D28DD_ATTACHMENT\" "
        r"(\"FILE_NAME\",\"FILE_SIZE\",\"NAME\",\"PROJECT_ID\",\"USER_KEY\",\"TEMPORARY\","
        r"\"CREATED_ON\",\"MIME_TYPE\",\"TEST_CASE_ID\",\"STEP_ID\",\"TEST_RESULT_ID\") "
        r"FROM '/var/atlassian/application-data/jira/SquadToScale-10601/AO_4D28DD_ATTACHMENT.csv' "
        r"WITH (FORMAT csv, HEADER true);"
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("Database query executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Database query failed to execute.")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def trigger_script(script_name, *args):
    print(f"Starting {script_name} with arguments {args}...")
    try:
        result = subprocess.run(
            ['python3', script_name, *args],
            check=True, capture_output=True, text=True
        )
        print(f"Script {script_name} executed successfully.")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Script {script_name} failed to execute.")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def trigger_jar(jar_file_name, username, password, project_key):
    print(f"Starting {jar_file_name}...")
    try:
        result = subprocess.run(
            ['java', '-jar', jar_file_name, username, password, project_key],
            capture_output=True, text=True
        )
        if "Failed to execute the migration" in result.stdout:
            print(f"JAR file {jar_file_name} failed to execute.")
            print(f"Error: Review app.log for more information.")
            sys.exit(1)
        elif result.returncode != 0:
            print(f"JAR file {jar_file_name} failed with return code {result.returncode}. Review app.log for more information.")
            sys.exit(result.returncode)
        else:
            print(f"JAR file {jar_file_name} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"JAR file {jar_file_name} failed to execute due to an error.")
        print(f"Error: {e.stderr}")
        sys.exit(1)

DB_user = get_DB_user()

output = trigger_script(migrate_statuses, username, password, project_key)

ID = None
baseURL = None
for line in output.splitlines():
    if line.startswith("ID="):
        ID = line.split("=", 1)[1].strip()
    elif line.startswith("baseURL="):
        baseURL = line.split("=", 1)[1].strip()

if ID and baseURL:
    trigger_jar(jar_file_name, username, password, project_key)

    trigger_script(clean_up, ID, baseURL, username, password)

    execute_query(DB_user, db_name)

    print("All processes completed successfully.")
else:
    print("Failed to capture ID and baseURL from migrate statuses script.")
    sys.exit(1)
