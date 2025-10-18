{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2
) }}

with payments as (
  select * from {{ ref('stg_payments') }}
),
orders as (
  select * from {{ ref('stg_orders') }}
),
final as (
  select
    o.customer_id,
    sum(p.amount) as total_amount
  from payments p
  left join orders o using (order_id)
  group by 1
)
select * from final
