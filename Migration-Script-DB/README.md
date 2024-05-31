# Squad to Scale Migration Script

This script executes a Migration From Zephyr Squad to Zephyr Scale on Server or Data Center, with both apps on the same Jira instance.
It uses Jira, Squad and Scale APIs to read and insert entities. It also executes some queries on Zephyr Scale Database
to fetch complementary data to help the migration. This migration will COPY data from Zephyr Squad to Zephyr Scale. 

<!-- TOC -->

* [Squad to Scale Migration Script](#squad-to-scale-migration-script)
    * [What is currently migrated](#what-is-currently-migrated)
    * [Properties setup](#properties-setup)
        * [app.properties](#appproperties)
        * [database.properties](#databaseproperties)
    * [Execution](#execution)
        * [Steps](#steps)
      

<!-- TOC -->

## What is currently migrated

The following Zephyr Squad Entities are migrated to Zephyr Scale:

- Test Cases
   - Zephyr Squad Test Cases are mapped 1 to 1 to Zephyr Scale Test Cases.    
- Test Steps
   - Zephyr Squad Test Steps are mapped 1 to 1 to Zephyr Scale Test Steps, on the associated Test Case. 
- Cycles
   - Zephyr Squad Test Cycles are mapped 1 to 1 to Zephyr Scale Test Cycles. 
- Test Executions
   - Zephyr Squad Test Executions are mapped 1 to 1 to Zephyr Scale Test Executions. 
- Attachments for Test Cases, Steps and Executions

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

1. Move the JAR file alongside both `app.properties` and `database.properties` (already configured) to the machine
   holding Jira instance
2. Execute the JAR in the command
   line: `java -jar squadToScale.jar <jira_api_username> <jira_api_password> [PROJECT KEY]`
3. Wait for it to finish. The process will print several logs on the screen where you can check its progress. It will
   also generate a `app.log` file with te logs being generated
4. If successful, a csv file will be generated with the name configured in `app.properties`
   field  `attachmentsMappedCsvFile`.
5. Import this csv file into Zephyr Scale Table `AO_4D28DD_ATTACHMENT`
