import streamlit as st
import pandas as pd
import duckdb
from sql_safety import validate_sql

st.title("LLM Data Analyst Agent")
st.write("Welcome! This app will help you explore your data.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Column names and data types:")
    schema = pd.DataFrame({
        "column": df.columns,
        "data_type": df.dtypes.astype(str).values
    })
    st.dataframe(schema)
    connection = duckdb.connect()
    connection.register("uploaded_data", df)

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

    st.code(sql, language="sql")

    st.write("SQL query result:")
    st.dataframe(result)

    st.write("Number of rows by country")
    st.bar_chart(result.set_index("country")["total_rows"])

    st.write(
        "This chart compares the number of rows for each country. "
        "A taller bar means that country has more records in the uploaded data."
    )

    st.download_button(
        label="Download result as CSV",
        data=result.to_csv(index=False),
        file_name="query_result.csv",
        mime="text/csv"
    )

    st.success("File uploaded successfully!")
    st.dataframe(df)
    st.write("Number of rows:", df.shape[0])
    st.write("Number of columns:", df.shape[1])
    question = st.text_input("Ask a question about your data")

    if question:
        st.write("Your question:", question)
