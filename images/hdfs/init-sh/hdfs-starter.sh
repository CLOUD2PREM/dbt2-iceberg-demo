#!/bin/bash

export 

echo "Start SSH service"
service ssh start
sleep 2

echo "Format the namenode"
if [ "$HOSTNAME" = "namenode" ] && [ ! -f ${HADOOP_HOME}/dfs/name/current/VERSION ]; then
    echo "Formatting namenode..."
    hdfs namenode -format -force
fi

echo "Start appropriate HDFS service"
if [ "$HOSTNAME" = "namenode" ]; then
    echo "Starting namenode..."
    hdfs --daemon start namenode
elif [ "$HOSTNAME" = "datanode" ]; then
    echo "Starting $HOSTNAME..."
    hdfs --daemon start datanode
else
    echo "Unknown hostname: $HOSTNAME. Must be 'namenode' or 'datanode'."
    exit 1
fi

echo "Setting up iceberg path and permission"
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -chmod 777 /user/hive/warehouse

echo "HDFS service started successfully"
tail -f ${HADOOP_HOME}/logs/*