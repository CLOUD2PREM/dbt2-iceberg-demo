{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2
) }}

with customers as (
  select * from {{ ref('stg_customers') }}
),
customer_orders as (
  select * from {{ ref('customer_orders') }}
),
customer_payments as (
  select * from {{ ref('customer_payments') }}
),
final as (
  select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    co.first_order,
    co.most_recent_order,
    co.number_of_orders,
    cp.total_amount as customer_lifetime_value
  from customers c
  left join customer_orders   co on c.customer_id = co.customer_id
  left join customer_payments cp on c.customer_id = cp.customer_id
)
select * from final
