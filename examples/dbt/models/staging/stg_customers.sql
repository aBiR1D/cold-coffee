-- Staging layer for raw customers
-- Isolates source schema from downstream models.
-- Column renames, type casts, and basic filtering happen here.

WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
)

SELECT
    customer_id,
    name                            AS customer_name,
    LOWER(TRIM(email))              AS email,
    LOWER(TRIM(tier))               AS tier,
    updated_at
FROM source
WHERE customer_id IS NOT NULL
