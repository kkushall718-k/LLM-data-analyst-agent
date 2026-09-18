import pandas as pd
import psycopg
from sql_safety import validate_sql


def get_postgres_schema(settings):
    with psycopg.connect(
        **dict(settings),
        connect_timeout=5,
        options="-c statement_timeout=5000",
    ) as connection:
        connection.read_only = True

        cursor = connection.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s
              AND table_name = %s
            ORDER BY ordinal_position
            """,
            ("public", "sales"),
        )

        rows = cursor.fetchall()

    return pd.DataFrame(rows, columns=["column", "data_type"])


def run_postgres_query(settings, sql):
    is_valid, message = validate_sql(
        sql,
        table_name="sales",
        dialect="postgres",
    )

    if not is_valid:
        raise ValueError(message)

    with psycopg.connect(
        **dict(settings),
        connect_timeout=5,
        options="-c statement_timeout=5000 -c lock_timeout=2000",
    ) as connection:
        connection.read_only = True
        connection.execute("SET LOCAL search_path = pg_catalog, public")

        with connection.cursor(name="analyst_result") as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany(1001)
            columns = [column.name for column in cursor.description]

    result = pd.DataFrame(rows[:1000], columns=columns)
    truncated = len(rows) > 1000

    return result, truncated
