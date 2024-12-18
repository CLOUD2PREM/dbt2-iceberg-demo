# Start with a lightweight base image
FROM eclipse-temurin:22-jdk-jammy

ARG TRINO_VERSION

# Set environment variables
ENV TRINO_HOME=/opt/trino \
    PATH="/opt/trino/bin:$PATH"

# Install dependencies and Python
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    jq \
    libicu-dev \
    less \
    openssh-server \
    && touch /var/log/auth.log \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ensure 'python' command is available
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update && apt-get install -y openssh-server \
&& mkdir /var/run/sshd

# Configure SSH
RUN echo "root:3541" | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Initialize custom scripts
COPY init /app/init
RUN chmod +x /app/init/* && /app/init/setup.sh || true

# Download and install the Trino CLI
RUN curl "https://repo1.maven.org/maven2/io/trino/trino-cli/$TRINO_VERSION/trino-cli-$TRINO_VERSION-executable.jar" -o /usr/local/bin/trino \
    && chmod +x /usr/local/bin/trino

# Download and install Trino
RUN mkdir -p $TRINO_HOME \
    && curl -fsSL "https://repo1.maven.org/maven2/io/trino/trino-server/$TRINO_VERSION/trino-server-$TRINO_VERSION.tar.gz" | tar -xz -C $TRINO_HOME --strip-components=1 \
    && mkdir -p $TRINO_HOME/etc $TRINO_HOME/etc/catalog

# Copy configuration files
COPY etc/config.properties $TRINO_HOME/etc/config.properties
COPY etc/jvm.config $TRINO_HOME/etc/jvm.config
COPY etc/log.properties $TRINO_HOME/etc/log.properties
COPY etc/node.properties $TRINO_HOME/etc/node.properties
COPY catalog $TRINO_HOME/etc/catalog
COPY init/post-init.sh /app/init/post-init.sh
COPY init/post-init.sql /app/init/post-init.sql

RUN chmod -R 777 /app/init && \
    chmod +x /app/init/post-init.sh

# Expose Trino ports
EXPOSE 8080 22

# Set the entry point
WORKDIR $TRINO_HOME
ENTRYPOINT ["/app/init/post-init.sh"]