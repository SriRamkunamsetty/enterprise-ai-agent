import time
import json
import os
from google.adk.callbacks import Callback
from google.cloud import logging as gcloud_logging
from google.cloud import bigquery


class LoggingCallback(Callback):
    """
    Sends observability data to:
    - Google Cloud Logging
    - BigQuery (enterprise_analytics.agent_events)
    """

    def __init__(self):
        super().__init__()

        # Cloud Logging client
        self.log_client = gcloud_logging.Client()
        self.logger = self.log_client.logger("enterprise_ai_agent")

        # BigQuery client
        self.bq = bigquery.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))

    # When a tool starts
    async def on_tool_start(self, ctx, tool_name, args):
        ctx._tool_start_ts = time.time()

    # When a tool ends
    async def on_tool_end(self, ctx, tool_name, result):

        start_ts = getattr(ctx, "_tool_start_ts", None)
        duration_ms = int((time.time() - start_ts) * 1000) if start_ts else None

        # Build event entry
        entry = {
            "event_time": time.time(),
            "session_id": ctx.session.session_id if ctx.session else None,
            "agent": getattr(ctx, "agent_name", "unknown"),
            "event_type": "tool_call",
            "tool_name": tool_name,
            "duration_ms": duration_ms,
        }

        # ---- 1) Send to Cloud Logging ----
        self.logger.log_struct(entry)

        # ---- 2) Send to BigQuery ----
        try:
            table_id = f"{os.environ.get('GOOGLE_CLOUD_PROJECT')}.enterprise_analytics.agent_events"
            row = [{
                "event_time": entry["event_time"],
                "session_id": entry["session_id"],
                "agent": entry["agent"],
                "event_type": entry["event_type"],
                "details": json.dumps({
                    "tool": tool_name,
                    "duration_ms": duration_ms
                }),
                "duration_ms": duration_ms
            }]
            self.bq.insert_rows_json(table_id, row)
        except Exception as e:
            # Best effort logging; don't break agent execution
            self.logger.log_text(f"BigQuery insert failed: {e}", severity="WARNING")