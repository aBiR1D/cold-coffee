-- Incremental events model with deduplication and late-arriving data handling
--
-- Handles: deduplication via surrogate key, late data via 3-day lookback,
-- schema drift via on_schema_change='fail', partitioning by date.

{{
  config(
    materialized='incremental',
    unique_key=['user_id', 'event_type', 'timestamp'],
    on_schema_change='fail',
    partition_by={
      "field": "event_date",
      "data_type": "date",
      "granularity": "day"
    }
  )
}}

WITH source_data AS (
  SELECT 
    user_id,
    event_type,
    timestamp,
    DATE(timestamp) AS event_date,
    -- Generate surrogate key for deduplication
    {{ dbt_utils.generate_surrogate_key([
      'user_id', 
      'event_type', 
      'timestamp'
    ]) }} AS event_key
  FROM {{ source('raw', 'events') }}
  WHERE timestamp IS NOT NULL
),

deduplicated AS (
  SELECT * FROM (
    SELECT 
      *,
      ROW_NUMBER() OVER (
        PARTITION BY event_key 
        ORDER BY timestamp DESC
      ) AS row_num
    FROM source_data
  )
  WHERE row_num = 1
)

SELECT 
  user_id,
  event_type,
  timestamp,
  event_date,
  event_key
FROM deduplicated

{% if is_incremental() %}
WHERE event_date >= DATE_SUB(
  (SELECT MAX(event_date) FROM {{ this }}), 
  INTERVAL 3 DAY
)
{% endif %}
