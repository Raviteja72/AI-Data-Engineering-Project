from datetime import datetime
from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.bash import BashOperator

DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt/zomato_project"

COPY_RAW = [
    'USE WAREHOUSE "ZOMATO_WH"',
    """COPY INTO ZOMATO.RAW.restaurants
    FROM @ZOMATO_RAW_STAGE/restaurants
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.reviews
    FROM @ZOMATO_RAW_STAGE/reviews
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.users
    FROM @ZOMATO_RAW_STAGE/users
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.food
    FROM @ZOMATO_RAW_STAGE/food
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.orders
    FROM @ZOMATO_RAW_STAGE/orders
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.menu
    FROM @ZOMATO_RAW_STAGE/menu
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
    """COPY INTO ZOMATO.RAW.order_items
    FROM @ZOMATO_RAW_STAGE/order_items
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 1
    )
    ON_ERROR = 'CONTINUE'""",
]

with DAG(
    dag_id="zomato_batch",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["zomato", "batch"],
    doc_md=__doc__,
) as dag:

    reload_raw = SQLExecuteQueryOperator(
        task_id="reload_raw",
        conn_id="snowflake_default",
        sql=COPY_RAW,
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
