import os
import json
import snowflake.connector
from openai import OpenAI
from dotenv import load_dotenv

MODEL = "gpt-4o-mini"
# Change MODEL to select a different OpenAI model.

SAMPLE_N = 15
TOPICS = [
    "food quality",
    "delivery",
    "pricing",
    "service",
    "packaging",
    "other",
]
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = f"""
You classify customer reviews for a food delivery app.

For the review you are given, return:
- sentiment_label: positive, negative, or neutral
- sentiment_score: a number between -1.0 and 1.0
- topic: one of {TOPICS}
- key_issue: a short phrase (6 words or less) describing the main issue.
  Return null if there is no issue.

Reply as JSON in the exact format:
{{

    "sentiment_label": "<sentiment_label>",
    "sentiment_score": <sentiment_score>,
    "topic": "<topic>",
    "key_issue": "<key_issue>"
}}
"""


def get_connection():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def create_output_table(cursor):
    # conn = get_connection()
    # cursor = conn.cursor()
    cursor.execute(
        """
        CREATE SCHEMA IF NOT EXISTS ZOMATO.AI;

    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ZOMATO.AI.review_enriched (
            review_id STRING PRIMARY KEY,
            sentiment_label STRING,
            sentiment_score FLOAT,
            topic STRING,
            key_issue STRING,
            model STRING,
            enriched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        );
    """
    )
    # cursor.close()i
    # conn.close()


def get_reviews_to_enrich(cursor):
    # conn = get_connection()
    # cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT review_id, comment
        FROM ZOMATO.RAW.reviews
        WHERE review_id NOT IN (
            SELECT review_id FROM ZOMATO.AI.review_enriched
        )
        LIMIT {SAMPLE_N};
        """
    )
    reviews = cursor.fetchall()
    # cursor.close()
    # conn.close()
    return reviews


def classify_review(comment):
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment},
        ],
    )
    answer = response.choices[0].message.content
    print("Model - Answer", answer)
    return json.loads(answer)


def save_results(cursor, results):
    print(f"Saving {len(results)} enriched reviews to Snowflake...")
    cursor.executemany(
        """
        INSERT INTO ZOMATO.AI.REVIEW_ENRICHED
            (
                review_id,
                sentiment_label,
                sentiment_score,
                topic,
                key_issue,
                model
            )
        VALUES (%s, %s, %s, %s, %s, %s)

    """,
        results,
    )


def main():
    conn = get_connection()
    cursor = conn.cursor()

    create_output_table(cursor)
    reviews = get_reviews_to_enrich(cursor)

    if len(reviews) == 0:
        print("No new reviews to enrich.")
        return

    print(f"Enriching {len(reviews)} reviews...")

    results = []
    for review_id, comment in reviews:
        try:
            labels = classify_review(comment)
            results.append(
                (
                    review_id,
                    labels["sentiment_label"],
                    labels["sentiment_score"],
                    labels["topic"],
                    labels["key_issue"],
                    MODEL,
                )
            )
        except Exception as e:
            print(f"Error enriching review {review_id}: {e}")

    save_results(cursor, results)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
