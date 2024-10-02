CREATE TABLE jaffle_shop_iceberg.jaffle_shop_sc WITH (location = 's3://warehouse/clean_orders');

CREATE TABLE jaffle_shop_iceberg.jaffle_shop_sc WITH (location = 's3://warehouse/clean_customers');

CREATE TABLE jaffle_shop_iceberg.jaffle_shop_sc WITH (location = 's3://warehouse/clean_payments');