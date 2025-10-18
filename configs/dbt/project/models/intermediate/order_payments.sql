{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2
) }}

{% set payment_methods = ['credit_card','coupon','bank_transfer','gift_card'] %}

with payments as (
  select * from {{ ref('stg_payments') }}
),
final as (
  select
    order_id,
    {% for m in payment_methods -%}
    sum(case when payment_method = '{{ m }}' then amount else 0 end) as {{ m }}_amount,
    {% endfor -%}
    sum(amount) as total_amount
  from payments
  group by 1
)
select * from final
