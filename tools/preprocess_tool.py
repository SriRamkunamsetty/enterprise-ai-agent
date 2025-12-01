from google.adk.tools import mcp_tool
import pandas as pd
import numpy as np


@mcp_tool(
    name="clean_data",
    description="Clean raw BigQuery rows and prepare a time-series array for forecasting.",
    input_schema={
        "type": "object",
        "properties": {
            "rows": {"type": "array"}
        },
        "required": ["rows"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "series": {"type": "array"}
        }
    }
)
def clean_data(rows):
    """
    Convert raw SQL rows → Pandas DF → clean → extract 'revenue' column.
    You can modify column names depending on your dataset.
    """
    if not rows:
        return {"series": []}

    df = pd.DataFrame(rows)

    # Expecting at least "date" + "revenue"
    if "date" not in df.columns or "revenue" not in df.columns:
        # Return empty to trigger refinement by CriticAgent
        return {"series": []}

    # Convert date column, sort chronologically
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    # Replace missing revenue with 0
    df["revenue"] = df["revenue"].fillna(0)

    # Make sure dtype is numeric
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    # Time-series array (pure numbers)
    series = df["revenue"].astype(float).tolist()

    return {"series": series}