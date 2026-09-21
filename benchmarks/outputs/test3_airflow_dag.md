# Test 3: Daily Airflow DAG

## Prompt
```
Create an Airflow DAG that:
1. Waits for a file to land in S3 (bucket: raw-data, prefix: daily/)
2. Triggers a dbt run for models tagged 'daily'
3. Runs data quality checks
4. Sends a Slack notification on failure
5. Runs daily at 2 AM UTC
```

## AI Output (Claude Artifacts 2.0)

Full output: see `examples/airflow/daily_data_pipeline.py`

Key decisions it made:
- `S3KeySensor` with `wildcard_match=True` and `bucket_key='daily/*.csv'`
- `TaskGroup` for dbt run + dbt test
- `schedule_interval='0 2 * * *'` (daily at 2 AM UTC)
- `on_failure_callback` using `SlackWebhookOperator`
- `catchup=False` (correct — prevents backfill storm)
- `retries=2` with 5-minute delay
- 1-hour timeout on sensor, 5-minute poke interval

## What it got right
- Correct sensor choice (S3KeySensor, not S3PrefixSensor)
- Wildcard matching for daily file pattern
- Tasks grouped logically
- Failure notification with context (task ID, DAG ID, log URL)
- Reasonable retry strategy
- `catchup=False` prevents the deploy-day backfill disaster

## What I had to fix
- Slack callback instantiates `SlackWebhookOperator` inside the callback — needs `.execute(context=context)` call (it had this, actually)
- Added TODO for configuring the `slack_webhook` Airflow connection
- Would add a success notification task at the end
- Would parameterize the dbt project path instead of hardcoding `/opt/dbt`

## What it missed
- No SLA/alerting on the overall DAG duration
- No idempotency guarantee if dbt run is re-triggered
- The sensor only matches `*.csv` — what about Parquet or JSON files?

## Time comparison
- AI generation: ~20 seconds
- Manual equivalent: ~45 minutes (mostly looking up the S3KeySensor API)
