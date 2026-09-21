# Test 1: Incremental Events Model

## Prompt
```
Create an incremental dbt model for user events.
Source table: raw.events (user_id, event_type, timestamp)
```

## AI Output (Claude Artifacts 2.0)

```sql
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
```

## What it got right
- Deduplication via ROW_NUMBER + surrogate key
- 3-day lookback window for late-arriving data
- `on_schema_change='fail'` to catch breaking changes
- Partitioning by date for query performance
- Null filtering on timestamp

## What I had to fix
- Nothing critical — this was production-ready as-is
- I added a staging layer in front of it (`stg_events`) to isolate source schema

## Time comparison
- AI generation: ~15 seconds
- Manual equivalent: ~30 minutes (including the lookback logic I always forget)
