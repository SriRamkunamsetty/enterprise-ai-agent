# 🚀 Enterprise-AI-Agent
A fully cloud-native multi-agent analytics system built using **Google ADK** (Agent Development Kit), deployed on **Google Cloud Agent Engine**.

This project demonstrates all major components required for the Kaggle Agents Intensive Capstone:

## ✅ Features Implemented
- **Multi-Agent System**
  - Supervisor Agent
  - Planner Agent
  - Data Worker
  - Forecast Worker
  - Critic Agent
  - Reporter Agent

- **Tools**
  - MCP BigQuery Loader
  - Data Preprocessing Tool
  - Forecast ML Tool (Reflect & Retry)
  - Report Artifact Generator

- **Advanced Capstone Concepts**
  - Parallel/Sequential workflow support
  - Loop Agent behavior (critic refinement)
  - Long-running operations (resume enabled)
  - Sessions & State (Firestore)
  - Long-term Memory (GCS memory bank)
  - Context Compaction
  - Observability:
    - Cloud Logging
    - BigQuery Metrics
    - Tracing
  - A2A Multi-Agent Collaboration
  - Cloud Deployment via Agent Engine

---

## 📁 Project Structure

## License

This project is licensed under the  
**Creative Commons Attribution 4.0 International (CC BY 4.0)** license.

You are free to use, modify, and share this project with attribution.  
Full license text → https://creativecommons.org/licenses/by/4.0/
---

## 🚀 Run Locally (Cloud Shell)
```bash
export PATH=$PATH:~/.local/bin
pip install -r requirements.txt
python3 app.py
