Paste:

```bash
#!/bin/bash

# Replace with your Agent Engine endpoint after deployment
ENDPOINT="https://YOUR_AGENT_ENDPOINT/agent"

cat > payload.json <<EOF
{
  "input": {
    "task": "generate_report",
    "params": {
      "project": "enterprise-agent-478612",
      "query": "SELECT date, revenue FROM dataset.table LIMIT 50"
    }
  }
}
EOF

curl -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d @payload.json \
    | jq