#!/bin/bash

# Create necessary directories
mkdir -p /root/airflow/{dags,logs,plugins}

# Wait for PostgreSQL to be ready
while ! nc -z postgres 5432; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

cd /root/airflow

sleep 5 

# Initialize the database and create user
airflow db migrate 

sleep 1

# Add DBT SSH Connection
airflow connections add 'dbt_ssh' \
    --conn-type 'ssh' \
    --conn-login 'root' \
    --conn-password '3541' \
    --conn-port 22 \
    --conn-host '172.80.0.79'

sleep 1

# Add Trino Connection
airflow connections add 'trino_conn' \
    --conn-type 'trino' \
    --conn-login 'cagri' \
    --conn-port 8080 \
    --conn-host '172.80.0.80'
  
sleep 5

# Start Airflow scheduler in the background
airflow scheduler &

sleep 1

# Start Airflow dag-processor in the background
airflow dag-processor &

sleep 1

# Start Airflow triggerer in the background
airflow triggerer & 

sleep 1

# Start Airflow webserver
airflow api-server