#!/bin/bash

sleep 5

# Start Trino in the background and redirect logs to stdout
nohup /opt/trino/bin/launcher run >> /dev/stdout 2>&1 &

# Wait for Trino to start
sleep 10

# Run post-init SQL commands
# trino < /app/init/post-init.sql

sleep 5

service ssh start 

sleep 5

# Keep the container running
tail -f /dev/null