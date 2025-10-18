-- Main Iceberg schema for jaffle_shop data quality metrics
CREATE SCHEMA IF NOT EXISTS jaffle_shop_iceberg.jaffle_shop_sc
WITH (location = 'hdfs://namenode:9000/warehouse/jaffle_shop_sc');