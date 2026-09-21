-- Schema migration pattern: isolate a source column rename at the staging layer
--
-- Scenario: raw.users renamed `user_id` to `customer_id`.
-- Instead of updating 47 downstream models, alias it at the staging layer.
-- Downstream models continue to reference `user_id` and nothing breaks.

-- STEP 1: Update the staging model (this is the ONLY file that changes)

-- models/staging/stg_users.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'users') }}
)

SELECT
    -- Alias the renamed column to preserve the downstream contract
    customer_id                     AS user_id,
    username,
    email,
    created_at,
    updated_at
FROM source


-- STEP 2: Downstream models don't change at all.
-- This model still references `user_id` and works fine:
--
--   SELECT
--       u.user_id,
--       COUNT(*) AS event_count
--   FROM {{ ref('stg_users') }} u
--   JOIN {{ ref('stg_events') }} e ON u.user_id = e.user_id
--   GROUP BY u.user_id
--
-- The alias in stg_users absorbs the breaking change.
