{{ config(
  materialized = 'table',
  partition_by = 'order_id',
  file_format = 'parquet',
  format_version = 2
) }}

with source as (
  select * from {{ ref('raw_payments') }}
),
payment as (
  select
    id             as payment_id,
    order_id,
    payment_method,
    amount / 100.0 as amount
  from source
)
select * from payment
