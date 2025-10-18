{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2,
  partition_by = 'order_date'
) }}

{% set payment_methods = ['credit_card','coupon','bank_transfer','gift_card'] %}

with orders as (
  select * from {{ ref('stg_orders') }}
),
order_payments as (
  select * from {{ ref('order_payments') }}
),
final as (
  select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    {% for m in payment_methods -%}
    coalesce(op.{{ m }}_amount, 0) as {{ m }}_amount,
    {% endfor -%}
    coalesce(op.total_amount, 0) as amount
  from orders o
  left join order_payments op on o.order_id = op.order_id
)
select * from final