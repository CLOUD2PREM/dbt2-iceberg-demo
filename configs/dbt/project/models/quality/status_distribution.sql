{{ config(
  materialized = 'table',
  file_format = 'parquet',
  format_version = 2,
  partition_by = 'insert_date'
) }}


WITH status_distribution AS (
  SELECT 
    status,
    COUNT(*) as status_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as status_percentage,
    SUM(amount) as total_amount
  FROM {{ ref('fct_orders') }}
  GROUP BY status
)
SELECT 
  status,
  status_count,
  status_percentage,
  total_amount,
  CURRENT_TIMESTAMP AS insert_date,
  CASE 
    WHEN status_percentage > 90 THEN 'WARN: Single status dominance'
    WHEN status_count = 0 THEN 'FAIL: Missing status values'
    ELSE 'PASS'
  END as distribution_status
  FROM status_distribution
ORDER BY status_count DESC