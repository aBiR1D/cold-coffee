-- Custom test: Ensure no overlapping effective date ranges per customer
-- A customer should never have two "current" records at the same time.
--
-- This test returns rows that VIOLATE the constraint.
-- dbt expects 0 rows for a passing test.

WITH date_ranges AS (
  SELECT
    customer_id,
    effective_from,
    effective_to,
    LEAD(effective_from) OVER (
      PARTITION BY customer_id 
      ORDER BY effective_from
    ) AS next_effective_from
  FROM {{ ref('scd_type2_customers') }}
)

SELECT
  customer_id,
  effective_from,
  effective_to,
  next_effective_from
FROM date_ranges
WHERE next_effective_from IS NOT NULL
  AND effective_to > next_effective_from
