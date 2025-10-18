#!/bin/bash
set -e

echo "SSH is starting..."
/usr/sbin/sshd &

sleep 5

if [[ ! -f "${DBT_PROJECT_DIR}/logs/dbt.log" ]]; then
    touch "${DBT_PROJECT_DIR}/logs/dbt.log"
    echo "Log file created: ${DBT_PROJECT_DIR}/logs/dbt.log"
else
    echo "Log file already exists"
fi

echo "DBT is starting..."
tail -f "${DBT_PROJECT_DIR}/logs/dbt.log"