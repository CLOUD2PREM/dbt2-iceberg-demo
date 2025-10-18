#!/bin/bash

echo "Trino properties files are creating..."
envsubst < /opt/trino/etc/catalog/jaffle_shop_postgres.properties.templates > /opt/trino/etc/catalog/jaffle_shop_postgres.properties

echo "Trino post-init.sql is starting..."
post-init.sh &

echo "Trino is starting..."
/opt/trino/bin/launcher run