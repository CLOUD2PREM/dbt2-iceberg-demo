#!/bin/bash

echo " 🛠️ Checking has been started..."

echo "✅ Containers are being checked and shut down."
docker-compose down

echo ".........."

FILE="trino/config/config.properties"
if [ -f "$FILE" ]; then
    echo "✅ $FILE file exists."
else
    echo "⚠️ $FILE file does not exist! ⚠️"
fi

echo ".........."

FILE="trino/catalog/jaffle_shop_db.properties"
if [ -f "$FILE" ]; then
    echo "✅ $FILE file exists."
else
    echo "⚠️ $FILE file does not exist! ⚠️"
fi

echo ".........."

FILE="trino/config/jvm.config"
if [ -f "$FILE" ]; then
    echo "✅ $FILE file exists."
else
    echo "⚠️ $FILE file does not exist! ⚠️"
fi

echo ".........."

FILE="dags/dbt_dag.py"
if [ -f "$FILE" ]; then
    echo "✅ $FILE file exists."
else
    echo "⚠️ $FILE file does not exist! ⚠️"
fi

echo ".........."

read -p "Delete PostgreSQL data: (y/n): " clean_volume
if [ "$clean_volume" == "y" ]; then
    sudo rm -rf postgres/postgresql_data/*
    echo "✅ PostgreSQL volume cleaned."
fi

echo ".........."

read -p "Clean dbt project files: (y/n): " clean_dbt
if [ "$clean_dbt" == "y" ]; then
    cd jaffle_shop
    dbt clean
    echo "✅ dbt project files cleaned."
    cd ..
fi

echo ".........."

echo "Checking Docker containers..."
docker ps -a --format "table {{.Names}}\t{{.Status}}"
if docker ps -a --filter "status=exited" | grep -q 'Exited'; then
    read -p "Some containers have stopped, would you like to restart them using the docker-compose file? (y/n): " restart_containers
    if [ "$restart_containers" == "y" ]; then
        docker-compose up -d --build
        echo "✅ Containers restarted."
    else
        echo "No action taken on containers."
    fi
else
    echo "✅ All containers are running."
fi

echo ".........."
