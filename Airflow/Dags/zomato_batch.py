from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.bash import BashOperator


DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt/zomato_project"
TEMPLATE_PATH = Path(__file__).parent

with DAG(
    dag_id="zomato_batch",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["zomato", "batch"],
    doc_md=__doc__,
    template_searchpath=[str(TEMPLATE_PATH)],
) as dag:

    reload_raw = SQLExecuteQueryOperator(
        task_id="reload_raw",
        conn_id="snowflake_default",
        sql="queries/reload_raw.sql",
        split_statements=True,
        autocommit=True,
    )

    dbt_build_core = BashOperator(
        task_id="dbt_build_core",
        bash_command=" ".join(
            (
                f"{DBT} build --project-dir {DBT_PROJECT}",
                f"--profiles-dir {DBT_PROJECT}",
            )
        ),
    )

    reload_raw >> dbt_build_core
