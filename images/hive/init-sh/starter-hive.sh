#!/bin/bash

export HADOOP_HOME=/opt/hadoop-3.4.1
export HIVE_HOME=/opt/apache-hive-3.1.3-bin
export PATH=$PATH:$HADOOP_HOME/bin:$HIVE_HOME/bin
export JAVA_HOME=/usr/local/openjdk-17

# Wait for HDFS
echo "Waiting for HDFS..."
while ! nc -z namenode 9000; do
    sleep 2
done

# Wait for HMS
echo "Waiting for Hive Metastore..."
while ! nc -z hms 9083; do
    sleep 2
done

# Create required directories
$HADOOP_HOME/bin/hdfs dfs -mkdir -p /user/hive/warehouse
$HADOOP_HOME/bin/hdfs dfs -chmod g+w /user/hive/warehouse

# Print network info for debugging
echo "Network configuration:"
ip addr show
netstat -tlpn

# Start HiveServer2 with explicit configuration
echo "Starting HiveServer2 with explicit configuration..."
hiveserver2 \
    --hiveconf hive.server2.thrift.bind.host=0.0.0.0 \
    --hiveconf hive.server2.thrift.port=10000 \
    --hiveconf hive.root.logger=INFO,console \
    --hiveconf hive.server2.transport.mode=binary \
    --hiveconf hive.metastore.uris=thrift://hms:9083 \
    --hiveconf hive.server2.logging.operation.enabled=true \
    --hiveconf hive.server2.logging.operation.log.location=/tmp/hive/operation_logs

# Wait for server to start
echo "Waiting for HiveServer2 port to be available..."
timeout=30
counter=0
while ! nc -z localhost 10000; do
    sleep 1
    counter=$((counter + 1))
    if [ $counter -gt $timeout ]; then
        echo "ERROR: HiveServer2 failed to start within $timeout seconds"
        exit 1
    fi
done

echo "HiveServer2 is listening on port 10000"
tail -f $HIVE_HOME/logs/*