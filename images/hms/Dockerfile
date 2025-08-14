FROM openjdk:17-slim-bullseye

WORKDIR /opt

ENV HADOOP_VERSION=3.4.1
ENV METASTORE_VERSION=3.0.0

RUN apt-get update && \
    apt-get install -y curl wget netcat procps net-tools iproute2 && \
    rm -rf /var/lib/apt/lists/*

ENV HADOOP_HOME=/opt/hadoop-${HADOOP_VERSION}
ENV HIVE_HOME=/opt/apache-hive-metastore-${METASTORE_VERSION}-bin

RUN curl -L https://repo1.maven.org/maven2/org/apache/hive/hive-standalone-metastore/${METASTORE_VERSION}/hive-standalone-metastore-${METASTORE_VERSION}-bin.tar.gz | tar zxf - && \
    curl -L https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz | tar zxf -

RUN curl -L https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-web/2.24.3/log4j-web-2.24.3.jar -o ${HIVE_HOME}/lib/log4j-web-2.14.1.jar

RUN chmod 777 /

COPY init-sh/starter-hms.sh /starter-hms.sh
RUN chmod +x /starter-hms.sh

EXPOSE 9083

ENTRYPOINT ["/starter-hms.sh"]