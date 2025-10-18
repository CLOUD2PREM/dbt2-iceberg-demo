{{ config(
  materialized = 'table',
  partition_by = 'customer_id',
  file_format = 'parquet',
  format_version = 2
) }}

with source as (
  select * from {{ ref('raw_customers') }}
),
customer as (
  select
    id as customer_id,
    first_name,
    last_name,
    email
  from source
)
select * from customer
