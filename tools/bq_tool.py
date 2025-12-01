from google.adk.tools import mcp_tool
from google.cloud import bigquery


@mcp_tool(
    name="load_table",
    description="Load rows from BigQuery via SQL query.",
    input_schema={
        "type": "object",
        "properties": {
            "project": {"type": "string"},
            "query": {"type": "string"},
            "timeout": {"type": "integer"}
        },
        "required": ["project", "query"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "rows": {"type": "array"}
        }
    }
)
def load_table(project: str, query: str, timeout: int = 300) -> dict:
    """
    Loads data from BigQuery using a SQL query.
    Used by DataWorkerAgent.
    """
    client = bigquery.Client(project=project)

    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(),
        timeout=timeout
    )

    rows = [dict(row) for row in job.result()]

    return {"rows": rows}