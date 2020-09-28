from .base import BaseBackend


class GCSBackend(BaseBackend):
    tag = "gcs"
    auth_tag = "google"

    def __init__(self, authenticators, *args, **kwargs):
        self._authenticator = authenticators.get(self.auth_tag)
