import streamlit as st
import pandas as pd
import duckdb
from openai import OpenAI
from sql_safety import validate_sql


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("LLM Data Analyst Agent")

if st.button("Test AI connection"):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input="Reply with: Connection successful!",
            max_output_tokens=30,
        )
        st.success(response.output_text)
    except Exception as error:
        st.error(f"Connection failed: {type(error).__name__}")

st.write("Welcome! This app will help you explore your data.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.write("Column names and data types:")
    schema = pd.DataFrame({
        "column": df.columns,
        "data_type": df.dtypes.astype(str).values,
    })
    st.dataframe(schema)

    connection = duckdb.connect()
    connection.register("csv_input", df)

    connection.execute(
        "CREATE TABLE uploaded_data AS SELECT * FROM csv_input"
    )
    connection.unregister("csv_input")

    connection.execute("SET enable_external_access = false")
    connection.execute("SET memory_limit = '256MB'")
    connection.execute("SET threads = 2")
    connection.execute("SET lock_configuration = true")

    sql = """
        SELECT country, COUNT(*) AS total_rows
        FROM uploaded_data
        GROUP BY country
        ORDER BY total_rows DESC
    """

    is_valid, message = validate_sql(sql)

    if not is_valid:
        connection.close()
        st.error(message)
        st.stop()

    result = connection.execute(sql).df()
    connection.close()

    st.write("Example analysis: rows by country")
    st.code(sql, language="sql")
    st.dataframe(result)

    st.bar_chart(result.set_index("country")["total_rows"])

    st.write(
        "This chart compares the number of rows for each country. "
        "A taller bar means that country has more records "
        "in the uploaded data."
    )

    st.download_button(
        label="Download example result as CSV",
        data=result.to_csv(index=False),
        file_name="query_result.csv",
        mime="text/csv",
    )

    st.success("File uploaded successfully!")
    st.dataframe(df)
    st.write("Number of rows:", df.shape[0])
    st.write("Number of columns:", df.shape[1])

    question = st.text_input("Ask a question about your data")

    if st.button("Generate SQL", disabled=not question.strip()):
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                instructions=(
                    "Write one DuckDB SELECT query for the user's question. "
                    "Use only the uploaded_data table and supplied columns. "
                    "Only COUNT is currently supported as a function. "
                    "Use simple selections, counting, grouping and ordering. "
                    "Do not use joins, subqueries or filters yet. "
                    "Return SQL without markdown fences. "
                    "If the question is unclear, ask for clarification instead. "
                    "If it needs unsupported features, explain that limitation."
                ),
                input=(
                    "Column names and types:\n"
                    f"{schema.to_json(orient='records')}\n\n"
                    f"Question: {question}"
                ),
                max_output_tokens=300,
                store=False,
            )

            generated_sql = response.output_text.strip()

            st.write("AI-generated response:")
            st.code(generated_sql, language="sql")

            is_valid, message = validate_sql(generated_sql)

            if is_valid:
                with duckdb.connect() as ai_connection:
                    ai_connection.execute("SET memory_limit = '256MB'")
                    ai_connection.execute("SET threads = 2")

                    ai_connection.register("csv_input", df)
                    ai_connection.execute(
                        "CREATE TABLE uploaded_data AS SELECT * FROM csv_input"
                    )
                    ai_connection.unregister("csv_input")

                    ai_connection.execute("SET enable_external_access = false")
                    ai_connection.execute("SET lock_configuration = true")

                    cursor = ai_connection.execute(generated_sql)
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchmany(1001)

                    ai_result = pd.DataFrame(
                        rows[:1000],
                        columns=columns,
                    )

                st.success("Query completed.")
                st.write("Result for your question:")

                explanation = client.responses.create(
                    model="gpt-4.1-mini",
                    instructions=(
                        "Explain the query results in 2–3 simple sentences. "
                        "Use only facts supported by the supplied results. "
                        "Do not invent causes or assume rows are unique customers. "
                        "The preview may be incomplete; do not claim it represents "
                        "the entire result unless the completeness flag is true."
                    ),
                    input=(
                        f"Question: {question}\n"
                        f"SQL: {generated_sql}\n"
                        f"Complete result included: {len(rows) <= 20}\n"
                        f"Result preview:\n"
                        f"{ai_result.head(20).to_json(orient='records')}"
                    ),
                    max_output_tokens=200,
                    store=False,
                )

                st.write("Explanation:")
                st.write(explanation.output_text)

                st.dataframe(ai_result)

                st.download_button(
                    label="Download AI result as CSV",
                    data=ai_result.to_csv(index=False),
                    file_name="ai_query_result.csv",
                    mime="text/csv",
                    key="download_ai_result",
                    on_click="ignore",
                )

                if (
                    ai_result.shape[1] == 2
                    and pd.api.types.is_numeric_dtype(ai_result.iloc[:, 1])
                ):
                    st.bar_chart(
                        ai_result.set_index(ai_result.columns[0])
                    )

                if len(rows) > 1000:
                    st.warning("Showing only the first 1,000 result rows.")
            else:
                st.warning(message)

        except Exception as error:
            st.error(f"Request failed: {type(error).__name__}")
