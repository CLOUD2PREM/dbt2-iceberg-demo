FROM eclipse-temurin:22-jdk-jammy

ARG TRINO_VERSION

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
    && touch /var/log/auth.log \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

# Download and install Trino
RUN mkdir -p $TRINO_HOME \
    && curl -fsSL "https://repo1.maven.org/maven2/io/trino/trino-server/$TRINO_VERSION/trino-server-$TRINO_VERSION.tar.gz" | tar -xz -C $TRINO_HOME --strip-components=1 \
    && mkdir -p $TRINO_HOME/etc $TRINO_HOME/etc/catalog

RUN mkdir -p $TRINO_HOME/init-sh

# Download and install the Trino CLI (https://repo1.maven.org/maven2/io/trino/trino-cli/)
RUN curl "https://repo1.maven.org/maven2/io/trino/trino-cli/$TRINO_VERSION/trino-cli-$TRINO_VERSION-executable.jar" -o $TRINO_HOME/init-sh/trino-cli \
    && chmod +x $TRINO_HOME/init-sh/trino-cli

COPY init-sh/starter-trino.sh $TRINO_HOME/init-sh/starter-trino.sh

RUN chmod -R 777 $TRINO_HOME/init-sh/starter-trino.sh && \
    chmod +x $TRINO_HOME/init-sh/starter-trino.sh

WORKDIR $TRINO_HOME

ENTRYPOINT ["/opt/trino/init-sh/starter-trino.sh"]