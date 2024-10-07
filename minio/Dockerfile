FROM minio/minio:RELEASE.2023-08-23T10-07-06Z

# Install curl for healthcheck
RUN microdnf install curl -y && microdnf clean all

# Copy the script into the container
COPY ./scripts/starter_minio.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/starter_minio.sh

# Use a custom entrypoint script
COPY ./scripts/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV MINIO_ROOT_USER_FILE=
ENV MINIO_ROOT_PASSWORD_FILE=

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]