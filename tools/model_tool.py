from google.adk.tools import mcp_tool
from google.adk.plugins import reflect_and_retry
import numpy as np


@reflect_and_retry(retries=2)
@mcp_tool(
    name="predict_revenue",
    description="Run a simple forecasting model on a time-series and return predictions.",
    input_schema={
        "type": "object",
        "properties": {
            "series": {"type": "array"}
        },
        "required": ["series"]
    },
    output_schema={
        "type": "object",
        "properties": {
            "predictions": {"type": "array"}
        }
    }
)
def predict_revenue(series):
    """
    Basic forecasting logic:
    - Converts input list to numpy array.
    - If empty → raises ValueError to trigger reflect/retry.
    - Uses simple heuristic model (last value + trending).
    - Returns 4-step forecast as example.

    You can upgrade this to use:
      - Vertex AI
      - ARIMA
      - Prophet
      - LSTM
    """

    # If no data → force reflect/retry
    if not series:
        raise ValueError("Input time-series is empty.")

    # Convert to numpy
    try:
        arr = np.array(series, dtype=float)
    except Exception:
        raise ValueError("Series contains non-numeric values.")

    # Not enough data?
    if len(arr) < 2:
        # Too little signal → retry
        raise ValueError("Too few points to forecast.")

    # Simple naive forecast: trend = last - second_last
    last = arr[-1]
    trend = arr[-1] - arr[-2]

    # Create forecast for next 4 periods
    preds = [
        float(last + trend * 1),
        float(last + trend * 2),
        float(last + trend * 3),
        float(last + trend * 4),
    ]

    # If predictions produce invalid values → trigger critic
    if any(np.isnan(preds)) or any(p < -1e9 for p in preds):
        raise ValueError("Invalid predictions generated.")

    return {"predictions": preds}