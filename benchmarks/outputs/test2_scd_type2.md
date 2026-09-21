# Test 2: Type 2 Slowly Changing Dimension

## Prompt
```
Create a dbt model that implements a Type 2 SCD for customer data.
Source table: raw.customers (customer_id, name, email, tier, updated_at)
Track changes to tier and email. Use effective_from/effective_to dates.
Current records should have effective_to = '9999-12-31'.
```

## AI Output (Claude Artifacts 2.0)

Generated a complete SCD2 implementation with:
- Staging CTE to pull source data
- Change detection via INNER JOIN comparing tracked columns
- Record expiration (setting effective_to on old versions)
- New version insertion with surrogate keys
- New customer handling (customers not yet in the target)
- Initial load path (non-incremental branch)
- `is_current` boolean flag

Full output: see `examples/dbt/models/scd_type2_customers.sql`

## What it got right
- Handles both initial load AND incremental correctly (the `{% if is_incremental() %}` branching)
- Generates surrogate keys via `dbt_utils.generate_surrogate_key`
- Expires old records by setting `effective_to` to the change timestamp
- New customers get `effective_to = '9999-12-31'`
- Change detection only on tracked columns (email, tier) — ignores name changes

## What I had to fix
- Added the custom test for overlapping effective dates (`test_no_overlapping_effective_dates.sql`)
- Added a staging model (`stg_customers`) with email normalization (LOWER/TRIM) to prevent false change detection from whitespace

## What it missed
- No handling for removed customers (soft-remove pattern)
- The `expired` CTE joins back to `{{ this }}` which could be slow at scale — might need a merge strategy instead

## Time comparison
- AI generation: ~30 seconds
- Manual equivalent: ~2 hours (this is the model I always copy-paste and debug for 45 minutes)
