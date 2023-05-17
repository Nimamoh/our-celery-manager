from dataclasses import dataclass
from pydantic import BaseSettings

from urllib.parse import urlparse

@dataclass
class SettingsApiResponse:
    root_path: str
    application_name: str
    broker: str | None
    backend: str | None

class Settings(BaseSettings):

    """Le chemin prefixe de l'application"""
    root_path: str = "/"

    application_name: str = "Our celery manager"
    """L'adresse du broker"""
    broker: str
    """Le backend url à utiliser pour récupérer les résultats"""
    backend: str

    
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
