{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2,
  partition_by = 'insert_date'
) }}


with row_count_check as (
  select
    count(*) as total_rows,
    count(distinct customer_id) as unique_customers,
    sum(case when amount is null then 1 else 0 end) as null_amounts,
    sum(case when order_date is null then 1 else 0 end) as null_dates
  from {{ ref('fct_orders') }}
)
  select
  total_rows,
  unique_customers,
  null_amounts,
  null_dates,
  current_timestamp as insert_date,
  case
    when total_rows = 0 then 'FAIL: No data found'
    when null_amounts > total_rows * 0.1 then 'WARN: High null amounts'
    when null_dates > 0 then 'FAIL: Null dates found'
    else 'PASS'
  end as validation_status
from row_count_check