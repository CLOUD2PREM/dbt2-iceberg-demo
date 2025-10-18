-- models/staging/stg_orders.sql (and do this for stg_customers.sql, stg_payments.sql too!)
{{ config(
  materialized = 'table',
  partition_by = 'order_date',
  file_format = 'parquet',
  format_version = 2
) }}

with source as (
  select * from {{ ref('raw_orders') }}
),
renamed as (
  select
    id         as order_id,
    user_id    as customer_id,
    order_date,
    status
  from source
)
select * from renamed