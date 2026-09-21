"""
Daily Data Pipeline — Airflow DAG

This DAG:
1. Waits for a file to land in S3 (bucket: raw-data, prefix: daily/)
2. Triggers a dbt run for models tagged 'daily'
3. Runs data quality checks via dbt test
4. Sends a Slack notification on failure
5. Runs daily at 2 AM UTC

See inline TODOs for what to customize before production use.
"""

from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "daily_data_pipeline",
    default_args=default_args,
    description="Daily data ingestion and transformation",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["production", "daily"],
) as dag:

    wait_for_file = S3KeySensor(
        task_id="wait_for_s3_file",
        bucket_name="raw-data",
        bucket_key="daily/*.csv",
        wildcard_match=True,
        aws_conn_id="aws_default",
        timeout=3600,  # 1 hour timeout
        poke_interval=300,  # check every 5 minutes
    )

    with TaskGroup("dbt_tasks") as dbt_group:
        dbt_run = BashOperator(
            task_id="dbt_run_daily_models",
            bash_command="cd /opt/dbt && dbt run --select tag:daily",
        )

        dbt_test = BashOperator(
            task_id="dbt_test_daily_models",
            bash_command="cd /opt/dbt && dbt test --select tag:daily",
        )

        dbt_run >> dbt_test

    def send_failure_notification(context):
        """Callback to send Slack alert on task failure."""
        # TODO: Configure 'slack_webhook' connection in Airflow UI
        return SlackWebhookOperator(
            task_id="slack_failure",
            http_conn_id="slack_webhook",
            message=(
                f"❌ Pipeline Failed: {context['task_instance'].task_id}\n"
                f"DAG: {context['dag'].dag_id}\n"
                f"Execution Time: {context['execution_date']}\n"
                f"Log: {context['task_instance'].log_url}"
            ),
        ).execute(context=context)

    wait_for_file >> dbt_group

    # Attach failure callback to all tasks
    for task in dag.tasks:
        task.on_failure_callback = send_failure_notification
