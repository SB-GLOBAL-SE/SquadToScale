# Squad to Scale Migration Script

This is a full workflow of the previous directory. If you trigger main.py it will execute the migration, and the CSV import into the DB. You still need to modify database.properties, and app.properties to be correct. 

## Properties setup

### app.properties

| Fields                   | Used For                                                                                                    |
|--------------------------|-------------------------------------------------------------------------------------------------------------|
| host                     | Public address of Jira Instance                                                                             |
| parallelBatchSize        | How many Test Cases are processed per batch. Default is 100                                                 |
| attachmentsMappedCsvFile | The name of the resulting csv generated during the migration                                                |
| database                 | Name of the database used in the instance. Supported values are `postgresql`, `oracle`, `mssql` and `mysql` |
| attachmentsBaseFolder    | Where the attachments are located in the Instance Machine                                                   | 

Example:

```
host=https://linux-60489.prod.atl-cd.net
parallelBatchSize=100
attachmentsMappedCsvFile=AO_4D28DD_ATTACHMENT.csv
database=postgresql
attachmentsBaseFolder=/home/ubuntu/jira/data/attachments/
```

### database.properties

| Fields                                       | Used for                                         |
|----------------------------------------------|--------------------------------------------------|
| <database type>.datasource.url               | Database url to access it                        |
| <database type>.datasource.driver.class.name | Database Driver. **You don't have to modify it** |
| <database type>.datasource.username          | database `username`                              |
| <database type>.datasource.password          | database `password`                              |

Example:

```
postgresql.datasource.url=jdbc:postgresql://localhost:5432/jira
postgresql.datasource.driver.class.name=org.postgresql.Driver
postgresql.datasource.username=some_username
postgresql.datasource.password=some_password
```

## Execution

The script has two different executions modes:

1. If you define a project key, it will migrate only the indicated project
2. If no project key is defined, it will run for all Zephyr Squad projects

### Steps

1. Move the JAR file alongside both configured properties file `app.properties`,  `database.properties` and the python scripts scripts `start-up.py`, `clean-up.py` and `main.py` to the same directory on the machine.
   holding Jira instance. 

   Configure `main.py` - It requires 2 parameters to be modified before you execute:

   `jar_file_name` is the version of the migration utility you are using. The migration utility needs to be in the same directory as main.py
   IE:
   `jar_file_name` = 'app-migration-zephyr-1.0.6-SNAPSHOT-jar-with-dependencies.jar'

   `db_name` is the Jira Database name that contains the jira specific information. Unless previously changed, expect that db_name = Jira. 
   IE:
   `db_name` = 'Jira'   

2. Execute the main.py in the command on a local Jira node.
   line: `pyton3 main.py Jira-Username Jira-Password Jira-Project-Key`

3. Wait for it to finish. The process will print several logs on the screen where you can check its progress. It will
   also generate a `app.log` file with te logs being generated

4. If every event is successful, a log will output 'All processes completed successfully.'

