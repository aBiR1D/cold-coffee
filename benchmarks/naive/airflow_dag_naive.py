"""
❌ NAIVE VERSION — The Airflow DAG you get from a quick autocomplete

Problems:
  1. catchup=True (default) — triggers a massive backfill on first deploy
  2. depends_on_past=True — one failure blocks all future runs permanently
  3. No sensor timeout — waits forever if the file never arrives
  4. No error notification — failures are silent
  5. No task grouping — flat list of tasks
  6. No retries — one transient error kills the run
  7. Hardcoded paths with no parameterization
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime

with DAG(
    "daily_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 2 * * *",
    # catchup defaults to True — will backfill every day since 2024-01-01
) as dag:

    wait = S3KeySensor(
        task_id="wait_for_file",
        bucket_name="raw-data",
        bucket_key="daily/data.csv",
        # No timeout — waits forever
        # No wildcard — only matches exact filename
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command="dbt run",
        # No --select flag — runs ALL models, not just daily
        # No working directory
    )

    test_dbt = BashOperator(
        task_id="test_dbt",
        bash_command="dbt test",
    )

    wait >> run_dbt >> test_dbt
    # No failure notification
    # No success notification
    # No retry logic
