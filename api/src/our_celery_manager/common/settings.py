import logging
from pathlib import Path
from dataclasses import dataclass
from pydantic_settings import BaseSettings

from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def _content_of_version_or(def_value = "¯\_(ツ)_/¯"):
    try:
        version_path = Path(__file__).parent / "VERSION"
        with version_path.open() as f:
            return f.read().strip()
    except Exception as e:
        logger.warn(f"Could not read VERSION file: {e}. Version will be set to {def_value}")
        return def_value

class Settings(BaseSettings):

    root_path: str = "/"
    """Prefix path of the application"""

    application_name: str = "Our celery manager"
    """Name of the app"""

    version: str = _content_of_version_or()
    """Version of the app"""

    broker: str
    """The broker url to send tasks to"""

    backend: str
    """The backend url to retrieve task results"""

    debug: bool = False
    """Debug mode which control some things like printing SQL requests."""
    
    def hiding_passwords(self):
        _settings = Settings()
        _settings.application_name = _hide_url_password(_settings.application_name)
        _settings.backend = _hide_url_password(_settings.backend)
        _settings.broker = _hide_url_password(_settings.broker)
        return _settings
    
    def db_connstring(self):
        """Deduce db connection string from backend string (remove prefixed db+ and options after ?)"""
        prefix = 'db+'
        if not self.backend.startswith(prefix):
            raise ValueError(f"result backend must be in form {prefix}")
        connstr = self.backend.removeprefix(prefix)
        return connstr

def _hide_url_password(s):
    if not isinstance(s, str):
        return s
    try:
        url = urlparse(s)
    except Exception:
        # Si l'entrée n'est pas une url, on passe
        return s
    if url.password is not None:
        return s.replace(url.password, '****')
    else:
        return s


@dataclass
class SettingsApiResponse:
    application_name: str
    version: str
    broker: str | None
    backend: str | None

    @staticmethod
    def from_settings(settings: Settings):
        return SettingsApiResponse(
            application_name=settings.application_name,
            version=settings.version,
            broker=settings.broker,
            backend=settings.backend,
        )

settings = Settings() # type: ignore