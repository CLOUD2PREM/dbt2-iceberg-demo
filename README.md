# dbt2-iceberg-demo
Iceberg with Postgres Seamless Data Integration

This project creates a data pipeline. It uses Airflow to manage ETL processes between different databases through Trino. The pipeline also uses MinIO as storage for Apache Iceberg and PostgreSQL for handling database tasks. Airflow helps by automating and scheduling the workflows. MariaDB works as the backend for the Hive Metastore. The Hive Metastore organizes and manages Iceberg tables. This makes it easy to manage and access the data. Additionally, dbt is used to add raw data into PostgreSQL. It uses the dbt seed command to load CSV files. This makes it easy to put raw data into PostgreSQL, which is then transformed and connected to Iceberg for better data analysis. The documentation also includes details about the software versions and tools used in the project.

![image](https://github.com/user-attachments/assets/02ff6958-7487-44a8-b26f-cb1ca5bda630)

# 🛠️ Environment Setup
### System and Software Versions

| Software         | Description                                    | Version                             | UI - Ports      |
|------------------|------------------------------------------------|-------------------------------------|------------|
| **WSL**          | Windows Subsystem for Linux environment         | Ubuntu 22.04 (Distro 2)             |            |
| **Docker**       | Containerization platform                      | Docker version 27.2.0               |            |
| **Docker Compose**| Tool for defining and running multi-container Docker applications | v2.29.2-desktop.2 |            |
| **Postgres**     | Open-source relational database                 | postgres:16                         |            |
| **Trino**        | Distributed SQL query engine                    | trino:457                           | 8080       |
| **Iceberg**      | High-performance table format for big data      | 1.6.1                               |            |
| **Python**       | Programming language                           | 3.10.12                             |            |
| **Airflow**      | Workflow automation and scheduling tool         | 2.10.1                              | 9090       |
| **Mariadb**      | Open-source relational database                 | 10.5.8                              |            |
| **Minio**        | Object storage server compatible with AWS S3    | RELEASE.2023-08-23T10-07-06Z        | 9000       |
| **HADOOP**       | Framework for distributed storage and processing| 3.2.0                               |            |
| **HIVE-METASTORE**    | Metadata management service for Hive            | 3.1.3                               |            |
| **DBT**          | Data build tool for transforming data in the warehouse | 1.8.7                          |            |


# 🛠️ How to Start The Project

1. Clone the project.
```plaintext
git clone https://github.com/CLOUD2PREM/dbt2-iceberg-demo.git
```

2. Create Docker network:
```plaintext
docker network create --subnet=172.80.0.0/16 dahbest
```

3. Check the .ENV file:
```plaintext
You can change your container username and password in .ENV file.
```

4. ⚠️ Grant permission to the Airflow logs and DBT folder:
```plaintext
sudo chmod 777 -R ../dbt2-iceberg-demo
```

5. Start the containers.
```plaintext
docker-compose up -d --build
```

⚠️ If you get any error: you can run `check_files.sh`
```plaintext
./check_files.sh
```

# ⚠️ Iceberg Connection Information:
If you want to change your Iceberg connection information. 
Iceberg: Please check the `docker-compose.yaml` and `trino` ==> `catalog` ==> `jaffle_shop_iceberg.properties` files:
```plaintext
connector.name=iceberg
iceberg.catalog.type=hive_metastore
hive.metastore.uri=thrift://hive-metastore:9083
hive.metastore.authentication.type=NONE
hive.s3.path-style-access=true
hive.s3.endpoint=http://minio:9000
hive.s3.region=us-east-1
hive.s3.aws-access-key=cTI5BM9ecjv6qISgGaHP
hive.s3.aws-secret-key=gJslk7jC1IJqOpDAVoV0fPXFS0WKDcSX9zBGd3f1
```

Postgres: Please check the `docker-compose.yaml` and `trino` ==> `catalog` ==> `jaffle_shop_postgres.properties` files:
```plaintext
connector.name=postgresql
connection-url=jdbc:postgresql://172.80.0.10:5432/jaffle_shop_postgres
connection-user=cagri
connection-password=3541
```

# 🐳 Container Setup:
### Airflow -> Trino Connection:
⚠️ Go to the Airflow UI and navigate to the Connections panel. Then, configure the following settings:
```plaintext
Connection Id * = trino_conn
Connection Type * = Trino (ensure the Airflow module is installed)
Host = 172.80.0.80
Login = cagri
Port = 8080
```

If you want to create new a DBT project, make sure to use in dbt folder:
```plaintext
dbt init <project_name>
⚠️ Don't delete the `dbt/profiles.yml` file. When you create a new DBT project, DBT automatically creates a `profiles.yml` file in `~/.dbt/profiles.yml`. In this project, DBT runs in the Airflow container, and I have set the `~/.dbt/profiles` path to `/opt/dbt`. Make sure to add your new settings to the `dbt/profiles.yml` file located in `/opt/dbt`.
```

Edit the profiles.yml file:
Here’s an example of a profiles.yml file for Trino and Postgres
nano <your_project_folder>/dbt/profiles.yml
```plaintext
jaffle_shop_iceberg:
  outputs:
    dev:
      type: trino
      host: 172.80.0.80
      port: 8080
      user: cagri
      catalog: jaffle_shop_iceberg
      schema: jaffle_shop_sc
  target: dev

jaffle_shop_postgres:
  outputs:
    dev:
      type: postgres
      host: 172.80.0.10
      port: 5432
      user: cagri
      password: '3541'
      dbname: jaffle_shop_postgres
      schema: jaffle_shop_sc
  target: dev
```

4. you can use dbt run command like this:
```plaintext
dbt run --profile jaffle_shop_iceberg
dbt run --profile jaffle_shop_postgres
```

# How to Run The Project
## full_dag.py High Level Steps
### 1. Creating Schemas for Postgres and Iceberg With Trino (Lines 23-39)
We'll create two schemas for our ETL pipeline:
1. **Postgres Schema**: This is a simple schema creation using an SQL query.
```plaintext
  create_schema_postgres = SQLExecuteQueryOperator(
      task_id='Create_postgres_schema',
      conn_id='trino_conn',
      sql="""
      CREATE SCHEMA IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc
      """,
      autocommit=True
  )
```
2. **Iceberg Schema**: This will create the schema in our lakehouse bucket.
```plaintext
    create_schema_iceberg = SQLExecuteQueryOperator(
        task_id='Create_iceberg_schema',
        conn_id='trino_conn',
        sql="""
        CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc 
        WITH (location = 's3a://lakehouse/jaffle_shop_sc')
        """,
        autocommit=True
    )
```

### 2. Create Tables for Postgres and Iceberg with Trino (41-126 Lines)
We'll create six tables for our ETL pipeline because we have three raw datasets. First, we insert raw data into Postgres, and then into Iceberg tables.
1. **Postgres Tables**: We use simple SQL queries to create the Postgres tables.
```plaintext
  create_clean_postgres_customers = SQLExecuteQueryOperator(
      task_id='create_postgres_customers_table',
      conn_id='trino_conn',
      sql="""
          CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_customers (
              id INTEGER, 
              first_name VARCHAR(50), 
              last_name VARCHAR(50), 
              email VARCHAR(50)
          )
      """,
  )

  create_clean_postgres_orders = SQLExecuteQueryOperator(
      task_id='create_postgres_orders_table',
      conn_id='trino_conn',
      sql="""
          CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_orders (
              id INTEGER, 
              user_id INTEGER, 
              order_date TIMESTAMP, 
              status VARCHAR(50)
          )
      """,
  )

    create_clean_postgres_payments = SQLExecuteQueryOperator(
        task_id='create_postgres_payments_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.clean_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            )
        """,
    )
  ```
  2. **Iceberg Tables**: The SQL queries for Iceberg tables require additional settings for Iceberg, including the storage format (PARQUET) and the location on S3 `WITH (location = 's3a://lakehouse/jaffle_shop_sc')`. While Iceberg supports both Avro and Parquet formats, Parquet is recommended due to its robust community support.
  ```plaintext
    create_clean_iceberg_customers = SQLExecuteQueryOperator(
        task_id='create_iceberg_customers_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/customers'
            )
        """,
    )

    create_clean_iceberg_orders = SQLExecuteQueryOperator(
        task_id='create_iceberg_orders_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_orders (
                id INTEGER, 
                user_id INTEGER, 
                order_date TIMESTAMP, 
                status VARCHAR(50)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/orders'
            )
        """,
    )

    create_clean_iceberg_payments = SQLExecuteQueryOperator(
        task_id='create_iceberg_payments_table',
        conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.clean_payments (
                id INTEGER, 
                order_id INTEGER, 
                payment_method VARCHAR(50), 
                amount DECIMAL(10, 2)
            ) WITH (
                format = 'PARQUET',
                location = 's3a://lakehouse/jaffle_shop_sc/clean_data/payments'
            )
        """,
    )
  ```

### 3. DBT with ELT Flow Start (Lines 128-145)
In this step, we initiate the ELT (Extract, Load, Transform) flow by using `dbt` to insert raw data into both Postgres and Iceberg tables. The raw data, which represents the source data for our pipeline, will be loaded into these tables before any transformations are applied. This allows us to store the raw data in both structured (Postgres) and lakehouse (Iceberg) environments.

We use the `dbt seed` command, which is specifically designed to load static data (typically from CSV files) into the target database. In our case, we load this data into both Postgres and Iceberg, leveraging dbt profiles for each environment.

#### Why DBT Seed is Used:
- **Postgres**: Postgres acts as a transactional database, which allows for efficient querying, relational operations, and data integrity checks. By seeding the raw data into Postgres first, we ensure that it is easily accessible for relational database operations and transformations.
- **Iceberg**: Iceberg is used for long-term storage and analytics. It enables high-performance queries on large datasets and is optimized for cloud environments (like S3). Seeding the raw data into Iceberg allows us to store it in a columnar format (e.g., Parquet), making it suitable for analytical workloads.

#### DBT Seed Process:

1. **DBT Seed to Postgres**:
   In this step, we use a BashOperator to run the `dbt seed` command, which inserts the raw data into the Postgres tables. The dbt profile `jaffle_shop_postgres` ensures that the data is loaded into the correct Postgres schema.

  ```plaintext
      dbt_insert_raw_data_to_postgres_table = BashOperator(
          task_id='dbt_seed_raw_to_postgres',
          bash_command='cd /opt/dbt/dbt_project && dbt seed --profile jaffle_shop_postgres',
      )
  ```

  - This command navigates to the dbt project directory and executes the dbt seed command
  - The data is inserted into the tables defined in the Postgres schema (jaffle_shop_postgres.jaffle_shop_sc), ensuring that the raw data is available for further transformations in the pipeline.

2. **DBT Seed to Iceberg**:
  Similarly, we seed the raw data into Iceberg using another BashOperator, which runs the dbt seed command with the jaffle_shop_iceberg profile. This step ensures that the raw data is also available in the Iceberg tables for lakehouse-based operations.

  ```plaintext
      dbt_insert_raw_data_to_iceberg_table = BashOperator(
          task_id='dbt_seed_raw_to_iceberg',
          bash_command='cd /opt/dbt/dbt_project && dbt seed --profile jaffle_shop_iceberg',
      )
  ```

  - This command inserts the raw data into the Iceberg schema (jaffle_shop_iceberg.jaffle_shop_sc) with the specified S3 location.
  - By using Iceberg, the raw data is stored in an optimized columnar format (Parquet), which is ideal for large-scale analytics and cloud-based data lakes.

### 4. Load Data from Postgres into Iceberg with Trino (138-190 Lines)
In this step, we transfer data between our Postgres and Iceberg tables. This is necessary because in our ETL pipeline, we might want to leverage Postgres for certain operations and Iceberg for others, such as querying data stored in an efficient columnar format like Parquet.

We first load data from Postgres tables into Iceberg, ensuring the data is written in the desired format (`PARQUET`) and stored in our S3-based lakehouse architecture. Then, we load data back from Iceberg into Postgres, allowing us to analyze or work with the data in both environments.
1. **Postgres Table to Iceberg Table:**
The following operators move data from Postgres tables to the Iceberg tables by using `INSERT INTO` statements. This approach allows us to use Postgres as a staging area for raw data and later transfer it into Iceberg for long-term storage in S3, where we take advantage of Iceberg’s features like partitioning and schema evolution.
```plaintext
  postgres_to_iceberg_customers = SQLExecuteQueryOperator(
      task_id='postgres_to_iceberg_customers',
      conn_id='trino_conn',
      sql="""            
          INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_customers 
          SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_customers
      """,
  )

  postgres_to_iceberg_orders = SQLExecuteQueryOperator(
      task_id='postgres_to_iceberg_orders',
      conn_id='trino_conn',
      sql="""            
          INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_orders 
          SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_orders
      """,
  )

  postgres_to_iceberg_payments = SQLExecuteQueryOperator(
      task_id='postgres_to_iceberg_payments',
      conn_id='trino_conn',
      sql="""            
          INSERT INTO jaffle_shop_iceberg.jaffle_shop_sc.clean_payments 
          SELECT * FROM jaffle_shop_postgres.jaffle_shop_sc.raw_payments
      """
  )
```
2. **Iceberg Table to Postgres Table:**
In this part, we move data from Iceberg tables back into Postgres. This step is useful when we want to leverage Postgres for querying and analysis while keeping the source data in Iceberg for optimized storage. By transferring the data back into Postgres, we ensure that we can perform relational database operations on it when needed.
```plaintext
    iceberg_to_postgres_customers = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_customers',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_customers 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_customers
        """,
    )

    iceberg_to_postgres_orders = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_orders',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_orders 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_orders
        """,
    )

    iceberg_to_postgres_payments = SQLExecuteQueryOperator(
        task_id='iceberg_to_postgres_payments',
        conn_id='trino_conn',
        sql="""
            INSERT INTO jaffle_shop_postgres.jaffle_shop_sc.clean_payments 
            SELECT * FROM jaffle_shop_iceberg.jaffle_shop_sc.raw_payments
        """,
    )
```
### 5. Optimization for Dummy Node for Airflow Dag (192-196 Lines)
To manage task dependencies, DummyOperator can be used to link multiple tasks, ensuring they run in sequence or in parallel, while keeping the DAG structure clean and organized.
```plaintext
connect_node_1 = DummyOperator(task_id='connect_empty_node_1')
connect_node_2 = DummyOperator(task_id='connect_empty_node_2')
connect_node_3 = DummyOperator(task_id='connect_empty_node_3')
connect_node_4 = DummyOperator(task_id='connect_empty_node_4')
connect_node_5 = DummyOperator(task_id='connect_empty_node_5')
```

### 6. Linked Tasks in The Airflow (198-203 Lines)
At the end of the DAG, tasks are linked to define the execution order, ensuring that the appropriate tasks run first.
```plaintext
[create_schema_iceberg, create_schema_postgres] >> connect_node_1
connect_node_1 >> [create_clean_postgres_customers, create_clean_postgres_orders, create_clean_postgres_payments] >> connect_node_2
connect_node_2 >> [create_clean_iceberg_customers, create_clean_iceberg_orders, create_clean_iceberg_payments] >> connect_node_3
connect_node_3 >> [dbt_insert_raw_data_to_postgres_table, dbt_insert_raw_data_to_iceberg_table] >> connect_node_4
connect_node_4 >> [iceberg_to_postgres_customers, iceberg_to_postgres_orders, iceberg_to_postgres_payments] >> connect_node_5
connect_node_5 >> [postgres_to_iceberg_customers, postgres_to_iceberg_orders, postgres_to_iceberg_payments]
```

## Project Conclusion and Data Flow Overview
This project implements a seamless data pipeline across multiple environments. Airflow orchestrates the ETL processes, managing task dependencies and scheduling workflows. Trino serves as the query engine, moving data between Postgres (for structured, transactional tasks) and Apache Iceberg (for high-performance analytics and long-term storage in a lakehouse, backed by MinIO for object storage).

MariaDB supports the Hive Metastore, organizing Iceberg tables. We use dbt to initiate the ELT flow, seeding raw data into both Postgres and Iceberg, preparing it for further transformations.

This architecture integrates Airflow, Trino, Iceberg, Postgres, MinIO, and dbt into a robust pipeline that efficiently manages and processes structured and unstructured data.

![full_dag](https://github.com/user-attachments/assets/6801c202-0f70-418d-b707-40e36be01e15)

# References:
Trino — Hive connector: https://trino.io/docs/current/connector/hive.html

Trino — Postgres connector: https://trino.io/docs/current/connector/postgresql.html

Trino — dbt connector: https://docs.getdbt.com/docs/core/connect-data-platform/trino-setup

Airflow & Scheduler container ENV: https://hub.docker.com/r/bitnami/airflow & https://hub.docker.com/r/bitnami/airflow-scheduler

Hive-Metastore: https://repo1.maven.org/maven2/org/apache/hive/hive-standalone-metastore/3.1.3/

Trino-Minio Docker Setup: https://blog.min.io/minio-trino-kubernetes/

# Authors
`Can Sevilmis` & `M. Cagri AKTAS`
