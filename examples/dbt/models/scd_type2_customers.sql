-- Type 2 Slowly Changing Dimension for customer data
--
-- Tracks historical changes to customer tier and email.
-- Current records have effective_to = '9999-12-31'.
-- Handles both initial load and incremental runs.

{{
  config(
    materialized='incremental',
    unique_key='customer_surrogate_key',
    on_schema_change='fail'
  )
}}

WITH source_customers AS (
  SELECT
    customer_id,
    name,
    email,
    tier,
    updated_at
  FROM {{ source('raw', 'customers') }}
),

{% if is_incremental() %}

current_records AS (
  SELECT
    customer_id,
    email,
    tier,
    customer_surrogate_key
  FROM {{ this }}
  WHERE effective_to = '9999-12-31'
),

changed_records AS (
  SELECT
    src.customer_id,
    src.name,
    src.email,
    src.tier,
    src.updated_at
  FROM source_customers src
  INNER JOIN current_records cur
    ON src.customer_id = cur.customer_id
  WHERE src.email != cur.email
     OR src.tier != cur.tier
),

-- Expire old records (set effective_to to the change date)
expired AS (
  SELECT
    cur.customer_surrogate_key,
    cur.customer_id,
    existing.name,
    cur.email,
    cur.tier,
    existing.effective_from,
    changed.updated_at AS effective_to,
    FALSE AS is_current
  FROM current_records cur
  INNER JOIN changed_records changed
    ON cur.customer_id = changed.customer_id
  INNER JOIN {{ this }} existing
    ON cur.customer_surrogate_key = existing.customer_surrogate_key
),

-- New version of changed records
new_versions AS (
  SELECT
    {{ dbt_utils.generate_surrogate_key([
      'customer_id',
      'updated_at'
    ]) }} AS customer_surrogate_key,
    customer_id,
    name,
    email,
    tier,
    updated_at AS effective_from,
    CAST('9999-12-31' AS DATE) AS effective_to,
    TRUE AS is_current
  FROM changed_records
),

-- Brand new customers (not in target yet)
new_customers AS (
  SELECT
    {{ dbt_utils.generate_surrogate_key([
      'src.customer_id',
      'src.updated_at'
    ]) }} AS customer_surrogate_key,
    src.customer_id,
    src.name,
    src.email,
    src.tier,
    src.updated_at AS effective_from,
    CAST('9999-12-31' AS DATE) AS effective_to,
    TRUE AS is_current
  FROM source_customers src
  LEFT JOIN current_records cur
    ON src.customer_id = cur.customer_id
  WHERE cur.customer_id IS NULL
),

final AS (
  SELECT * FROM expired
  UNION ALL
  SELECT * FROM new_versions
  UNION ALL
  SELECT * FROM new_customers
)

{% else %}

-- Initial load: all records are current
final AS (
  SELECT
    {{ dbt_utils.generate_surrogate_key([
      'customer_id',
      'updated_at'
    ]) }} AS customer_surrogate_key,
    customer_id,
    name,
    email,
    tier,
    updated_at AS effective_from,
    CAST('9999-12-31' AS DATE) AS effective_to,
    TRUE AS is_current
  FROM source_customers
)

{% endif %}

SELECT
  customer_surrogate_key,
  customer_id,
  name,
  email,
  tier,
  effective_from,
  effective_to,
  is_current
FROM final
