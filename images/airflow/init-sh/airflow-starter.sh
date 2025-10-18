#!/bin/bash

while ! nc -z postgres 5432; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

echo "Creating the Airflow User..."
envsubst < ${AIRFLOW_HOME}/airflow.cfg.template > ${AIRFLOW_HOME}/airflow.cfg
envsubst < ${AIRFLOW_HOME}/auth/admin_password.json.template > ${AIRFLOW_HOME}/auth/admin_password.json

cd ${AIRFLOW_HOME}
airflow db migrate 

sleep 1

airflow connections add 'dbt_ssh' \
    --conn-type 'ssh' \
    --conn-login 'root' \
    --conn-password '3541' \
    --conn-port 22 \
    --conn-host '172.80.0.79'

sleep 1

airflow api-server > ${AIRFLOW_HOME}/logs/api.log 2>&1 &
airflow scheduler > ${AIRFLOW_HOME}/logs/scheduler.log 2>&1 &
airflow triggerer > ${AIRFLOW_HOME}/logs/triggerer.log 2>&1 &
airflow dag-processor > ${AIRFLOW_HOME}/logs/dag_processor.log 2>&1 &

# Tail all logs together
tail -f ${AIRFLOW_HOME}/logs/*.log