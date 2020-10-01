from .base import BaseAuthenticator
from tfworker import constants as const


class GoogleAuthenticator(BaseAuthenticator):
    tag = "google"

    def __init__(self, state_args, **kwargs):
        super(GoogleAuthenticator, self).__init__(state_args, **kwargs)

        self.bucket = self._resolve_arg("backend_bucket")
        self.creds_path = self._resolve_arg("gcp_creds_path")
        self.deployment = self._resolve_arg("deployment")
        self.prefix = self._resolve_arg("backend_prefix")
        self.project = self._resolve_arg("gcp_project")
        self.region = self._resolve_arg("gcp_region")

        if self.prefix == const.DEFAULT_BACKEND_PREFIX:
            self.gcp_prefix = const.DEFAULT_BACKEND_PREFIX.format(
                deployment=self.deployment
            )
