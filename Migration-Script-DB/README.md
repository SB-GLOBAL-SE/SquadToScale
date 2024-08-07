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


## Runbook


### Migration Guide to Migrate Zephyr Squad to Zephyr Scale on Jira Data Center

#### Step 1: Preparation
1. **Backup Your Data:**
   - Ensure a complete backup of your Jira and Zephyr Squad data to prevent data loss during migration.

#### Step 2: Setting Up Your Environment

 **Installing Necessary Applications**
1. **Install Git:**
   - Visit [git-scm.com](https://git-scm.com) to download and install Git for your operating system.

2. **Install Java 17:**
   - Download Java 17 from [Oracle’s JDK Downloads](https://www.oracle.com/java/technologies/javase-jdk17-downloads.html) or [AdoptOpenJDK](https://adoptium.net/).
   - Follow the installation instructions and ensure Java is added to your system’s PATH. Verify the installation by running `java -version` and `javac -version` in your command line.

 **Cloning the Repository**
1. **Clone the Repository:**
   - Run the following command in a terminal clone the repository:
     ```bash
     git clone https://github.com/matthewrbonner/SquadToScale.git
     ```
   - Navigate to the cloned repository:
     ```bash
     cd SquadToScale
     ```

#### Step 3: Configuration 

1. **Edit the Configuration Files:**
   - Edit configuration files (e.g., `app.properties` and `database.properties`) in the `SquadToScale` directory.
   - Add the following details to the configuration file:
     ```app.properties
      host=https://your-jira-instance.atlassian.net
      parallelBatchSize=100
      attachmentsMappedCsvFile=AO_4D28DD_ATTACHMENT.csv
      database=postgresql
      attachmentsBaseFolder=/home/ubuntu/jira/data/attachments/
     ```

     ```database.properties
      postgresql.datasource.url=jdbc:postgresql://localhost:5432/jira
      postgresql.datasource.driver.class.name=org.postgresql.Driver
      postgresql.datasource.username=username
      postgresql.datasource.password=password
     ```

**How to determine host, database.url, and username/password**

#### 1. **Determine Attachments Base Folder**

To locate the base folder where Jira stores attachments:

1. Navigate to the `<JIRA_INSTALLATION_DIRECTORY>/jira-home` or `<JIRA_HOME>` directory.
2. Look for the `attachments` folder within this directory. This folder contains all Jira attachments by default unless a custom location is configured.
3. If a custom location is used, you can verify it by checking the `jira-config.properties` file or the Administration settings within Jira.

#### 2. **Determine Jira Base URL**

To find the base URL that Jira uses:

1. Log in to Jira as an administrator.
2. Go to **Administration** > **System** > **General Configuration**.
3. Look for the **Base URL** setting. This is the URL that Jira uses to generate links and references.

#### 3. **Determine Database URL, Username, and Password**

To find the database URL, username, and password:

1. Locate the `dbconfig.xml` file in the `<JIRA_HOME>` directory.
2. Open the `dbconfig.xml` file to view the database connection details.
3. The following tags within the `dbconfig.xml` file will provide the information:

   - **Database URL:**
     ```xml
     <url>jdbc:<DB_TYPE>://<DB_HOST>:<DB_PORT>/<DB_NAME></url>
     ```
   - **Database Username:**
     ```xml
     <username>your_db_username</username>
     ```
   - **Database Password:**
     ```xml
     <password>your_db_password</password>
     ```

#### Example Database URLs for Different Databases:

- **PostgreSQL:**
  ```xml
  <url>jdbc:postgresql://<DB_HOST>:<DB_PORT>/<DB_NAME></url>
  ```

- **MySQL:**
  ```xml
  <url>jdbc:mysql://<DB_HOST>:<DB_PORT>/<DB_NAME>?useUnicode=true&amp;characterEncoding=utf8</url>
  ```

- **Oracle:**
  ```xml
  <url>jdbc:oracle:thin:@<DB_HOST>:<DB_PORT>:<DB_NAME></url>
  ```

- **SQL Server:**
  ```xml
  <url>jdbc:sqlserver://<DB_HOST>:<DB_PORT>;databaseName=<DB_NAME></url>
  ```

**Note:**
Ensure that you have access to the server where Jira is installed, as these files and configurations are only accessible from the filesystem where Jira is running.


#### Step 4: Runtime 

1. **Run the Java Program:**

   - Run the compiled program:
     ```bash
     java -jar app-migration-zephyr-1.0.6-SNAPSHOT-jar-with-dependencies.jar <jira_api_username> <jira_api_password> [PROJECT KEY]
     ```

2. **Import Attachments CSV into the Database:**
   - Import the generated attachments CSV into the Zephyr Scale Table `AO_4D28DD_ATTACHMENT` table.
      IE:
     ```bash
      psql -U postgres -d jira -c "\COPY public.\"AO_4D28DD_ATTACHMENT\" (\"FILE_NAME\",\"FILE_SIZE\",\"NAME\",\"PROJECT_ID\",\"USER_KEY\",\"TEMPORARY\",\"CREATED_ON\",\"MIME_TYPE\",\"TEST_CASE_ID\",\"STEP_ID\",\"TEST_RESULT_ID\") FROM /AO_4D28DD_ATTACHMENT.csv delimiter ',' CSV HEADER"
     ```
      



