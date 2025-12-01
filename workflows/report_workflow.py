from google.adk.workflow import workflow, step


@workflow()
async def report_flow(ctx):
    """
    Sequential workflow for enterprise analytics:
    1) Load data from BigQuery
    2) Clean & preprocess
    3) Predict revenue
    4) Critic validation loop
    5) Report generation (HTML/PDF)
    """

    params = ctx.input.get("params", {})

    project = params.get("project")
    query = params.get("query")

    # Store these permanently in workflow state
    ctx.state["project"] = project
    ctx.state["query"] = query

    # ------------------------------
    # STEP 1 — Load data
    # ------------------------------
    loaded = await ctx.call_tool("load_table", {
        "project": project,
        "query": query
    })
    ctx.state["raw_rows"] = loaded["rows"]

    # ------------------------------
    # STEP 2 — Clean data
    # ------------------------------
    cleaned = await ctx.call_tool("clean_data", {
        "rows": ctx.state["raw_rows"]
    })
    series = cleaned.get("series", [])
    ctx.state["series"] = series

    # ------------------------------
    # STEP 3 — Predict revenue
    # ------------------------------
    preds = await ctx.call_tool("predict_revenue", {
        "series": ctx.state["series"]
    })
    ctx.state["predictions"] = preds["predictions"]

    # ------------------------------
    # STEP 4 — Critic validation loop
    # (Manual internal loop — 3 attempts max)
    # ------------------------------
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        attempts += 1

        # Call critic agent through A2A
        critic_message = {
            "action": "validate",
            "predictions": preds
        }

        critic_agent = ctx.agent.team.get_agent("CriticAgent")
        critic_result = await critic_agent.on_message(critic_message, ctx.session)

        if critic_result.get("action") == "accept":
            break

        if critic_result.get("action") == "refine":
            # Retry prediction
            preds = await ctx.call_tool("predict_revenue", {
                "series": ctx.state["series"]
            })
            ctx.state["predictions"] = preds["predictions"]

    # ------------------------------
    # STEP 5 — Build report (artifact)
    # ------------------------------
    html = f"""
    <html>
    <body>
        <h1>Enterprise AI Forecast Report</h1>
        <h2>Predictions</h2>
        <pre>{ctx.state["predictions"]}</pre>
        <h3>Source Query</h3>
        <pre>{query}</pre>
    </body>
    </html>
    """

    final_report = await ctx.call_tool("build_report", {
        "html": html,
        "filename": "enterprise_ai_report.pdf"
    })

    ctx.state["report_artifact"] = final_report

    # Return structured result
    return {
        "status": "success",
        "predictions": ctx.state["predictions"],
        "artifact": final_report
    }