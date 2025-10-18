# dbt2-iceberg-demo
Iceberg with Seamless Data Integration

This repo demonstrates a reproducible lakehouse pipeline that integrates dbt, Trino, Apache Iceberg, Hive Metastore, HDFS, Postgres and Airflow. The demo shows how to seed raw CSV data into HDFS, materialize it into Iceberg tables via dbt + Trino, run transformations and tests with dbt from Airflow, and use Postgres for certain downstream operations. The README below explains environment requirements, startup steps, configuration snippets and the high-level ETL flow.

<p align="center">
  <img width="438" height="594" alt="airflow-art" src="https://github.com/user-attachments/assets/072d1864-a4e9-4662-926d-27d29e00e812" />
</p>

---

## Table of Contents

- [Environment Setup](#environment-setup)
  - [System and Software Versions](#system-and-software-versions)
- [How to Start the Project](#how-to-start-the-project)
- [Iceberg Connection Information](#iceberg-connection-information)
- [DBT Connection Schema Information](#dbt-connection-schema-information)
- [How to Run the Project: ETL_Lakehouse_Pattern.py High-Level Steps](#how-to-run-the-project-etl_lakehouse_patternpy-high-level-steps)
  - [1. Seed the raw data (sample data) to HDFS (24-35 Lines)](#1-seed-the-raw-data-sample-data-to-hdfs-24-35-lines)
  - [2. Creating dbt_pipeline for Iceberg With Trino (41-81 Lines)](#2-creating-dbt_pipeline-for-iceberg-with-trino-41-81-lines)  
  - [3. Check the transfrom data quality with DBT Test and SQL checking (87-114 Lines)](#3-check-the-transfrom-data-quality-with-dbt-test-and-sql-checks-87-114-lines) 
  - [4. DBT DOCS (118-129 Lines)](#4-dbt-docs-118-129-lines)
- [Project Conclusion and Data Flow Overview](#project-conclusion-and-data-flow-overview)
- [References](#references)
- [Authors](#authors)

---

## Environment Setup
### System and Software Versions

| Software          | Description                                    | Version                             | UI - Ports      |
|-------------------|------------------------------------------------|-------------------------------------|------------|
| **WSL**           | Windows Subsystem for Linux environment         | Rocky Linux (Distro 2)             |            |
| **Docker**        | Containerization platform                      | Docker version 27.2.0               |            |
| **Docker Compose**| Tool for defining and running multi-container Docker applications | v2.29.2-desktop.2 |            |
| **Postgres**      | Open-source relational database                 | postgres:17                         |            |
| **Trino**         | Distributed SQL query engine                    | trino:476                           | 8080       |
| **DBT**           | Data build tool for transforming data in the warehouse | 1.10.2                          |            |
| **Iceberg**       | High-performance table format for big data      | 1.6.1                               |            |
| **Python**        | Programming language                           | 3.10.12                             |            |
| **Airflow**       | Workflow automation and scheduling tool         | 3.0.0                              | 9090       |
| **Hadoop**        | Framework for distributed storage and processing| 3.4.1                             |  9870          |
| **Hive-Metastore**| Metadata service for table management and storage           | 4.1.0                               |            |

---

## How to Start The Project

**1. Clone the project:**
```plaintext
git clone https://github.com/CLOUD2PREM/dbt2-iceberg-demo.git
```

**2. Create Docker network:**
```plaintext
docker network create --subnet=172.80.0.0/16 dahbest
```

**3. Check the .ENV file:**
```plaintext
You can change your container username and password in .ENV file.
```

**4. Start the containers:**
```plaintext
docker-compose up -d --build
```

**5. Start The ETL Dag:**
Wait 1–2 minutes for Airflow to fully start, then go to `localhost:9090`. You can run the DAG file in two ways:

  1. Airflow UI:
  ```bash
  DAGS Section => Trigger
  ```
    
  2. Airflow CLI:
  ```bash
  docker exec -it airflow bash
  airflow dags trigger ETL_Lakehouse_Pattern
  ```

---

## Iceberg Connection Information:
If you want to change your Iceberg connection information. 
Iceberg: Please check the `docker-compose.yaml` and `trino` ==> `catalog` ==> `jaffle_shop_iceberg.properties` files:
```plaintext
connector.name=iceberg
iceberg.catalog.type=hive_metastore
hive.metastore.uri=thrift://hms:9083
hive.metastore.authentication.type=NONE
iceberg.compression-codec=NONE
iceberg.file-format=ORC
fs.hadoop.enabled=true
hive.config.resources=/opt/hadoop-3.4.1/etc/hadoop/core-site.xml,/opt/hadoop-3.4.1/etc/hadoop/hdfs-site.xml
```

---

## DBT Connection Schema Information:
When we define Iceberg integration in dbt, we need to specify the schema and some configuration settings. In `/configs/dbt/project/models/*`, each folder contains its own schema.yml file. The schema.yml defines the table fields and the testing scenarios for those fields. Typically, a schema.yml file can be written like this:
```yml
version: 2

models:
  - name: stg_customers # Table name

    columns:
    - name: customer_id  # Fiels name
    tests: [unique, not_null] # For testing (dbt test)
```

---

## How to Run The Project: ETL_Lakehouse_Pattern.py High Level Steps
### 1. Seed the raw data (sample data) to HDFS (24-35 Lines)
First, we seed raw sample data into HDFS for the demo. To understand this step, it’s important to know how the dbt seed command loads raw data into HDFS.
  - Iceberg: Iceberg is used for long-term storage and analytics. It enables high-performance queries on large datasets and is optimized for cloud environments (such as S3). Seeding raw data into Iceberg stores it in a columnar format (e.g., Parquet), making it suitable for analytical workloads.
We use a BashOperator that runs the dbt seed command with the jaffle_shop_iceberg profile. This ensures that the raw data is available in Iceberg tables for lakehouse-based operations.

We also defined a macro for seeding Iceberg. The macro retrieves the schema for each seed insert. You can check it in `/configs/dbt/project/seeds/schema.yml`.
```sql
-- macros/get_custom_schema.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

Also, when we use the Hive catalog with Iceberg, we need to create a schema. However, DBT cannot create schemas directly, so we create it using Trino instead. I configured the container startup process to create the schema automatically. If you want to check it, please see the `configs/trino/init-sql/post-init.sql file`.
```sql
CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc
WITH (location = 'hdfs://namenode:9000/warehouse/jaffle_shop_sc');
```

Then, the seed command triggers the macro, which locates the corresponding Iceberg schema.
```py
dbt_seed = SSHOperator(
    task_id='dbt_sample_data',
    command="""
        cd /opt/dbt && \
        dbt seed --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```

### 2. Creating dbt_pipeline for Iceberg With Trino (41-81 Lines)
Next, we create three ETL pipelines to transform the data. In this step, data is moved from Iceberg tables back into PostgreSQL. This allows us to leverage PostgreSQL for querying and analysis while keeping the source data in Iceberg for optimized storage. In this step, we transfer data between our Postgres and Iceberg tables. This is necessary because in our ETL pipeline, we might want to leverage Postgres for certain operations and Iceberg for others, such as querying data stored in an efficient columnar format like Parquet. We first load data from Postgres tables into Iceberg, ensuring the data is written in the desired format (PARQUET) and stored in our HDFS-based lakehouse architecture. Then, we load data back from Iceberg into Postgres, allowing us to analyze or work with the data in both environments.

The four dbt pipelines are:
  - Staging
  - Intermediate
  - Marts

All models use Iceberg partition columns and configurations. Here’s a sample of how to manage dbt SQL for Iceberg.
Example of a SQL file, `./configs/dbt/project/models/staging/stg_customers.sql`:
```sql
{{ config(
  materialized='table',             # Creates a table directly; no need to use INSERT INTO.
  partition_by='customer_id',       # Important: choose the best partition column for each dataset. Often a date field is used.
  file_format='parquet',            # Parquet format is defined in Trino configuration. You can also set it here, but Trino may override this parameter.
  format_version=2                  # Iceberg table format version 2.
) }}
```

After that, we need to set up our data manipulation logic in `stg_customers.sql`:
```sql
with source as (
  select * from {{ ref('raw_customers') }}
),
customer as (
  select
    id as customer_id,
    first_name,
    last_name,
    email
  from source
)
select * from customer
```

---

**1. staging**
```py
dbt_staging = SSHOperator(
    task_id='dbt_staging',
    command="""
        cd /opt/dbt && \
        dbt run --profiles-dir /opt/dbt/profiles \
                --project-dir /opt/dbt/project \
                --profile jaffle_shop_iceberg \
                --target dev \
                --select models/staging
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```
**2. intermediate**
```py
dbt_intermediate = SSHOperator(
    task_id='dbt_intermediate',
    command="""
        cd /opt/dbt && \
        dbt run --profiles-dir /opt/dbt/profiles \
                --project-dir /opt/dbt/project \
                --profile jaffle_shop_iceberg \
                --target dev \
                --select models/intermediate
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```
**3. marts**: 
```py
dbt_marts = SSHOperator(
    task_id='dbt_marts',
    command="""
        cd /opt/dbt && \
        dbt run --profiles-dir /opt/dbt/profiles \
                --project-dir /opt/dbt/project \
                --profile jaffle_shop_iceberg \
                --target dev \
                --select models/marts
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```

### 3. Check the transfrom data quality with DBT Test and SQL checks (87-114 Lines)
Data quality is checked in two ways. When we trigger dbt models, we need to validate the data to ensure it is optimal.
**1. DBT Quality**
```py
dbt_quality = SSHOperator(
    task_id='dbt_quality',
    command="""
        cd /opt/dbt && \
        dbt run --profiles-dir /opt/dbt/profiles \
                --project-dir /opt/dbt/project \
                --profile jaffle_shop_iceberg \
                --target dev \
                --select models/quality
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```

As we discussed in `models/schema.yml`, we defined test fields, and dbt automatically checks these configurations and returns the results.
Exmaple:
```sql
  - name: stg_orders
    columns:
      - name: order_id
        tests: [unique, not_null] # <<<
```

**2. DBT Test**
```py
dbt_test = SSHOperator(
    task_id='dbt_test',
    command="""
        cd /opt/dbt && \
        dbt test --profiles-dir /opt/dbt/profiles \
                    --project-dir /opt/dbt/project \
                    --profile jaffle_shop_iceberg \
                    --target dev
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```

### 4. DBT DOCS (118-129 Lines)
Finally, we generate documentation for the dbt models to understand what happened.
```py
dbt_docs = SSHOperator(
    task_id='dbt_docs_generate',
    command="""
        cd /opt/dbt && \
        dbt docs generate --profiles-dir /opt/dbt/profiles \
                            --project-dir /opt/dbt/project \
                            --profile jaffle_shop_iceberg \
                            --target dev
    """,
    ssh_conn_id='dbt_ssh',
    dag=dag
)
```

DBT provides a clear view of our data pipeline architecture and detailed information about each table.
```bash
docker exec -it dbt dbt docs serve --host 0.0.0.0 --port 5050
```

<p align="center">
  <img width="350" height="594" alt="dbt-docs" src="https://github.com/user-attachments/assets/48ceee56-5853-4388-94f8-74ec3026b83c" />
</p>

All data is stored in HDFS using the Iceberg table format:

<p align="center">
  <img width="1000" height="1600" alt="hdfs-output" src="https://github.com/user-attachments/assets/311d3f2f-9298-46fb-8087-db3b8a027979" />
</p>

---

## Project Conclusion and Data Flow Overview
This project implements a seamless data pipeline across multiple environments. Airflow orchestrates the ETL processes, managing task dependencies and scheduling workflows. Trino serves as the query engine, moving data between Postgres (for structured, transactional tasks) and Apache Iceberg (for high-performance analytics and long-term storage in a lakehouse, backed by HDFS for object storage).

HDFS supports the Hive Metastore, organizing Iceberg tables. We use dbt to initiate the ELT flow, seeding raw data into HDFS with Iceberg, preparing it for further transformations.

This architecture integrates Airflow, Trino, Iceberg, HDFS, Postgres for DB and dbt into a robust pipeline that efficiently manages and processes structured and unstructured data.

<p align="center">
  <img width="350" height="594" alt="airflow-output" src="https://github.com/user-attachments/assets/13f8a7aa-1802-4e1c-90f2-44fcc7d9ff35" />
</p>

---

## References:
Trino — Hive connector: https://trino.io/docs/current/connector/hive.html

Trino — dbt connector: https://docs.getdbt.com/docs/core/connect-data-platform/trino-setup

Hive-Metastore: https://repo1.maven.org/maven2/org/apache/hive/hive-standalone-metastore/3.1.3/

## Authors
`Can Sevilmis` & `M. Cagri AKTAS`
