# LLM Data Analyst Agent

A learning project that answers plain-English questions about CSV files
and a small PostgreSQL database using Python, Streamlit, and OpenAI.

## Features

- Upload and preview CSV data
- Connect to a configured PostgreSQL sales table
- Generate SQL from plain-English questions
- Display generated SQL for transparency
- Validate SQL before execution
- Ask for clarification when questions are unclear
- Show result tables, compatible bar charts, and AI explanations
- Download results as CSV
- Download PDF reports with SQL, explanations, and a result preview

## Supported analysis

- COUNT, SUM, AVG, MIN, and MAX
- Grouping and sorting
- DISTINCT and LIMIT

Filters, joins, and subqueries are not supported yet.

## Technology

- Python and Streamlit
- pandas and DuckDB
- PostgreSQL and Psycopg
- OpenAI API and Pydantic
- SQLGlot
- ReportLab

## Run locally

Create and activate a virtual environment on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` with your own settings:

```toml
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

[postgres]
host = "localhost"
port = 5432
dbname = "analyst_demo"
user = "analyst_reader"
password = "YOUR_DATABASE_PASSWORD"
```

Keep the OpenAI key above the `[postgres]` section.
Never commit this secrets file.

Start the app:

```bash
python -m streamlit run app.py
```

CSV mode requires an OpenAI API key.
PostgreSQL mode additionally requires a running database with a
`public.sales` table and a role granted SELECT access.

The demo sales table has these columns:
`id`, `country`, `product`, `quantity`, and `revenue`.

## Example questions

- How many rows are there for each country?
- What is the total revenue for each country?
- What is the average revenue per sales row for each country?
- Which country has the most rows?

## Data handling

Questions and column names/types are sent to OpenAI for SQL generation.
Up to 20 query-result rows are sent for the AI explanation.
API usage may incur charges.

## Safeguards and limitations

- SQL validation restricts statements, tables, functions, and syntax.
- DuckDB external access is disabled after loading the uploaded data.
- PostgreSQL queries use a restricted role and read-only transactions.
- PostgreSQL statement and lock timeouts are configured.
- Displayed results and CSV exports are limited to 1,000 rows.
- PDF table previews include up to 20 rows and 6 columns.
- PDFs currently contain text and a table preview, without the chart.
- Results are not yet preserved across all Streamlit reruns.
- AI-generated SQL and explanations can be incorrect.

This is a local learning prototype, not a production-ready service.
DuckDB execution still needs stronger isolation and execution time limits
before public deployment.

## Planned improvements

- Preserve results across app reruns
- Improve error messages
- Add automated SQL validation tests
- Add reproducible PostgreSQL setup instructions
- Support more query types
- Strengthen execution isolation before deployment