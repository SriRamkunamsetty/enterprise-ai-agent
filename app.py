from google.adk.apps import App
from agents.supervisor import SupervisorAgent

def create_app():
    agent = SupervisorAgent()
    app = App(agent=agent, name="Enterprise-AI-Agent")
    return app

if __name__ == "__main__":
    app = create_app()
    app.serve()  # For local dev inside Cloud Shell