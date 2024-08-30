import sys
import os
import subprocess

# 2 parameters you must modify.
# Jar file name/version you are migrating with
jar_file_name = 'app-migration-zephyr-1.0.6-SNAPSHOT-jar-with-dependencies.jar'
# Jira DB name
db_name = 'jira'

# Name of start-up script 
migrate_statuses = 'start-up2.7.py'
# Name of clean-up script
clean_up = 'clean-up2.7.py'

if len(sys.argv) != 4:
    print("Usage: python main5.py <username> <password> <project_key>")
    sys.exit(1)

username = sys.argv[1]
password = sys.argv[2]
project_key = sys.argv[3]

def get_DB_credentials():
    DB_user = None
    DB_password = None
    with open('database.properties', 'r') as file:
        for line in file:
            if 'postgresql.datasource.username' in line:
                DB_user = line.split('=', 1)[1].strip()
            elif 'postgresql.datasource.password' in line:
                DB_password = line.split('=', 1)[1].strip()
            if DB_user and DB_password:
                break

    if DB_user is None:
        print("Error: postgresql.datasource.username not found in database.properties")
        sys.exit(1)
        
    if DB_password is None:
        print("Error: postgresql.datasource.password not found in database.properties")
        sys.exit(1)

    return DB_user, DB_password

def execute_query(DB_user, DB_password, db_name):
    os.environ['PGPASSWORD'] = DB_password
    command = [
        "psql", "-U", DB_user, "-d", db_name, "-c",
        r"\COPY public.\"AO_4D28DD_ATTACHMENT\" "
        r"(\"FILE_NAME\",\"FILE_SIZE\",\"NAME\",\"PROJECT_ID\",\"USER_KEY\",\"TEMPORARY\","
        r"\"CREATED_ON\",\"MIME_TYPE\",\"TEST_CASE_ID\",\"STEP_ID\",\"TEST_RESULT_ID\") "
        r"FROM '/var/atlassian/application-data/jira/SquadToScale-10601/AO_4D28DD_ATTACHMENT.csv' "
        r"WITH (FORMAT csv, HEADER true);"
    ]
    try:
        subprocess.check_call(command)
        print("Database query executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Database query failed to execute.")
        print("Error: {}".format(e))
        sys.exit(1)
    finally:
        os.environ.pop('PGPASSWORD')

def trigger_script(script_name, *args):
    print("Starting {} with arguments {}...".format(script_name, args))
    try:
        result = subprocess.check_output(
            ['python', script_name] + list(args),
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print("Script {} executed successfully.".format(script_name))
        return result.strip()
    except subprocess.CalledProcessError as e:
        print("Script {} failed to execute.".format(script_name))
        print("Error: {}".format(e.output))
        sys.exit(1)

def trigger_jar(jar_file_name, username, password, project_key):
    # Get the absolute path of the JAR file
    jar_file_path = os.path.abspath(jar_file_name)
    
    print("Starting {}...".format(jar_file_name))
    print("Executing JAR file in directory: {}".format(jar_file_path))
    
    try:
        result = subprocess.check_output(
            ['java', '-jar', jar_file_name, username, password, project_key],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        if "Failed to execute the migrations" in result:
            print("JAR file {} failed to execute.".format(jar_file_name))
            print("Error: Review app.log for more information.")
            sys.exit(1)
        print("JAR file {} executed successfully.".format(jar_file_name))
    except subprocess.CalledProcessError as e:
        print("JAR file {} failed to execute due to an error.".format(jar_file_name))
        print("Error: {}".format(e.output))
        sys.exit(1)
    except OSError as e:
        print("JAR file {} could not be found or executed.".format(jar_file_name))
        print("Error: {}".format(e))
        sys.exit(1)

DB_user, DB_password = get_DB_credentials()

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

    execute_query(DB_user, DB_password, "jira")

    print("All processes completed successfully.")
else:
    print("Failed to capture ID and baseURL from migrate statuses script.")
    sys.exit(1)
