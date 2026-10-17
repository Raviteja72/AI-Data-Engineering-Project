# Zomato AI Data Engineering End-to-End Project

This repository implements an end-to-end data engineering pipeline for Zomato-style restaurant and order data. It combines Apache Airflow for orchestration, Snowflake for cloud data warehousing, and dbt for transformation logic to turn raw operational data into analytics-ready tables.

## Overview

The project is designed to:

- Ingest raw restaurant, review, user, menu, order, and order-item data into Snowflake
- Orchestrate daily ELT jobs with Airflow
- Transform raw data into curated staging and mart models using dbt
- Build analytical views for revenue, customer behavior, restaurant performance, and delivery SLA monitoring
- Support AI-assisted enrichment workflows using OpenAI credentials configured in the pipeline environment

## Architecture

The solution follows a classic modern ELT pattern:

1. Raw CSV data is staged in Snowflake
2. Airflow runs the ingestion DAG on a schedule
3. dbt models clean and standardize the raw layer into staging tables
4. dbt marts produce analytics-friendly fact and dimension tables
5. Analysts and BI tools consume the final marts for reporting and dashboarding

## Tech Stack

- Python
- Apache Airflow
- Docker & Docker Compose
- Snowflake
- dbt
- SQL
- OpenAI API (optional enrichment/configured in environment)

## Repository Structure

```text
.
├── Airflow/
│   ├── Dags/
│   │   └── zomato_batch.py
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   ├── .env.example
│   └── .gitignore
├── logs/
├── README.md
├── zomato_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── analyses/
│   ├── macros/
│   ├── models/
│   │   ├── sources.yaml
│   │   ├── staging/
│   │   │   ├── staging.yaml
│   │   │   ├── stg_food.sql
│   │   │   ├── stg_menu.sql
│   │   │   ├── stg_order_items.sql
│   │   │   ├── stg_orders.sql
│   │   │   ├── stg_restaurants.sql
│   │   │   ├── stg_reviews.sql
│   │   │   └── stg_users.sql
│   │   └── marts/
│   │       ├── dim_customer.sql
│   │       ├── dim_date.sql
│   │       ├── dim_food.sql
│   │       ├── dim_restaurants.sql
│   │       ├── fct_order_items.sql
│   │       ├── fct_orders.sql
│   │       ├── mart_daily_city_revenue.sql
│   │       ├── mart_delivery_sla.sql
│   │       ├── mart_restaurant_performance.sql
│   │       └── marts.yaml
│   ├── seeds/
│   ├── snapshots/
│   └── tests/
└── .gitignore
```

## Data Sources

The raw layer is built around these Zomato-related entities:

- Restaurants
- Reviews
- Users
- Food items
- Orders
- Menu
- Order items

These are mapped in the dbt sources configuration under `zomato_project/models/sources.yaml` inside the `ZOMATO.RAW` Snowflake schema.

## Airflow Pipeline

The DAG file `Airflow/Dags/zomato_batch.py` orchestrates the pipeline:

- Uses a Snowflake connection configured via `AIRFLOW_CONN_SNOWFLAKE_DEFAULT`
- Runs `COPY INTO` statements into the raw schema for each table
- Executes a dbt build command after the raw load step

Main DAG details:

- DAG name: `zomato_batch`
- Schedule: daily (`@daily`)
- Trigger: Airflow task sequence
- Task flow:
  - `reload_raw` → loads raw data into Snowflake
  - `dbt_build_core` → runs the dbt project to create staging and marts

## GitHub Actions

Workflows are stored under `.github/workflows/`:

- `preview.yaml` runs Black, Flake8, Python compilation, and available pytest
  tests, parses the dbt project, and checks Snowflake SQL syntax when a pull
  request targeting `main` is opened or updated. These checks do not connect to
  Snowflake.
- `deploy.yaml` creates and uploads a deployment bundle after a pull request is
  merged into `main`. No deployment target is configured yet, so the artifact
  must be deployed manually.

To block merges when preview checks fail, configure the corresponding GitHub
Actions job as a required status check in the repository's branch protection rules.
GitHub is configured to automatically delete PR source branches after their PRs
are merged.

## dbt Project

The dbt project is configured in `zomato_project/dbt_project.yml`.

It contains:

- `staging` models materialized as views
- `marts` models materialized as tables
- central source definitions pointing to the Snowflake raw schema

### Staging Models

The staging layer includes cleaned source data for:

- `stg_restaurants.sql`
- `stg_orders.sql`
- `stg_reviews.sql`
- `stg_users.sql`
- `stg_food.sql`
- `stg_menu.sql`
- `stg_order_items.sql`

### Mart Models

The final analytical layer includes:

- `dim_customer.sql`
- `dim_date.sql`
- `dim_food.sql`
- `dim_restaurants.sql`
- `fct_orders.sql`
- `fct_order_items.sql`
- `mart_daily_city_revenue.sql`
- `mart_delivery_sla.sql`
- `mart_restaurant_performance.sql`

These support common questions such as:

- Which restaurants generate the most revenue?
- How does daily city revenue trend over time?
- What is the median or p90 delivery time?
- Which customers and orders contribute to sales volume?

## Environment Setup

1. Copy the sample environment file:

```bash
cp Airflow/.env.example Airflow/.env
```

2. Update the values in `Airflow/.env` with your Snowflake credentials and any needed OpenAI API key.

3. Start the Airflow stack:

```bash
cd Airflow
docker compose up -d
```

4. Open the Airflow UI:

```text
http://localhost:8080
```

Default login created in the config is:

- Username: `admin`
- Password: `admin`

## Local dbt Commands

From the project root:

```bash
dbt build --project-dir zomato_project --profiles-dir zomato_project
```

The project is also designed to be executed from the Airflow job using the configured dbt venv path.

## Project Goals

This project demonstrates a realistic end-to-end analytics engineering workflow for a food delivery business, including:

- Raw ingestion
- Data validation and staging
- Dimensional modeling
- Business reporting marts
- Automated orchestration
- Cloud warehouse integration

## Notes

- The project is configured to use the Snowflake warehouse `ZOMATO_WH` and schema `ZOMATO.RAW` in the Airflow DAG.
- The root `README.md` is intentionally minimal and the full project details live in the source folders and dbt model definitions.
- The setup is production-oriented and suitable for learning, experimentation, and extension to a broader reporting stack.

## Future Enhancements

Potential next steps for the project include:

- Adding data quality tests for each dbt model
- Integrating dashboards with a BI tool
- Expanding historical snapshots for trend analysis
- Incorporating real-time ingestion or event-based pipelines
- Adding AI-based sentiment analysis for review data

## License

This project is intended for learning and demonstration purposes unless otherwise specified in the repository.
