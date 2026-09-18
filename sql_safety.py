import sqlglot
from sqlglot import exp


def validate_sql(sql):
    try:
        statements = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError:
        return False, "The SQL could not be understood."

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed."

    query = statements[0]

    if not isinstance(query, exp.Select):
        return False, "Only SELECT queries are allowed."

    tables = list(query.find_all(exp.Table))

    if not tables:
        return False, "The query must use uploaded_data."

    for table in tables:
        if (
            table.name != "uploaded_data"
            or table.db
            or table.catalog
        ):
            return False, "Only the uploaded_data table is allowed."

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

    return True, "Initial checks passed."
