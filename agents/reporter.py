import logging
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

class ReporterAgent(Agent):
    def __init__(self, name="reporter"):
        super().__init__(name=name)

    async def on_message(self, message, session):
        """
        Expected message: dict containing results from previous agents.

        This agent MUST return a JSON-serializable dict.
        """

        logger.info("ReporterAgent received final data")

        # Normalize message to avoid unhashable types
        safe_message = self._sanitize(message)

        return {
            "agent": "reporter",
            "summary": "Enterprise workflow completed successfully.",
            "data": safe_message
        }

    def _sanitize(self, obj):
        """
        Recursively sanitize data so it is fully JSON-serializable.
        Converts:
        - sets → lists
        - numpy types → python types
        - lists/dicts deep cleaning
        """

        if isinstance(obj, dict):
            new = {}
            for k, v in obj.items():
                # keys must be strings
                new[str(k)] = self._sanitize(v)
            return new

        elif isinstance(obj, list):
            return [self._sanitize(v) for v in obj]

        elif isinstance(obj, set):
            return [self._sanitize(v) for v in obj]

        elif hasattr(obj, "item"):  # numpy scalar
            return obj.item()

        return obj