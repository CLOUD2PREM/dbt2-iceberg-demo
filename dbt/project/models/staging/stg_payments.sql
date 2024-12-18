{{ config(
    materialized='table',
    partition_by=['payment_id']
) }}

with source as (
    select * from {{ ref('raw_payments') }}
),
payment as (

    select
        id as payment_id,
        order_id,
        payment_method,
        amount / 100 as amount
    from source
)
select * from payment
