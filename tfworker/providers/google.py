from .base import BaseProvider
from tfworker import constants as const


class GoogleProvider(BaseProvider):
    tag = "google"

    def __init__(self, body, authenticators, *args, **kwargs):
        super(GoogleProvider, self).__init__(body)

        self._authenticator = authenticators.get(self.tag)

        # if there is a creds file, tuck it into the provider vars
        if self._authenticator.creds_path:
            self.vars["credentials", f"file('{self._authenticator.creds_path}')"]
