# cold-coffee ☕

> *Because every data engineer knows the exact moment their coffee goes cold — it's when the pipeline breaks.*

A benchmark suite for AI-generated data pipelines. Contains production-grade examples, their naive counterparts, a scoring framework, and the raw test results from 40 hours of evaluation.

---

## Why This Exists

AI tools can now generate dbt models, Airflow DAGs, and migration plans. But **how good are they really?** This repo provides:

- **Side-by-side comparisons** — naive autocomplete output vs. production-grade output
- **A scoring framework** — reproducible tests with expected patterns and anti-patterns
- **Runnable examples** — a real dbt project you can clone and build
- **Benchmark data** — scored results so you can compare your own AI tool

---

## Project Structure

```
cold-coffee/
├── examples/                        # Production-grade code
│   ├── dbt/
│   │   ├── dbt_project.yml          # Runnable dbt project config
│   │   ├── packages.yml             # dbt_utils dependency
│   │   ├── profiles.yml             # Local dev profile (DuckDB)
│   │   ├── models/
│   │   │   ├── staging/
│   │   │   │   ├── stg_events.sql
│   │   │   │   └── stg_customers.sql
│   │   │   ├── incremental_events.sql
│   │   │   ├── scd_type2_customers.sql
│   │   │   └── schema_migration_example.sql
│   │   ├── tests/
│   │   │   └── test_no_overlapping_effective_dates.sql
│   │   └── schema.yml
│   └── airflow/
│       ├── daily_data_pipeline.py
│       └── requirements.txt
│
├── benchmarks/
│   ├── naive/                       # ❌ The "bad" outputs (for comparison)
│   │   ├── incremental_events_naive.sql
│   │   ├── scd_type2_naive.sql
│   │   └── airflow_dag_naive.py
│   ├── outputs/                     # Raw AI outputs for all 5 tests
│   │   ├── test1_incremental_events.md
│   │   ├── test2_scd_type2.md
│   │   ├── test3_airflow_dag.md
│   │   ├── test4_ambiguous_mau.md
│   │   └── test5_schema_migration.md
│   └── results/
│       └── benchmark_results.yml    # Scored results
│
├── runner/                          # Test scoring framework
│   ├── evaluate.py                  # CLI runner
│   └── scoring.py                   # Pattern matching + scoring engine
│
├── tests/
│   └── prompt_test_suite.yml        # 5 test definitions with patterns
│
└── checklist/
    └── ai-code-review.md            # Pre-merge review checklist
```

---

## Quick Start

### 1. Run the benchmark scorer

```bash
pip install -r requirements.txt

# Score all 5 test outputs
python -m runner.evaluate --all

# Score a single test
python -m runner.evaluate --test incremental_events_basic

# Score your own AI's output
python -m runner.evaluate --test scd_type2_customers --file my_output.sql

# Export results as YAML
python -m runner.evaluate --all --format yaml
```

### 2. Compare naive vs. production

Open any file in `benchmarks/naive/` alongside its counterpart in `examples/dbt/models/`:

| Naive | Production |
|---|---|
| `benchmarks/naive/incremental_events_naive.sql` | `examples/dbt/models/incremental_events.sql` |
| `benchmarks/naive/scd_type2_naive.sql` | `examples/dbt/models/scd_type2_customers.sql` |
| `benchmarks/naive/airflow_dag_naive.py` | `examples/airflow/daily_data_pipeline.py` |

Each naive file has inline comments explaining exactly what's wrong with it.

### 3. Run the dbt project locally

```bash
cd examples/dbt
pip install dbt-duckdb
dbt deps
dbt compile   # validates SQL without a warehouse
```

### 4. Use the review checklist

Before merging any AI-generated pipeline code:

```bash
cat checklist/ai-code-review.md
```

---

## Test Suite

5 tests across 3 categories, difficulty ★ to ★★★★★:

| # | Test | Category | Difficulty | What It Measures |
|---|---|---|---|---|
| 1 | Incremental Events | dbt | ★★☆☆☆ | Deduplication, lookback, schema handling |
| 2 | Type 2 SCD | dbt | ★★★★☆ | Change detection, history tracking, initial load |
| 3 | Airflow DAG | airflow | ★★★☆☆ | Sensor config, error handling, task structure |
| 4 | Ambiguous MAU | clarification | ★★★★★ | Does it ask questions or make assumptions? |
| 5 | Schema Migration | debugging | ★★★★☆ | Staging isolation, impact analysis, rollback |

Scoring: `+1` per expected pattern, `-2` per anti-pattern, `+3` bonus for asking clarifying questions on ambiguous prompts.

---

## Contributing

**Add a test case:** Edit `tests/prompt_test_suite.yml` with your prompt, expected patterns, and anti-patterns.

**Add a naive example:** Drop it in `benchmarks/naive/` with inline comments explaining the problems.

**Add benchmark results:** Run the same prompts against a different AI tool and PR your outputs to `benchmarks/outputs/`.

The worse the failure, the more useful it is.

---

## License

MIT
