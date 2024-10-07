#!/bin/sh

echo "Starting MinIO initialization..."
echo "MINIO_ROOT_USER length: ${#MINIO_ROOT_USER}"
echo "MINIO_ROOT_PASSWORD length: ${#MINIO_ROOT_PASSWORD}"
echo "AWS_ACCESS_KEY_ID length: ${#AWS_ACCESS_KEY_ID}"
echo "AWS_SECRET_ACCESS_KEY length: ${#AWS_SECRET_ACCESS_KEY}"

# Start MinIO in background
minio server --console-address ":9001" /data &

# Wait for MinIO to be ready
until curl -s http://localhost:9000/minio/health/ready; do
  echo 'Waiting for MinIO to be ready...'
  sleep 5
done

# Run the initialization script
/usr/local/bin/starter_minio.sh

# Keep container running
wait