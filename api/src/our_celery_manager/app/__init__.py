import logging
from pathlib import Path

from collections.abc import Sized, Iterable

logger = logging.getLogger(__name__)

def _content_of_version_or(def_value = "¯\_(ツ)_/¯"):
    try:
        version_path = Path(__file__).parent / "VERSION"
        with version_path.open() as f:
            return f.read().strip()
    except Exception as e:
        logger.warn(f"Could not read VERSION file: {e}. Version will be set to {def_value}")
        return def_value

def is_iterable_empty(t: Iterable):
    """Check if a tuple is empty. ie: has no values or all being None."""
    empty = True
    for e in t:
        empty = empty and \
            (e is None or \
             (isinstance(e, Sized) and len(e) == 0))
        if not empty:
            break
    return empty