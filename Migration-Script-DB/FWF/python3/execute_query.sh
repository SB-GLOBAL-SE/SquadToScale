#!/bin/bash

DB_USER=$1
DB_NAME=$2

# Command to run the \COPY statement
psql -U $DB_USER -d $DB_NAME <<EOF
\COPY "AO_4D28DD_ATTACHMENT" (
  "FILE_NAME","FILE_SIZE","NAME","PROJECT_ID","USER_KEY","TEMPORARY",
  "CREATED_ON","MIME_TYPE","TEST_CASE_ID","STEP_ID","TEST_RESULT_ID"
) 
FROM '/var/atlassian/application-data/jira/SquadToScale-10601/AO_4D28DD_ATTACHMENT.csv' 
WITH (FORMAT csv, HEADER true);
EOF

# Check if the command was successful
if [ $? -eq 0 ]; then
  echo "Database query executed successfully."
else
  echo "Database query failed."
  exit 1
fi
