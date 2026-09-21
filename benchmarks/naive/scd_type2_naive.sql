-- ❌ NAIVE VERSION — "SCD2" that's actually just an overwrite
--
-- Problems:
--   1. TRUNCATE + INSERT destroys all history — defeats the purpose of SCD2
--   2. No effective_from / effective_to tracking
--   3. No change detection — rewrites everything every run
--   4. No surrogate key — can't join to fact tables reliably
--   5. Not incremental — full table scan every run at scale

{{ config(materialized='table') }}

SELECT
    customer_id,
    name,
    email,
    tier,
    updated_at,
    CURRENT_TIMESTAMP() AS loaded_at
FROM {{ source('raw', 'customers') }}
