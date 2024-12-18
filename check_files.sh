#!/bin/bash

echo " 🛠️ Checking has been started..."
echo ".........."

total_files=0
existing_files=0

FILES=("airflow/dags" "airflow/logs" "airflow/Dockerfile" "airflow/scripts" "airflow/config")
for FILE in "${FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$FILE" ] || [ -d "$FILE" ]; then
        echo "✅ $FILE exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $FILE does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

HIVE_FILES=("hive-metastore/conf/metastore-site.xml" "hive-metastore/scripts/entrypoint.sh" "hive-metastore/Dockerfile")
for HIVE_FILE in "${HIVE_FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$HIVE_FILE" ] || [ -d "$HIVE_FILE" ]; then
        echo "✅ $HIVE_FILE exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $HIVE_FILE does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

MARIADB_FILE="mariadb/mariadb_data"
total_files=$((total_files + 1))
if [ -f "$MARIADB_FILE" ] || [ -d "$MARIADB_FILE" ]; then
    echo "✅ $MARIADB_FILE exists."
    existing_files=$((existing_files + 1))
else
    echo "⚠️ $MARIADB_FILE does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
fi

echo ".........."

MINIO_FILES=("minio/minio_data" "minio/scripts/entrypoint.sh" "minio/scripts/starter_minio.sh" "minio/Dockerfile")
for MINIO_FILE in "${MINIO_FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$MINIO_FILE" ] || [ -d "$MINIO_FILE" ]; then
        echo "✅ $MINIO_FILE exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $MINIO_FILE does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

POSTGRES_FILES=("postgres/postgres_data" "postgres/query_init")
for POSTGRES_FILE in "${POSTGRES_FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$POSTGRES_FILE" ] || [ -d "$POSTGRES_FILE" ]; then
        echo "✅ $POSTGRES_FILE exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $POSTGRES_FILE does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

TRINO_FILES=("trino/catalog" "trino/config/config.properties" "trino/config/jvm.config" "trino/logs")
for TRINO_FILES in "${TRINO_FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$TRINO_FILES" ] || [ -d "$TRINO_FILES" ]; then
        echo "✅ $TRINO_FILES exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $TRINO_FILES does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

DBT_FILES=("dbt/profiles" "dbt/project" "dbt/scripts" "dbt/Dockerfile")
for DBT_FILES in "${DBT_FILES[@]}"
do
    total_files=$((total_files + 1))
    if [ -f "$DBT_FILES" ] || [ -d "$DBT_FILES" ]; then
        echo "✅ $DBT_FILES exists."
        existing_files=$((existing_files + 1))
    else
        echo "⚠️ $DBT_FILES does not exist! Please check the GitHub repo: https://github.com/CLOUD2PREM/dbt2-iceberg-demo ⚠️"
    fi
done

echo ".........."

echo "✅ $existing_files/$total_files files or directories found."

echo ".........."

read -p "Delete PostgreSQL data: (y/n): " clean_volume
if [ "$clean_volume" == "y" ]; then
    sudo rm -rf postgres/postgresql_data
    mkdir postgres/postgresql_data
    echo "✅ PostgreSQL volume cleaned."
fi

echo ".........."

read -p "Delete Minio data: (y/n): " clean_volume
if [ "$clean_volume" == "y" ]; then
    sudo rm -rf minio/minio_data
    mkdir minio/minio_data
    echo "✅ Minio volume cleaned."
fi

echo ".........."

read -p "Delete Meta-store data: (y/n): " clean_volume
if [ "$clean_volume" == "y" ]; then
    sudo rm -rf mariadb/mariadb_data
    mkdir mariadb/mariadb_data
    echo "✅ Meta-store volume cleaned."
fi

echo ".........."