# app/logging_config.py
import logging
import sys

def configure_logging(level: str = "INFO"):
    fmt = "[%(asctime)s] %(levelname)s %(name)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=level, format=fmt)
    # reduce verbosity of noisy libs
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)