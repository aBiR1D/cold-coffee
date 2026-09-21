-- Staging layer for raw events
-- This is the single place where source column names are mapped.
-- If the source renames a column, fix it HERE — downstream models don't change.

WITH source AS (
    SELECT * FROM {{ source('raw', 'events') }}
)

SELECT
    user_id,
    event_type,
    timestamp                       AS event_timestamp,
    DATE(timestamp)                 AS event_date
FROM source
WHERE user_id IS NOT NULL
  AND timestamp IS NOT NULL
