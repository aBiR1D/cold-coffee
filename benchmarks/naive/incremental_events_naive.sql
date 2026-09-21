-- ❌ NAIVE VERSION — The kind of output you get from basic autocomplete
--
-- Problems:
--   1. No deduplication — duplicate events with the same timestamp both load
--   2. No lookback window — late-arriving data is silently dropped
--   3. No schema change handling — breaks silently if source changes
--   4. Race condition — concurrent runs can miss or double-count rows
--   5. SELECT * from subquery means schema drift propagates everywhere

{{ config(materialized='incremental') }}

SELECT 
    user_id,
    event_type,
    timestamp
FROM {{ source('raw', 'events') }}

{% if is_incremental() %}
WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})
{% endif %}
