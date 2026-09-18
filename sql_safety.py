import sqlglot
from sqlglot import exp


def validate_sql(sql, table_name="uploaded_data", dialect="duckdb"):
    try:
        statements = sqlglot.parse(sql, read=dialect)
    except sqlglot.errors.ParseError:
        return False, "The SQL could not be understood."

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    query = statements[0]

    if not isinstance(query, exp.Select):
        return False, "Only SELECT queries are allowed."

    tables = list(query.find_all(exp.Table))

    if not tables:
        return False, f"The query must use {table_name}."

    for table in tables:
        if (
            table.name != table_name
            or table.db
            or table.catalog
        ):
            return False, f"Use only the unqualified table name {table_name}."

    for function in query.find_all(exp.Func):
        if not isinstance(function, exp.Count):
            return False, "Only the COUNT function is currently allowed."

    allowed_nodes = {
        exp.Select,
        exp.From,
        exp.Table,
        exp.Identifier,
        exp.Column,
        exp.Star,
        exp.Count,
        exp.Alias,
        exp.Group,
        exp.Order,
        exp.Ordered,
        exp.Limit,
        exp.Literal,
        exp.Distinct,
    }

    for node in query.walk():
        if type(node) not in allowed_nodes:
            return False, "This SQL structure is not supported yet."

    return True, "Initial SQL checks passed."
