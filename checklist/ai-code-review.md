# AI-Generated Pipeline Code Review Checklist

Use this checklist before merging **any** AI-generated data pipeline code into production.

---

## Core Safety Checks

- [ ] **Idempotency** — Can this run multiple times without creating duplicates or side effects?
- [ ] **Schema evolution** — What happens when a column is added, removed, or renamed upstream?
- [ ] **Late-arriving data** — Is there a lookback window? Is it wide enough for your SLAs?
- [ ] **Deduplication** — Are there unique key constraints? What's the dedup strategy?
- [ ] **Error handling** — Does it fail loudly (with clear errors) or silently (with bad data)?

## Performance

- [ ] **Partitioning** — Is the model partitioned on the right column(s)?
- [ ] **Materialization** — Is the strategy appropriate? (table vs. view vs. incremental)
- [ ] **Query complexity** — Are there unnecessary subqueries or repeated scans?
- [ ] **Data volume** — Will this work at 10x current volume?

## Data Quality

- [ ] **Not-null tests** — Are key columns tested for nulls?
- [ ] **Uniqueness tests** — Are surrogate/natural keys tested for uniqueness?
- [ ] **Freshness tests** — Is source data freshness monitored?
- [ ] **Accepted values** — Are categorical columns validated?
- [ ] **Referential integrity** — Do foreign key relationships hold?

## Architecture

- [ ] **Dependencies** — Are upstream models referenced via `ref()` / `source()`, not hardcoded?
- [ ] **Naming conventions** — Does it follow your team's naming standards?
- [ ] **Documentation** — Are columns described in `schema.yml`?
- [ ] **Tags/labels** — Is the model properly tagged for selective runs?

## Security & Compliance

- [ ] **PII handling** — Is personally identifiable information masked/hashed where required?
- [ ] **Access control** — Does the model respect your data access policies?
- [ ] **Audit trail** — Are transformation timestamps and metadata captured?

## Operational

- [ ] **Monitoring** — Will you know if this breaks tomorrow?
- [ ] **Rollback plan** — Can you revert to the previous version quickly?
- [ ] **Runbook** — Is there documentation for on-call troubleshooting?

---

> **Rule of thumb:** If the AI generated it in 30 seconds, spend at least 5 minutes reviewing it.
> The time you save generating code should be reinvested in reviewing it.
