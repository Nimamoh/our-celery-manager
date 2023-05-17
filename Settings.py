from pydantic import BaseSettings

from urllib.parse import urlparse


class Settings(BaseSettings):
    application_name: str = "Our celery manager"
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
