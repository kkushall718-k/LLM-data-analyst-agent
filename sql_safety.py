import sqlglot
from sqlglot import exp


def validate_sql(sql):
    try:
        statements = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError:
        return False, "The SQL could not be understood."

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    if not isinstance(statements[0], exp.Select):
        return False, "Only SELECT queries are allowed."

    tables = list(statements[0].find_all(exp.Table))

    for table in tables:
        if (
            table.name != "uploaded_data"
            or table.db
            or table.catalog
        ):
            return False, "Only the uploaded_data table is allowed."

    for function in statements[0].find_all(exp.Func):
        if not isinstance(function, exp.Count):
            return False, "Only the COUNT function is currently allowed."

    return True, "Initial checks passed."
