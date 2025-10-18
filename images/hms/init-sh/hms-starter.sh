#!/bin/bash

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
    sleep 1
done

echo "Creating The HMS's metastore-site.xml configs..."
envsubst < $HIVE_HOME/conf/metastore-site.xml.template > $HIVE_HOME/conf/metastore-site.xml

echo "Waiting for HDFS NameNode..."
while ! nc -z namenode 9000; do
    sleep 1
done

if [ ! -f /var/lib/metastore/SCHEMA_VERSION ]; then
    echo "Initializing Hive Metastore schema..."
    schematool -initSchema -dbType postgres
fi

sleep 1

echo "Starting Hive Metastore..."
start-metastore -p 9083