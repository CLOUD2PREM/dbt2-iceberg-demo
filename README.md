# dbt2-iceberg-demo
Iceberg with Postgres Seamless Data Integration

This project aims to create a data pipeline using Airflow triggers, integrating ETL processes with relevant databases via Trino. The pipeline includes S3 MinIO for Iceberg storage and PostgreSQL for database operations, with Airflow orchestrating the workflow. Additionally, dbt is used to seed raw data into PostgreSQL, where CSV files are loaded via the dbt seed command. This enables easy population of raw data into PostgreSQL, facilitating further transformations and smooth integration with Iceberg. The documentation outlines the system and software versions used, along with the necessary libraries.

![image](https://github.com/user-attachments/assets/a0966f81-133b-4571-9650-2b54018122ff)

In this project, we’ll cover:
  - How to install dbt and create a data pipeline.
  - How to create Docker containers for Trino, PostgreSQL, and MinIO (S3).
  - How to deploy Trino configuration and properties files for connecting to Iceberg and PostgreSQL.
  - How to configure Trino to use Iceberg as a table format with MinIO as the storage backend.
  - How to create Docker container volumes.
  - How to set up a Docker network for our containers.
  - How to seed your raw data with DBT pipeline.
  - Load Data from Iceberg into Postgres
  - Load Data from Postgres into Iceberg

# 🛠️ Git Clone (Easy Setup)

```plaintext
git clone https://github.com/CLOUD2PREM/dbt2-iceberg-demo.git
```
If you clone the project, just make sure to install:
1. Python
2. dbt
3. Set up the ~/.dbt/profiles.yml file
4. Create docker network
5. docker-compose up -d --build
6. You need to install and start Airflow. Please check the 🛠️ Airflow Setup section.

⚠️ Airflow's dags has been ready, you can find in `project folder` in `dags folder`, there're 3 dag files.
  1. Load data iceberg table to Postgres table.
  2. Load data postgres to Iceberg table.
The other configuration has already been ready.

All other configurations are already in place.

If you get any error: you can run `check_config.sh`

# 🛠️ Environment Setup

### System and Software Versions
- **WSL**: Ubuntu 24.04 (Distro 2)
- **Docker**: `Docker version 27.2.0, build 3ab4256`
- **Docker Compose**: `v2.29.2-desktop.2`
- **Postgres**: `postgres:16` (Postgres 16)
- **Trino**: `trinodb/trino:457` (Trino CLI 457)
- **Iceberg**: `iceberg:1.6.1`
- **Python**: `3.10.12`
- **Airflow**: `2.10.1`
  
### Python Environment Setup
```bash
python3.10 -m venv dbt_env
source dbt_env/bin/activate
pip install --upgrade pip setuptools wheel
pip install pip install dbt-core dbt-trino dbt-postgres
dbt --version
```

### dbt ve plugin versions
```bash
  Core:
    - installed: 1.8.7
    - latest:    1.8.7 - Up to date!
  
  Plugins:
    - postgres: 1.8.2 - Up to date!
    - trino:    1.8.2 - Up to date!
```

### ⚠️ Iceberg Connection Information:
If you want to change your Iceberg connection information, please check the docker-compose.yaml and trino ==> catalog ==> jaffle_shop_db.properties files.
```plaintext
connector.name=iceberg
iceberg.catalog.type=nessie
iceberg.nessie-catalog.uri=http://catalog:19120/api/v1
iceberg.nessie-catalog.default-warehouse-dir=s3://warehouse
fs.native-s3.enabled=true
s3.endpoint=http://storage:9000
s3.region=us-east-1
s3.path-style-access=true
s3.aws-access-key=admin
s3.aws-secret-key=password
```

# 🐳 Container Setup:
## Trino
1. Create the *.properties files for Trino and add the volume:
```plaintext
  - ./trino/config/config.properties:/etc/trino/config.properties:ro
  - ./trino/config/jvm.config:/etc/trino/jvm.config:ro
```

2. Create the catalog file for the Trino and PostgreSQL connection:
```plaintext
  - ./trino/catalog/jaffle_shop_iceberg.properties:/etc/trino/catalog/jaffle_shop_iceberg.properties:ro
  - ./trino/catalog/jaffle_shop_postgres.properties:/etc/trino/catalog/jaffle_shop_postgres.properties:ro
```

3. Also there're two file on init folder, these files is easly create iceberg table, if you wish you can use raw data or what u want.
```plaintext
  - ./trino/init/post-init.sh:/tmp/post-init.sh
  - ./trino/init/post-init.sql:/tmp/post-init.sql
```

4. Allocate memory to Trino at the start in the Docker-compose file to prevent overload during dbt operations:
```plaintext
environment:
  - TRINO_MEMORY_HEAP_HEADROOM_PER_NODE=2048MB
```

## PostgreSQL
1. Create Docker volume for our PostgreSQL data:
```plaintext
volumes:
  - ./postgres/postgresql_data:/var/lib/postgresql/data
  - ./postgres/query_init:/docker-entrypoint-initdb.d
```

2. Create Docker Container starter sql executer files:
⚠️ If you wish you can combine two file in single sql file but this artitecture looking clear.
```plaintext
  - ./postgres/query_init/jaffle_shop_postgres.sql:/docker-entrypoint-initdb.d/jaffle_shop_postgres.sql:ro
  - ./postgres/query_init/jaffle_shop_sc.sql:/docker-entrypoint-initdb.d/jaffle_shop_sc.sql:ro
```

3. ⚠️ Set up the SQL queries that will run when we start Docker:
```plaintext
echo "CREATE SCHEMA IF NOT EXISTS jaffle_shop_db;" >> postgres/query_init/create_jaffle_db.sql
```

## Iceberg Table:
⚠️ To use Iceberg tables, we need to deploy the following:

1. Storage: I used MinIO (S3) for this project. If you'd like more information, you can refer to this article: Trino Iceberg Documentation.
2. Catalog: A catalog is required to manage the Iceberg tables.
3. Executor Configuration: We also need to configure MinIO (S3) with the Secret Key, Access Key, and additional settings to access our bucket.

⚠️ You can find all the images and details on how to deploy the containers in the docker-compose.yaml file.

## Docker Network
1. Create Docker network before starting the containers:
```plaintext
docker network create --subnet=172.80.0.0/16 dahbest
```

## Docker Starter
1. Start up the Docker containers:
```plaintext
docker-compose up -d --build
```

2. Wait for 15 seconds and then check the Docker containers:
```plaintext
docker ps -a
```

# 🛠️ Airflow Setup
1. Activate Python Environment:
```plaintext
source ~/dbt_env/bin/activate
```

2. Install Airflow and Airflow database library:
```plaintext
pip install apache-airflow
pip install psycopg2-binary
```

3. Create dags folder in your project:
```plaintext
mkdir /home/cagri/project/dbt2-iceberg-demo/dags`
```

4. Change the Airflow configs:
```plaintext
dags_folder = /home/cagri/project/dbt2-iceberg-demo/dags
sql_alchemy_conn = postgresql+psycopg2://cagri:3541@localhost:5432/airflow_db
⚠️ We'll use Trino in 8080 port so les't change to airflow's port to 9090
base_url = http://localhost:9090
web_server_port = 9090
```

5. Create Airflow Admin User:
```plaintext
airflow users create --role Admin --username cagri --email mucagriaktas@gmail.com --firstname cagri --lastname aktas --password 3541
```

6. Setup Trino Operator Connection:

Go to the Airflow UI and navigate to the Connections panel. Then, configure the following settings:
```plaintext
Connection Id * = trino_conn
Connection Type * = Trino (ensure the Airflow module is installed)
Host = localhost
Login = cagri
Port = 8080
```

7. Define your new settings:
```plaintext
airflow db init
```

8. Start The Airflow:
If you want to start airflow background use nohup,
```plaintext
nohup airflow scheduler > scheduler.log 2>&1 &
nohup airflow webserver -p 9090 > webserver.log 2>&1 &
```
You can close your services:
```plaintext
ps aux | grep "airflow scheduler"
kill <scheduler_pid>
ps aux | grep "airflow webserver"
kill <scheduler_pid>
```
Or you can start manually:
```plaintext
cd ~/airflow
First terminal: airflow scheduler
Second terminal: airflow webserver -p 9090
```


# 🛠️ How to Load Data
⚠️ You'll need the raw data. I have placed 3 raw data files in the project folder, and you can find them as `jaffle_shop/seed/.` folder.
Also you can send your raw data with DBT pipeline:

## 🛠️ dbt Setup:
1. Setup the dbt project:
`dbt init jaffle_shop`

2. ⚠️ Then, let’s choose Trino.
`select trino.`

3. Edit the profiles.yml file:
Here’s an example of a profiles.yml file for Trino
nano ~/.dbt/profiles.yml
```plaintext
jaffle_shop_iceberg:
  outputs:
    dev:
      type: trino
      host: localhost
      port: 8080
      user: cagri
      catalog: jaffle_shop_iceberg
      schema: jaffle_shop_sc
      access_key: admin
      secret_key: password
      extras:
        hive.s3.aws-access-key: admin
        hive.s3.aws-secret-key: password
        hive.s3.endpoint: http://storage:9000
        hive.s3.path-style-access: true
  target: dev

jaffle_shop_postgres:
  outputs:
    dev:
      type: postgres
      host: localhost
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
⚠️ As you can see, you can also use it in the Airflow bash_command like this.

## How to Load data Iceberg to Postgres
1. Create dag file:
You can find dag file in `dags/ folder`, here's a examaple:
```plaintext
create_raw_iceberg_customers = TrinoOperator(
    task_id='create_raw_iceberg_customers_table',
    trino_conn_id='trino_conn',
    sql="""
        CREATE TABLE IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc.raw_customers (
            id INTEGER, 
            first_name VARCHAR(50), 
            last_name VARCHAR(50), 
            email VARCHAR(50)
        ) WITH (
            format = 'PARQUET',
            location = 's3://warehouse/raw_data/customers'
        )
    """,
)
```

![image](https://github.com/user-attachments/assets/fe6edca2-6eb8-49fc-adb2-14ecb115be34)


## How to load data Postgres to Iceberg
1. Create daf file:
2. You can find dag file in `dags/` folder, here's a example:
```plaintext
    create_raw_postgres_customers = TrinoOperator(
        task_id='create_postgres_customers_table',
        trino_conn_id='trino_conn',
        sql="""
            CREATE TABLE IF NOT EXISTS jaffle_shop_postgres.jaffle_shop_sc.raw_customers (
                id INTEGER, 
                first_name VARCHAR(50), 
                last_name VARCHAR(50), 
                email VARCHAR(50)
            )
        """,
    )
```

![image](https://github.com/user-attachments/assets/f2938c42-b708-43a3-bb25-6b63497b86eb)

