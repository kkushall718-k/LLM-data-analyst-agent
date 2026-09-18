# LLM Data Analyst Agent

A Python project I am building step by step to explore data using SQL and AI.

## Working features
- Upload and preview a CSV
- View row and column counts
- Run a predefined SQL query to count rows by country
- Display SQL, results, and a bar chart
- Download query results as CSV

## Current limitations
- The CSV must contain a country column.
- Questions are displayed but are not yet answered by AI.
- The chart explanation is predefined.

## Planned features
- Convert plain-English questions into validated SQL
- Ask for clarification when questions are unclear
- Generate explanations from query results
- Connect to PostgreSQL
- Export PDF reports

## Run locally
Install dependencies:
python -m pip install -r requirements.txt

Start the app:
python -m streamlit run app.py