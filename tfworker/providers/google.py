from .base import BaseProvider


class GoogleProvider(BaseProvider):
    tag = "google"

    def __init__(self, body, authenticators, *args, **kwargs):
        super(GoogleProvider, self).__init__(body)

        self._authenticator = authenticators.get(self.tag)

        # if there is a creds file, tuck it into the provider vars
        if self._authenticator.creds_path:
            self.vars["credentials"] = f'file("{self._authenticator.creds_path}")'

    def clean(self, deployment, limit, config):
        """Nothing to do here so far"""
        pass
