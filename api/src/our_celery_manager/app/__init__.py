import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def _content_of_version_or(def_value = "¯\_(ツ)_/¯"):
    try:
        version_path = Path(__file__).parent / "VERSION"
        with version_path.open() as f:
            return f.read().strip()
    except Exception as e:
        logger.warn(f"Could not read VERSION file: {e}. Version will be set to {def_value}")
        return def_value