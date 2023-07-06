from dataclasses import dataclass
from pydantic import BaseSettings
from . import _content_of_version_or

from urllib.parse import urlparse

@dataclass
class SettingsApiResponse:
    application_name: str
    version: str
    broker: str | None
    backend: str | None

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

    
    def hiding_passwords(self):
        self.application_name = _hide_url_password(self.application_name)
        self.backend = _hide_url_password(self.backend)
        return self

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
