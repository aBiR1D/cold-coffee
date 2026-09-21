# Test 5: Schema Migration Impact Analysis

## Prompt
```
The source table `raw.users` is renaming `user_id` to `customer_id`.
I have 47 downstream dbt models. Generate a migration plan.
```

## AI Output (Claude Artifacts 2.0)

### Migration Plan: `user_id` → `customer_id` Column Rename

#### Phase 1: Impact Assessment (Day 1)

```bash
# Find every reference to user_id across the dbt project
grep -rn "user_id" models/ --include="*.sql" | grep -v "customer_id"

# Also check for variant naming
grep -rn "userid\|user_identifier\|uid" models/ --include="*.sql"

# Check schema.yml files for column definitions
grep -rn "user_id" models/ --include="*.yml"
```

Categorize results:
- **Direct references**: models that SELECT from `raw.users`
- **Indirect references**: models that reference the staging model
- **Test references**: schema tests on the `user_id` column

#### Phase 2: Isolate at the Staging Layer (Day 1-2)

The key insight: **don't touch 47 models. Touch ONE.**

```sql
-- models/staging/stg_users.sql (BEFORE)
SELECT
    user_id,
    ...
FROM {{ source('raw', 'users') }}

-- models/staging/stg_users.sql (AFTER)
SELECT
    customer_id AS user_id,  -- alias preserves downstream contract
    ...
FROM {{ source('raw', 'users') }}
```

This way, all 47 downstream models continue to reference `user_id` and nothing breaks.

#### Phase 3: Update Source Definition (Day 2)

```yaml
# schema.yml
sources:
  - name: raw
    tables:
      - name: users
        columns:
          - name: customer_id  # was: user_id
            description: "Primary key (renamed from user_id)"
```

#### Phase 4: Validate (Day 2-3)

```bash
# Run all models with no actual execution (compile only)
dbt compile --select stg_users+

# Run tests on the staging model
dbt test --select stg_users

# Full test suite
dbt test
```

Compare row counts before and after:
```sql
-- Validation query
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT user_id) AS unique_users
FROM {{ ref('stg_users') }}
```

#### Phase 5: Gradual Downstream Migration (Week 2-4, optional)

If you *want* to rename `user_id` to `customer_id` everywhere (not required):

1. Update models in dependency order (leaves → roots)
2. Run `dbt test` after each batch
3. Update documentation and schema.yml
4. Communicate the rename to downstream consumers

#### Phase 6: Rollback Plan

```sql
-- If anything breaks, revert stg_users.sql to:
SELECT
    customer_id AS user_id,  -- keep the alias
    ...
FROM {{ source('raw', 'users') }}
-- This buys you time while you fix the real issue
```

### Key Principles
1. **Isolate breaking changes at the staging layer** — this is why staging models exist
2. **Alias for backward compatibility** — downstream models shouldn't need to know about source renames
3. **Validate before deploying** — compile + test before any production run
4. **Communicate** — post in the data team channel before and after the migration
5. **Don't do a bulk search-swap across 47 files** — that's how you introduce typos at scale

## Scoring notes
- Correctly identified the staging layer isolation pattern
- Included grep/search commands for impact assessment
- Provided a rollback plan
- Explicitly warned against naive bulk-rename approach
- Phased approach with validation at each step

## What it missed
- No CI/CD considerations (how to test this in a PR before merging)
- No mention of downstream consumers outside dbt (dashboards, APIs, etc.)
- Didn't suggest a deprecation warning period for the old column name

## Time comparison
- AI generation: ~25 seconds for the full plan
- Manual equivalent: ~1 hour to write this up, plus the 11 PM debugging session from the blog's opening story
